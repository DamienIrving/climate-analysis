#!/bin/bash
#
# Description: Run fix_salinity_units.py over a bunch of files
#             

function usage {
    echo "USAGE: bash $0 infiles"
    echo "   infiles:      Input file names"
    exit 1
}

infiles=($@)

for infile in "${infiles[@]}"; do

    outfile=`echo ${infile} | sed s:ua6:r87/dbi599:`
    python ~/climate-analysis/data_processing/fix_salinity_units.py ${infile} ${outfile}

done


 
