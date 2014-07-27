# Timescale analysis

The overall aim is to reproduce the images I showed in a previous meeting with Ian, for 3-years of individual
days for a running mean of 1, 5, 30, 90, 180 days. Those images had three panels:

- A map of the wave envelope with zonal streamfunction anomaly over the top (/visualisation/plot_envelope.py)
- One map of the power spectrum and the other of each component of the Fourier Transform (/testing/plot_hilbert.py)

Notes:

- I should extract the wave for w2-10
- Pull out 5 years of data to foucs on the centre 3 (i.e. for the 180 day overlap)
- How can I pull out the phase information for each of the Fourier components? (I could show that the others are random but when a large zonal extent is on, wave 1 and 3 stay in the same location)


## Wave envelope map

### 1. Extract the wave envelope
#### a. Calculate the running mean (for va; for a limited time range)
    $ cdo runmean,30 /mnt/meteo0/data/simmonds/dbirving/Merra/data/va_Merra_250hPa_daily_native.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_native.nc
    $ ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_native.nc

#### b. Put on a regular grid
    $ cdo remapcon2,r360x181 /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_native.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_r360x181.nc
    $ ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_r360x181.nc

#### c. Extract the wave envelope (w2-10)
    $ bash ~/phd/data_processing/calc_fourier_transform.sh    /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_30day-runmean_r360x181.nc va /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181.nc --filter 2 4 --outtype hilbert

### 2. Calculate the zonal streamfunction anomaly (for a limited time range)
#### a. Calculate the zonal anomaly (all times)
    $ ~/phd/data_processing/calc_zonal_anomaly.sh /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean_native.nc sf /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc
    $ ncatted -O -a axis,time,c,c,T /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc

#### b. Calculate the running mean (for a limited time range)


### 3. Generate the plot
    $ /usr/local/uvcdat/1.3.0/bin/cdat ~/phd/visualisation/plot_envelope.py /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181.nc env 30day-runmean --contour /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/sf_Merra_250hPa_30day-runmean-zonal-anom_native.nc sf --time 2001-01-01 2003-12-31 none --projection spstere --ofile /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/figures/env-w234-va_Merra_250hPa_30day-runmean_r360x181_2003-12-31.png


