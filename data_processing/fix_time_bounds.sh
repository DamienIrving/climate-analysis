#!/bin/bash
#
# Description: fix_time_bounds.py cannot write over the input file.
#             

function usage {
    echo "USAGE: bash $0 infile python_exe code_dir"
    echo "   infile:      Input file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that fix_time_bounds.py is in"
    exit 1
}

nargs=3

if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
python_exe=$2
code_dir=$3
tmpfile=`echo ${infile} | sed s/.nc/_temp.nc/`


cp ${infile} ${tmpfile}
${python_exe} ${code_dir}/fix_time_bounds.py ${tmpfile} ${infile}

rm ${tmpfile}
 
