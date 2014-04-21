## JRA-55 download

Data can be obtained from [JRA](http://jra.kishou.go.jp/JRA-55/index_en.html) or collaborative organizations:
* DIAS: [Data Integration & Analysis System](http://dias-dmg.tkl.iis.u-tokyo.ac.jp/dmm/doc/JRA-55-DIAS-en.html)
* NCAR: National Center for Atmospheric Research (USA):
  * [Daily 3-Hourly and 6-Hourly Data](http://rda.ucar.edu/datasets/ds628.0/)
  * [Monthly Means and Variances](http://rda.ucar.edu/datasets/ds628.1/)

## Paper acknowledgement
From [here](http://jra.kishou.go.jp/comm/application_en.html): The dataset used for this study is provided from the Japanese 55-year Reanalysis (JRA-55) project carried out by the Japan Meteorological Agency (JMA)

## Initial processing

The DIAS download gives you a c-shell script to execute (just type csh at the command line
followed by the filename) which runs a series of wget scripts to download the data. To merge all
those individual files I did the following:

```
years=`seq 1958 1 2012`

# Merge data into a file for each year
for var in ugrd vgrd; do
    for year in ${years}; do
        cdo mergetime anl_p125.*${var}.${year}*.irving65861.nc anl_p125.${var}.${year}_3hourly.nc
    done
done

# Remove the time stamp variable
echo 'o' > answer.txt
for var in ugrd vgrd; do
    for year in ${years}; do
        ncks -x -v initial_time0_encoded anl_p125.${var}.${year}_3hourly.nc anl_p125.${var}.${year}_3hourly.nc < answer.txt
    done
done 

# Calculate the daily mean and merge into one file
for var in ugrd vgrd; do
    for year in ${years}; do
        cdo daymean anl_p125.${var}.${year}_3hourly.nc anl_p125.${var}.${year}_daily.nc
    done
done

cdo mergetime anl_p125.ugrd.*_daily.nc anl_p125.ugrd.1958-2012_daily.nc
cdo mergetime anl_p125.vgrd.*_daily.nc anl_p125.vgrd.1958-2012_daily.nc

```
