#
# Description: For global daily data, calc_vwind_rotation.py can only handle 5 years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

nargs=15
function usage {
    echo "USAGE: bash $0 ufile uvar vfile vvar outfile npopt nplat nplon gridopt latstart nlat latstep lonstart nlon lonstep"
    echo "   ufile:     Input zonal wind file"
    echo "   uvar:      Input zonal wind variable"
    echo "   vfile:     Input meridional wind file"
    echo "   vvar:      Input zonal wind variable"
    echo "   outfile:   Output file name"
    echo "   npopt:     Type --north_pole so compatable with makefile"
    echo "   nplat:     Latitude of north pole"
    echo "   nplat:     Longitude of north pole"
    echo "   gridopt:   Type --grid so compatable with makefile"
    echo "   latstart:  Start latitude for new grid"
    echo "   nlat:      Number of latitude points"
    echo "   latstep:   Size of latitude step"
    echo "   lonstart:  Start longitude for new grid"
    echo "   nlon:      Number of longitude points"
    echo "   lonstep:   Size of latitude step"
    echo "   e.g. bash $0 ua_Merra_250hPa_daily_native.nc ua va_Merra_250hPa_daily_native.nc va vrot_Merra_250hPa_daily_y181x360-np20N260E.nc --north_pole 20 260 --grid -90.0 181 1.0 0.0 360 1.0"
    exit 1
}

if [ $nargs -ne $# ] ; then
  usage
fi

ufile=$1 
uvar=$2
vfile=$3
vvar=$4 
outfile=$5 

nplat=$7 
nplon=$8 

latstart=${10} 
nlat=${11} 
latstep=${12} 
lonstart=${13} 
nlon=${14} 
lonstep=${15}
temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp

if [ ! -f $ufile ] ; then
    echo "Zonal wind file doesn't exist: " $ufile
    usage
fi

if [ ! -f $vfile ] ; then
    echo "Meridional wind file doesn't exist: " $vfile
    usage
fi


years=(1979 1984 1989 1994 1999 2004 2009)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 4`
    temp_file=${temp_dir}/temp-vrot_${year}-${end}.nc
    /usr/local/uvcdat/1.3.0/bin/cdat ~/phd/data_processing/calc_vwind_rotation.py $ufile $uvar $vfile $vvar ${temp_file} --north_pole $nplat $nplon --grid $latstart $nlat $latstep $lonstart $nlon $lonstep --time ${year}-01-01 ${end}-12-31 none
    temp_files+=(${temp_file})
done

cdo mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
ncatted -O -a axis,time,c,c,T $outfile
