#
# Description: For global daily data, calc_wind_quantities.py can only handle a few years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 ufile uvar vfile vvar outfile quantity"
    echo "   quantity:   Name of quantity to calculate"
    echo "   ufile:      Input zonal wind file name"
    echo "   uvar:       Input zonal wind variable name"
    echo "   vfile:      Input zonal wind file name"
    echo "   vvar:       Input zonal wind variable name"
    echo "   outfile:    Output file name"
    echo "   e.g. bash $0 streamfunction ua_Merra_250hPa_daily_native.nc ua va_Merra_250hPa_daily_native.nc va sf_Merra_250hPa_daily_native.nc"
    exit 1
}

nargs=6

if [ $# -ne $nargs ] ; then
  usage
fi

quantity=$1
ufile=$2
uvar=$3
vfile=$4
vvar=$5
outfile=$6
temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp

if [ ! -f $ufile ] ; then
    echo "Input U file doesn't exist: " $ufile
    usage
fi

if [ ! -f $vfile ] ; then
    echo "Input V file doesn't exist: " $vfile
    usage
fi

years=(1979 1982 1985 1988 1991 1994 1997 2000 2003 2006 2009 2012)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 2`
    temp_file=${temp_dir}/temp-${quantity}_${year}-${end}.nc
    /usr/local/uvcdat/1.3.0/bin/cdat ~/phd/data_processing/calc_wind_quantities.py ${quantity} $ufile $uvar $vfile $vvar ${temp_file} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo -O mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
ncatted -O -a axis,time,c,c,T $outfile


