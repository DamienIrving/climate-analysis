#
# Description: For global daily data, calc_envelope.py can only handle 5 years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

nargs=6
function usage {
    echo "USAGE: bash $0 infile invar outfile lonopt lonstart lonend"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   outfile:    Output file name"
    echo "   lonopt:     Type --longitude so compatable with makefile"
    echo "   latstart:   Start longitude search"
    echo "   lonstart:   Start longitude for new grid"
    echo "   e.g. bash $0 vrot_Merra_250hPa_daily-anom-wrt-all_y181x360-np20N260E.nc vrot env-w567-vrot_Merra_250hPa_daily-anom-wrt-all_y181x360-np20N260E.nc  --longitude 225 335 "
    exit 1
}

if [ $nargs -ne $# ] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3

lonstart=$5
lonend=$6
temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp

if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi


years=(1979 1984 1989 1994 1999 2004 2009)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 5`
    end_label=`expr $year + 4`
    temp_file=${temp_dir}/temp-env_${year}-${end_label}.nc
    echo /usr/local/uvcdat/1.2.0rc1/bin/cdat ~/phd/data_processing/calc_envelope.py $infile $invar $outfile --longitude $lonstart $lonend --time ${year}-01-01 ${end}-01-01 none
    temp_files+=(${temp_file})
done

echo cdo mergetime ${temp_files[@]} $outfile
echo rm ${temp_files[@]}
