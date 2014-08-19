#!/bin/bash

# Steps required before using this script:
# 1. Download the 6 hourly data from http://apps.ecmwf.int/datasets/data/interim_full_daily/?levtype=pl,
# 2. Use "ncpdq -P upk in.nc out.nc" to unpack the data 
#    (removes add_offset and scale_factor according to unpacked = add_offset + (packed_val * scale_factor))
# 3. Merge all the files into one using cdo mergetime  
#

function usage {
    echo "USAGE: bash $0 infile invar outfile outvar"
    echo "   infile:      Input file name"
    echo "   invar:       Input variable name"
    echo "   outfile:     Output file name"
    echo "   outvar:      Output variable name"
    echo "   e.g. bash $0 zfile.nc z new-zgfile.nc zg"
    exit 1
}

nargs=4
if [[ $# -ne $nargs ]] ; then
  usage
fi

infile=$1
invar=$2
outfile=$3
outvar=$4

cdo sellonlatbox,0,359.9,-90,90  -divc,9.80665 -daymean ${infile} ${outfile}   # Divude by standard gravity to go from geopotential to geopotential height
ncrename -O -v ${invar},${outvar} ${outfile}
ncatted -O -a units,${outvar},m,c,"m" ${outfile}
ncatted -O -a standard_name,${outvar},m,c,"geopotential height" ${outfile}
ncatted -O -a long_name,${outvar},m,c,"geopotential height at 500hPa" ${outfile}
ncatted -O -a axis,time,c,c,T ${outfile}
