#
# Description: For global daily data, calc_zonal_anomaly.py can only handle 5 years of data at a time
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 infile invar outfile cdofix"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   outfile:    Output file name"
    echo "   cdofix:      Script for replacing attributes that cdo strips"
    echo "   e.g. bash $0 sf.nc sf sf-zonal-anom.nc ~/phd/data_processing/cdo_fix.sh"
    exit 1
}

nargs=4

if [ $# -ne $nargs ] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3
cdofix=$4

temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp
  
if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi

years=(1979 1984 1989 1994 1999 2004 2009 2014)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 4`
    temp_file=${temp_dir}/temp-zonal-anom_${year}-${end}.nc
    /usr/local/anaconda/bin/python ~/phd/data_processing/calc_zonal_anomaly.py $infile $invar ${temp_file} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo -O mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
bash ${cdofix} ${outfile} ${invar}      # Put back the required attributes that CDO strips