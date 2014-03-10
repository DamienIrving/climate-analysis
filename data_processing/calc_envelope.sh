#
# Description: For global daily data, calc_envelope.py can only handle 5 years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 infile invar outfile wavestart waveend lonopt lonstart lonend"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   outfile:    Output file name"
    echo "   waveopt:    Type --wavenumbers so compatable with makefile"
    echo "   wavestart:  Beginning of wavenumber range"
    echo "   waveend:    End of wavenumber range"
    echo "   lonopt:     Type --longitude so compatable with makefile"
    echo "   latstart:   Start longitude search"
    echo "   lonstart:   Start longitude for new grid"
    echo "   (the longitude selection is optional)"
    echo "   e.g. bash $0 vrot_Merra_250hPa_daily-anom-wrt-all_y181x360-np20N260E.nc vrot env-w567-vrot_Merra_250hPa_daily-anom-wrt-all_y181x360-np20N260E.nc --wavenumbers 5 7 --longitude 225 335 "
    echo "   e.g. bash $0 va_Merra_250hPa_daily-anom-wrt-all_y181x360.nc va env-w234-va_Merra_250hPa_daily-anom-wrt-all_y181x360.nc --wavenumbers 2 4"
    exit 1
}

narg_min=6
narg_max=9

if [[ $# -ne $narg_min && $# -ne $narg_max ]] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3
waveselect=($4 $5 $6)
temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp

if [ $# == $narg_max ] ; then
  lonselect=($7 $8 $9) 
else
  lonselect=""
fi  
  

if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi


years=(1979 1984 1989 1994 1999 2004 2009)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 4`
    temp_file=${temp_dir}/temp-env_${year}-${end}.nc
    /usr/local/uvcdat/1.3.0/bin/cdat ~/phd/data_processing/calc_envelope.py $infile $invar ${temp_file} ${waveselect[@]} ${lonselect[@]} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
ncatted -O -a axis,time,c,c,T $outfile
