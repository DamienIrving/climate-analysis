#
# Description: For global daily data, calc_zonal_anomaly.py can only handle 5 years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 infile invar outfile python_exe code_dir temp_dir"
    echo "   infile:      Input file name"
    echo "   invar:       Input variable name"
    echo "   outfile:     Output file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    echo "   temp_dir:    Directory to store temporary data files"
    echo "   e.g. bash $0 sf.nc sf sf-zonal-anom.nc /usr/local/anaconda/bin/python ~/climate-analysis/data_processing /mnt/meteo0/data/simmonds/dbirving/temp"
    exit 1
}

nargs=6

if [ $# -ne $nargs ] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3
python_exe=$4
code_dir=$5
temp_dir=$6
  
if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi

years=(1979 1984 1989 1994 1999 2004 2009 2014)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 4`
    temp_file=${temp_dir}/temp-zonal-anom_${year}-${end}.nc
    ${python_exe} ${code_dir}/calc_zonal_anomaly.py $infile $invar ${temp_file} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo -O mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
