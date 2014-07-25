# Timescale analysis

The overall aim is to reproduce the images I showed in a previous meeting with Ian, for 3-years of individual
days for a running mean of 1, 5, 30, 90, 180 days. Those images had three panels:
- A map of the wave envelope with zonal streamfunction anomaly over the top (/visualisation/plot_envelope.py)
- One map of the power spectrum and the other of each component of the Fourier Transform (/testing/plot_hilbert.py)

Notes:
- I should extract the wave for w2-10
- Pull out 5 years of data to foucs on the centre 3 (i.e. for the 180 day overlap)
- How can I pull out the phase information for each of the Fourier components? (I could
  show that the others are random but when a large zonal extent is on, wave 1 and 3 stay 
  in the same location)


## Wave envelope map

### Calculate the running mean (for va; all times)
cdo runmean,30 /mnt/meteo0/data/simmonds/dbirving/Merra/data/va_Merra_250hPa_daily_native.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_native.nc
ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_native.nc

### Put on a regular grid
cdo remapcon2,r360x181 /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_native.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_r360x181.nc
ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_r360x181.nc

### Extract the wave envelope (w2-10)
bash ~/phd/data_processing/calc_fourier_transform.sh    /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_r360x181.nc va /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181.nc --filter 2 4 --outtype hilbert

### Calculate the wave statistics (for the extent - perhaps I don't need this...) 
cdo mermax -sellonlatbox,0,360,-70,-40 /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S.nc
ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S.nc
/usr/local/uvcdat/1.3.0/bin/cdat ~/phd/data_processing/calc_wave_stats.py /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S.nc env 7 /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/zw3-stats_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7.csv 
~/phd/data_processing/calc_zonal_anomaly.sh /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean_native.nc sf /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc
ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc
/usr/local/uvcdat/1.3.0/bin/cdat ~/phd/visualisation/plot_envelope.py /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181.nc env 30day-runmean --extent /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/zw3-stats_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7.csv -70 -40 --contour /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc sf --time 2001-01-01 2003-12-31 none --projection spstere --ofile /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/figures/env-w234-va_Merra_250hPa_30day-runmean_r360x181_2003-12-31.png


