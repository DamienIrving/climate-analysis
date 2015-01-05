#!/bin/bash
#
# Description: CDO strips a bunch of variable attributes that other programs need.
#              This script puts them back.

function usage {
    echo "USAGE: bash $0 infile invar"
    echo "   infile:     Input file name"
    echo "   invar:      Input variable name"
    echo "   e.g. bash $0 in.nc var"
    exit 1
}

nargs=2

if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
invar=$2

# Check what the missing value is

missval=$(ncdump -h ${infile} | grep -E -i  "${invar}:_FillValue" | cut -f 2 -d '=' | cut -f 1 -d ';')
if [ -z "${missval}" ]; then
  echo "did not successfully extract the missing value" 
  exit 1
fi
missval=`echo ${missval}`  # Trim whitespace from front of variable

# NCO and CDAT need missing_value
# (e.g. see http://stderr.org/doc/nco/html/Missing-Values.html)

ncatted -O -a missing_value,${invar},o,c,${missval} ${infile}  

# My netcdf_io module needs axis=T

ncatted -O -a axis,time,c,c,T ${infile}  
