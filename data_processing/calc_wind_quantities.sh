#!/bin/bash

for year in {1979..1983} ; do

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_wind_quantities.py absolutevorticitygradient \
/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_daily_native.nc ua \
/work/dbirving/datasets/Merra/data/va_Merra_250hPa_daily_native.nc va \
/work/dbirving/test_data/avrtgrad_Merra_250hPa_daily${year}_native.nc \
--time ${year}-01-01 $(( $year + 1 ))-01-01 \
--grid -90.0 73 2.5 0.0 144 2.5

done

