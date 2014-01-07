#!/bin/bash

data_path=/mnt/meteo0/data/simmonds/dbirving/Merra/data/processed
tas_file=${data_path}/tas_Merra_surface_daily-anom-wrt-1979-2012_native.nc
start=${data_path}/stats/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates-filter


for region in antarctic-peninsula marie-byrd-land ; do
    for season in DJF MAM JJA SON ; do
    
        /usr/local/uvcdat/1.3.0/bin/cdat calc_composite.py ${tas_file} tas ${start}-${region}-northerly-va.txt ${start}-${region}-northerly-va_composite-${season}.nc --time 1979-01-01 2012-12-31 ${season}
        echo ${region} ${season}

    done
done
