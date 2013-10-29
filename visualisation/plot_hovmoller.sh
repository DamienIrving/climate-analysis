#!/bin/bash

declare -a months=(none January February March April May June July August September October November December)

for year in 1980 1981 1982 1983 1984 ; do
    for month in 01 02 03 04 05 06 07 08 09 10 11 12 ; do
    
        next_month=$(( $(( 10#${month} )) + 1 ))
        next_year=${year}
        if [ ${next_month} -eq 13 ]; then
            next_month=01
            next_year=$(( ${year} + 1 ))
        fi

        python plot_hovmoller.py \
        ~/Downloads/Data/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270_absolute14_lon195-340.nc \
        envelope DAILY \
        --time_bounds ${year}-${month}-01 ${next_year}-${next_month}-01 \
        --units ms-1 --title ${months[$(( 10#${month} ))]}_${year} \
        --ofile hovmoller_${year}_${month}.png

    done
done
