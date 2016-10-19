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

    echo ${infile} 
    outfile=`echo ${infile} | sed s:ua6:r87/dbi599:`
    /g/data/r87/dbi599/miniconda2/envs/default/bin/python ~/climate-analysis/data_processing/fix_salinity_units.py ${infile} ${outfile}

done


 
