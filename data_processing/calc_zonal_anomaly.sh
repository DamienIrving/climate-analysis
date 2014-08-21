#
# Description: For global daily data, calc_zonal_anomaly.py can only handle 5 years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 infile invar outfile"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   outfile:    Output file name"
    echo "   e.g. bash $0 sf_Merra_250hPa_30day-runmean_native.nc sf sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3
temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp
  
  
if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi


years=(1979 1984 1989 1994 1999 2004 2009 2014)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 4`
    temp_file=${temp_dir}/temp-zonal_anom_${year}-${end}.nc
    /usr/local/uvcdat/1.3.0/bin/cdat ~/phd/data_processing/calc_zonal_anomaly.py $infile $invar ${temp_file} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
ncatted -O -a axis,time,c,c,T $outfile
