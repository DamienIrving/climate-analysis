#!/bin/bash


function usage {
    echo "USAGE: bash $0 infile invar outfile outvar"
    echo "   infile:      Input file name"
    echo "   invar:       Input variable name"
    echo "   outfile:     Output file name"
    echo "   outvar:      Output variable name"
    echo "   e.g. bash $0 vfile.nc VGRD_GDS0_ISBL new-vfile.nc va"
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

cdo invertlat ${infile} ${outfile}
ncrename -O -d g0_lat_1,latitude ${outfile}
ncrename -O -v g0_lat_1,latitude ${outfile}
ncrename -O -d g0_lon_2,longitude ${outfile}
ncrename -O -v g0_lon_2,longitude ${outfile}
ncrename -O -v ${invar},${outvar} ${outfile}
ncatted -O -a axis,time,c,c,T ${outfile}
