#!/bin/bash

# Steps required before using this script:
# 1. Download wget scripts from http://disc.sci.gsfc.nasa.gov/daac-bin/DataHoldings.pl
#    (some of these are saved in this repo)

# Fields I selected:
#  - Daily data: IAU 2d atmospheric single-level diagnostics (tavg1_2d_slv_Nx)
#  - Monthly data: Monthly IAU 2d atmospheric single-level diagnostics (tavgM_2d_slv_Nx)

# Download the data
for script in $*
do
    wget --content-disposition -i $script
done

# Merge all the individual files into one
for year in {1979..2013}
do
    cdo mergetime *.${year}????.* MERRA.prod.assim.tavg1_2d_slv_Nx.${year}.SUB.nc
    rm *.${year}[01]???.*
done
