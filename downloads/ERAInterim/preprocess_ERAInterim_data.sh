#!/bin/bash

# Steps required before using this script:
# 1. Download the 6 hourly data from http://apps.ecmwf.int/datasets/data/interim_full_daily/?levtype=pl in 5 year chunks,
# 2. Use "ncpdq -P upk in.nc out.nc" to unpack the data 
#    (removes add_offset and scale_factor according to unpacked = add_offset + (packed_val * scale_factor))
# 3. Merge all the files into one using cdo mergetime  
#

function usage {
    echo "USAGE: bash $0 infile invar outfile outvar cdofix"
    echo "   infile:      Input file name"
    echo "   invar:       Input variable name"
    echo "   outfile:     Output file name"
    echo "   outvar:      Output variable name"
    echo "   cdofix:      Script for replacing attributes that cdo strips"
    echo "   e.g. bash $0 zfile.nc z new-zgfile.nc zg ~/phd/data_processing/cdo_fix.sh"
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
cdofix=$5

if [[ "${outvar}" = "zg" ]] ; then
    cdo invertlat -sellonlatbox,0,359.9,-90,90  -divc,9.80665 -daymean ${infile} ${outfile}   # Divude by standard gravity to go from geopotential to geopotential height
elif [[ "${outvar}" = "pr" ]] ; then
    cdo invertlat -sellonlatbox,0,359.9,-90,90 -mulc,1000 -daysum -shifttime,-12hour ${infile} ${outfile}  # Get the daily rainfall totals
else
    cdo invertlat -sellonlatbox,0,359.9,-90,90 -daymean ${infile} ${outfile} 
fi

bash ${cdofix} ${outfile} ${invar}            # Put back the required attributes that CDO strips
ncrename -O -v ${invar},${outvar} ${outfile}
ncatted -O -a axis,time,c,c,T ${outfile}
ncatted -O -a calendar,global,d,, ${outfile}  # Iris does not like this

if [[ "${outvar}" = "zg" ]] ; then
    ncatted -O -a units,${outvar},o,c,"m" ${outfile}
    ncatted -O -a standard_name,${outvar},o,c,"geopotential_height" ${outfile}
    ncatted -O -a long_name,${outvar},o,c,"geopotential_height" ${outfile}
    ncatted -O -a level,${outvar},o,c,"500hPa" ${outfile}
elif [[ "${outvar}" = "tas" ]] ; then
    ncatted -O -a standard_name,${outvar},o,c,"surface_air_temperature" ${outfile}
    ncatted -O -a long_name,${outvar},o,c,"surface_air_temperature" ${outfile}
    ncatted -O -a level,${outvar},o,c,"2m" ${outfile}
elif [[ "${outvar}" = "pr" ]] ; then
    ncatted -O -a standard_name,${outvar},o,c,"precipitation" ${outfile}
    ncatted -O -a long_name,${outvar},o,c,"precipitation" ${outfile}
    ncatted -O -a units,${outvar},o,c,"mm/day" ${outfile}
elif [[ "${outvar}" = "va" ]] ; then
    ncatted -O -a standard_name,${outvar},o,c,"northward_wind" ${outfile}
    ncatted -O -a long_name,${outvar},o,c,"northward_wind" ${outfile}
    ncatted -O -a level,${outvar},o,c,"500hPa" ${outfile}
elif [[ "${outvar}" = "va" ]] ; then
    ncatted -O -a standard_name,${outvar},o,c,"eastward_wind" ${outfile}
    ncatted -O -a long_name,${outvar},o,c,"eastward_wind" ${outfile}
    ncatted -O -a level,${outvar},o,c,"500hPa" ${outfile}
elif [[ "${outvar}" = "sic" ]] ; then
    ncatted -O -a standard_name,${outvar},o,c,"sea_ice_fraction" ${outfile}
    ncatted -O -a long_name,${outvar},o,c,"sea_ice_fraction" ${outfile}
fi
