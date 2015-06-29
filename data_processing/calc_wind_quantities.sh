#
# Description: For global daily data, calc_wind_quantities.py can only handle a few years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 quantity ufile uvar vfile vvar outfile python_exe code_dir temp_dir"
    echo "   quantity:    Name of quantity to calculate"
    echo "   ufile:       Input zonal wind file name"
    echo "   uvar:        Input zonal wind variable name"
    echo "   vfile:       Input zonal wind file name"
    echo "   vvar:        Input zonal wind variable name"
    echo "   outfile:     Output file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that calc_wind_quantities.py is in"
    echo "   temp_dir:    Directory to store temporary data files"
    echo "   e.g. bash $0 streamfunction ua_Merra_250hPa_daily_native.nc ua va_Merra_250hPa_daily_native.nc va sf_Merra_250hPa_daily_native.nc /usr/local/uvcdat/1.3.0/bin/python ~/climate-analysis/data_processing /mnt/meteo0/data/simmonds/dbirving/temp"
    exit 1
}

nargs=9

if [ $# -ne $nargs ] ; then
  usage
fi

quantity=$1
ufile=$2
uvar=$3
vfile=$4
vvar=$5
outfile=$6
python_exe=$7
code_dir=$8
temp_dir=$9

if [ ! -f $ufile ] ; then
    echo "Input U file doesn't exist: " $ufile
    usage
fi

if [ ! -f $vfile ] ; then
    echo "Input V file doesn't exist: " $vfile
    usage
fi

if [ ${quantity} == 'streamfunction' ] ; then
    outvar=sf
else
    echo "Unknown quantity: ${quantity}"
    exit 1
fi


years=(1979 1982 1985 1988 1991 1994 1997 2000 2003 2006 2009 2012)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 2`
    temp_file=${temp_dir}/temp-${quantity}_${year}-${end}.nc
    ${python_exe} ${code_dir}/calc_wind_quantities.py ${quantity} $ufile $uvar $vfile $vvar ${temp_file} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo -O mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}



