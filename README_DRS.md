# Data Reference Syntax

## Directory syntax

* `~/<dataset>/downloads`: A temporary dumping ground for downloaded files.  
* `~/<dataset>/data`: For data files I want to keep and use. To move from downloads to data
they must have undergone pre-processing 

## Standard variable abbreviations

* `zg`: Geopotential height
* `psl`: Sea level pressure
* `sf`: Streamfunction
* `ua`: Eastward wind velocity
* `va`: Northward wind velocity
* `vrot`: Northward wind velocity on a rotated sphere (i.e. the north pole has been shifted and the meridional wind re-calculated accordingly) 


## File name syntax

### Basic data files 

`<var>_<dataset>_<level>_<time>_<spatial>.nc`  

Sub-categories:  

* `<time>`: `<tscale>-<aggregation>-<season>`
* `<spatial>`: `<grid>-<region>`

Region names are defined in `netcdf_io.py` and the grid is either `native` or
something like `y181x360`, which desribes the number of latitude (181) and 
longitude (360) points (in this case it is a 1 by 1 degree horizontal grid.

Examples include:  
`psl_Merra_surface_daily_y181x360.nc`  
`eof-sf_Merra_250hPa_monthly-anom-wrt-1979-2011-JJA_native-sh.nc`  

### Files generated specifically for Rossby wave identification

The files in `~/<dataset>/data/processsed/rwid/` go all the way from simple wave extraction, 
to hovmoller diagrams, and filtered composites.  

`<var>_<dataset>_<level>_<time>_<spatial>_<searchbounds>_<clip>_<filter>.nc`

Sub-categories:  

* `<time>`: `<tscale>-<aggregation>-<season>-<composite>`
* `<spatial>`: `<grid>-<region>-<northpole>-<hovmoller>`

It is important to note that the details of the north pole location go in the `<spatial>` field
if the data are actually on a rotated grid, otherwise it needs to go in the `<hovmoller>` field (i.e. if 
the data are back on a regular lat/lon grid with the north pole at 90N).  

Examples:  
`vrot_Merra_250hPa_daily_anom-wrt-all_y181x360-np20N260E.nc` #calc_vwind_rotation  
`env-w567-vrot_Merra_250hPa_daily_anom-wrt-all_y181x360-np20N260E.nc` #calc_envelope  
`env-w567-vrot_Merra_250hPa_daily-anom-wrt-all_y181x360-np20N260E-hov_lon225E335E-lat10S10N_absolute14.nc` #calc_hovmoller
`psa-dates_Merra_250hPa_daily-anom-wrt-all_y181x360-np20N260E-hov-env-w567-vrot_lon225E335E-lat10S10N_absolute14.csv` #run_roim
#filter_dates
`tas_Merra_250hPa_daily-anom-wrt-all-SON-composite-mean_y181x360-np20N260E-hov-env-w567-vrot_lon225E335E-lat10S10N_absolute14_mariebyrdland-va-below-neg5.nc` #calc_composite


### ZW3 analysis

tas-composite  env_amp_median-date-list  zw3-w19-va-stats-extent75pct-filter90pct   ERAInterim   500hPa   030day-runmean   native-mermax   .ext

tas-composite  env-amp-median   date-list  zw3-w19-va-extent75pct-filter90pct   ERAInterim   500hPa   030day-runmean   native-mermax   .ext

* `<composite>`: `<variable>-composite`
* `<metric>`
* `<file_type>`
* `<filters>`: `<analysis_category>-<wavenumbers>-<orig_var>-<filter1>-<filter2>-...-<filterN>
  * analysis category can be `zw3` or `psa`
  
