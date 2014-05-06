#!/bin/bash

function usage {
    echo "USAGE: bash $0 infile invar dates outfile timescale"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   dates:      List of dates to be included in the composite"
    echo "   outfile:    Output file name (ends with DJF.nc or whatever, which will be replaced with correct timescale)"
    echo "   timescale:  Can be monthly or seasonal"
    echo "   e.g. bash $0 "
    exit 1
}

nargs=5

if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
invar=$2
dates=$3
outfile=$4
timescale=$5

if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi

if [ "${timescale}" = "seasonal" ]; then
    times="DJF MAM JJA SON"
elif [ "${timescale}" = "monthly" ]; then
    times="JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC"
else
    echo "Timescale not recognised"
    exit 1
fi

for time in ${times} ; do
    regex=s/[a-zA-Z]{3}.nc/${time}.nc/g
    new_outfile=`echo ${outfile} | sed -r ${regex}`
    echo /usr/local/uvcdat/1.3.0/bin/cdat calc_composite.py ${infile} ${var} ${dates} ${new_outfile} --time 1979-01-01 2014-12-31 ${time}
done



