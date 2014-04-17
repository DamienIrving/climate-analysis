years=`seq 1958 1 2012`

## Merge data into a file for each year
#for var in ugrd vgrd; do
#    for year in ${years}; do
#        cdo mergetime anl_p125.*${var}.${year}*.irving65861.nc anl_p125.${var}.${year}_3hourly.nc
#    done
#done

## Remove the time stamp variable
#echo 'o' > answer.txt
#for var in ugrd vgrd; do
#    for year in ${years}; do
#        ncks -x -v initial_time0_encoded anl_p125.${var}.${year}_3hourly.nc anl_p125.${var}.${year}_3hourly.nc < answer.txt
#    done
#done 

## Calculate the daily mean and merge into one file
#for var in ugrd vgrd; do
#    for year in ${years}; do
#        cdo daymean anl_p125.${var}.${year}_3hourly.nc anl_p125.${var}.${year}_daily.nc
#    done
#done

cdo mergetime anl_p125.ugrd.*_daily.nc anl_p125.ugrd.1958-2012_daily.nc
cdo mergetime anl_p125.vgrd.*_daily.nc anl_p125.vgrd.1958-2012_daily.nc
