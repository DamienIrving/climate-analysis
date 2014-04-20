function usage {
    echo "USAGE: bash $0 var"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   e.g. bash $0  "
}

nargs=1

if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
invar=$2
  
if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi



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

#cdo mergetime anl_p125.ugrd.*_daily.nc anl_p125.ugrd.1958-2012_daily.nc
#cdo mergetime anl_p125.vgrd.*_daily.nc anl_p125.vgrd.1958-2012_daily.nc

cdo chname,g0_lon_2,longitude
cdo chname,g0_lat_1,latitude
cdo chname,VGRD_GDS0_ISBL,va
cdo sellonlatbox,0,359.9,-90,90   # Check if this is needed
ncatted -O -a axis,time,c,c,T
