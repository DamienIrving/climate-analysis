# Data Reference Syntax

## Directory syntax

* `~/<dataset>/downloads`: A temporary dumping ground for downloaded files.  
* `~/<dataset>/data/`: For data files that have only undergone minimal cosmetic 
changes since download (e.g. alterations of attributes to achieve CF compliance
or a change of units, but no averaging or other manipulation of the data).  
* `~/<dataset>/data/processed/`: For data files that have undergone only one or two
steps of standard processing (e.g. an anomaly timeseries or derived variable like
the streamfunction.  
* `~/<dataset>/data/processsed/stats/`: Highly modified data.

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


### Filtered composites based on ROIM method

`<var>_<dataset>_<level>_<time>_<spatial>_<hovmoller>_<search>_<clip>_<filter>.nc`

`tas_Merra_250hPa_daily-anom-wrt-1979-2012-SON-composite-mean_y181x360_hov-vrot-env_w567-lon225E-335E-lat10S-10N_absolute14_mariebyrdland-va-below-neg5.nc`


## Standard variable abbreviations

* `gz`: Geopotential height
* `psl`: Sea level pressure
* `sf`: Streamfunction
* `ua`: Eastward wind velocity
* `va`: Northward wind velocity
* `vrot`: Northward wind velocity on a rotated sphere (i.e. the north pole has been shifted and the meridional wind re-calculated accordingly) 






