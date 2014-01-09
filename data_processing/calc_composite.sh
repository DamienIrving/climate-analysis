#!/bin/bash

data_path=/mnt/meteo0/data/simmonds/dbirving/Merra/data/processed
base=hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates-filter

for var in sf ; do
    for region in marie-byrd-land antarctic-peninsula ; do
        for season in DJF MAM JJA SON ; do
    
            if [ "${var}" = "sf" ]; then
                infile=${data_path}/sf_Merra_250hPa_daily-anom-wrt-all_native.nc
            elif [ "${var}" -eq "tas" ]; then
	        infile=${data_path}/tas_Merra_surface_daily-anom-wrt-1979-2012_native.nc
            fi
    
            /usr/local/uvcdat/1.3.0/bin/cdat calc_composite.py ${infile} ${var} ${data_path}/stats/${base}-${region}-northerly-va.txt ${data_path}/stats/${var}-${base}-${region}-northerly-va_composite-${season}.nc --time 1979-01-01 2012-12-31 ${season}

        done
    done
done



