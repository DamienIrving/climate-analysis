path=/mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/stats
region=marie-byrd-land
file=hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates-filter-${region}-va-below-neg5_composite
proj=nsper

/usr/local/uvcdat/1.2.0/bin/cdat plot_composite.py tas ${path}/tas-${file}-DJF.nc ${path}/tas-${file}-MAM.nc ${path}/tas-${file}-JJA.nc ${path}/tas-${file}-SON.nc --headings DJF MAM JJA SON --ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0 --contour_var sf --contour_files ${path}/sf-${file}-DJF.nc ${path}/sf-${file}-MAM.nc ${path}/sf-${file}-JJA.nc ${path}/sf-${file}-SON.nc --contour_ticks -30 -25 -20 -15 -10 -5 0 5 10 15 20 25 30 --projection ${proj} --ofile /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/figures/tas-sf-${file}-mean_${proj}.eps --dimensions 2 2

