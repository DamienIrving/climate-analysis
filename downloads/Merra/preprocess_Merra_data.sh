#
# Description:  
#

function usage {
    echo "USAGE: bash $0 infile invar outfile outvar units"
    echo "   infile:      Input file name"
    echo "   invar:       Input variable name"
    echo "   outfile:     Output file name"
    echo "   outvar:      Output variable name"
    echo "   units:       Variable units"
    echo "   e.g. bash $0 ufile.nc u250 new-ufile.nc ua ms-1"
    exit 1
}

nargs=5
if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3
outvar=$4
units=$5

cdo chname,${invar},${outvar} ${infile} temp.nc
cdo sellonlatbox,0,359.9,-90,90 temp.nc ${outfile}
ncatted -O -a comments,${outvar},d,, ${outfile}
ncatted -O -a units,${ourvar},c,c,"${units}" ${outfile}
ncatted -O -a axis,time,c,c,T ${outfile}
rm temp.nc

