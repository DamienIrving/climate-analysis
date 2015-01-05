#!/bin/bash

function usage {
    echo "USAGE: bash $0 infile invar missval"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   missval:    Missing value"
    echo "   e.g. bash $0 -32767"
    exit 1
}

nargs=3

if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
invar=$2
missval=$3

# CDO strips a bunch of variable attributes that other programs need.
# This script puts them back

# NCO and CDAT need missing_value
# (see http://stderr.org/doc/nco/html/Missing-Values.html)
ncatted -O -a missing_value,${invar},o,c,${missval} ${infile}  

# My netcdf_io module needs axis=T
ncatted -O -a axis,time,c,c,T ${infile}  