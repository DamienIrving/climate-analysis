#
# Description: For global daily data, calc_vrot.py can only handle a few years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 nplat nplon ufile ulong vfile vlong outfile python_exe code_dir temp_dir"
    echo "   nplat:       Latitude of north pole"
    echo "   nplon:       Longitude of north pole"
    echo "   ufile:       Input zonal wind file name"
    echo "   ulong:       Input zonal wind variable long name (e.g. eastward_wind)"
    echo "   vfile:       Input zonal wind file name"
    echo "   vlong:       Input zonal wind variable long name (e.g. northward_wind)"
    echo "   outfile:     Output file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that calc_vrot.py is in"
    echo "   temp_dir:    Directory to store temporary data files"
    echo "   e.g. bash $0 20 260 ua_Merra_250hPa_daily_native.nc ua va_Merra_250hPa_daily_native.nc va vrot_Merra_250hPa_daily_native-np20N260E.nc /usr/local/anaconda/bin/python ~/climate-analysis/data_processing /mnt/meteo0/data/simmonds/dbirving/temp"
    exit 1
}

nargs=10

if [ $# -ne $nargs ] ; then
  usage
fi

nplat=$1
nplon=$2
ufile=$3
ulong=$4
vfile=$5
vlong=$6
outfile=$7
python_exe=$8
code_dir=$9
temp_dir=${10}

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
    temp_file=${temp_dir}/temp-vrot_${year}-${end}.nc
    ${python_exe} ${code_dir}/calc_vrot.py $ufile $ulong $vfile $vlong ${temp_file} \
    --time ${year}-01-01 ${end}-12-31 --north_pole ${nplat} ${nplon} 
    temp_files+=(${temp_file})
done

cdo -O mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}

