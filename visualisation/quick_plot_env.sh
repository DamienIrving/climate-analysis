year=$1
month=$2
day1=$3

day2=`expr $day1 + 1`
day2=0$day2
day2=${day2: -2}

/usr/local/uvcdat/1.3.0/bin/cdat ~/phd/visualisation/plot_envelope.py /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw3/env-w19-va_ERAInterim_500hPa_030day-runmean_native.nc va daily --contour /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zg_ERAInterim_500hPa_030day-runmean_native-zonal-anom.nc zg --timescale 030day-runmean --projection spstere --raphael --ofile /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw3/figures/maps/env/030day-runmean/va/env-w19-va_ERAInterim_500hPa_030day-runmean_native_2011-07-14.png --time ${year}-${month}-${day1} ${year}-${month}-${day2} none

display /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw3/figures/maps/env/030day-runmean/va/env-w19-va_ERAInterim_500hPa_030day-runmean_native_${year}-${month}-${day1}.png &
