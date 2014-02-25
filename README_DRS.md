# Data Reference Syntax

## Directory syntax

* `~/<dataset>/downloads`: A temporary dumping ground for downloaded files.  
* `~/<dataset>/data/`: For data files that have only undergone minimal cosmetic 
changes since download (e.g. alterations of attributes to achieve CF compliance
or a change of units, but no averaging or other manipulation of the data).  
* `~/<dataset>/data/processed/`: For data files that have undergone only one or two
steps of standard processing (e.g. an anomaly timeseries or derived variable like
the streamfunction.  
* `~/<dataset>/data/processsed/stats/`: Statistics like eof analysis
* `~/<dataset>/data/processsed/rwid/`: Files relating to rossby wave identification


## Standard variable abbreviations

* `gz`: Geopotential height
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







