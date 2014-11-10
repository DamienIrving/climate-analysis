# Data Reference Syntax

## Directory syntax

* `~/<dataset>/downloads`: A temporary dumping ground for downloaded files.  
* `~/<dataset>/data`: For data files I want to keep and use. To move from downloads to data
they must have undergone pre-processing 

## Standard variable abbreviations

This list gives the stardard variable id, followed by the `standard_name` / `long_name` (these both need to be the same and have underscores instead of spaces
to keep iris/cartopy happy.

* `zg`, `geopotential_height`: Geopotential height
* `tas`, `surface_air_temperature`: Surface air temperature
* `psl`: Sea level pressure
* `sf`: Streamfunction
* `ua`, `eastward_wind`: Eastward wind velocity
* `va`, `northward_wind`: Northward wind velocity
* `vrot`: Northward wind velocity on a rotated sphere (i.e. the north pole has been shifted and the meridional wind re-calculated accordingly) 
* `envva`, `hilbert_transformed_northward_wind`: Wave envelope calculated via a Hilbert Transform

In order to be compliant with my iris/cartopy plotting routines, all variables should start with these standard names (and have the corresponding unaltered `standard_name` 
and `long_name`) then things can be appended to the id using underscores (e.g. `tas_DJF`). 

## File name syntax

### Basic data files 

`<var>_<dataset>_<level>_<time>_<spatial>.nc`  

Sub-categories:  

* `<time>`: `<tstep>-<aggregation>-<season>`
* `<spatial>`: `<grid>-<region>-<bounds>-<np>`

Where:  

* `<tstep>`: `daily`, `monthly`
* `<aggregation>`: `030day-runmean`, `anom-wrt-1979-2011`, `anom-wrt-all`
* `<season>`: `JJA`, `MJJASO`
* `<grid>`: `native` or something like `y181x360`, which describes the number of latitude (181) and longitude (360) points (in this case it is a 1 by 1 degree horizontal grid).
* `<region>`: Region names are defined in `netcdf_io.py`
* `<bounds>`: e.g. `lon225E335E-lat10S10N` or `mermax`, `zonal-anom` 
* `<np>`: North pole location, e.g. `np20N260E`

Examples include:  
`psl_Merra_surface_daily_y181x360.nc` 

### More complex file names

`<inside>_<project>_<filters>_<prev-var>_<dataset>_<level>_<time>_<spatial>.nc` 

Sub-categories:

* `<inside>`: The variable inside the file. e.g. `tas-composite`, `datelist`
* `<project>`: `zw3` or `psa`
* `<filters>`: e.g. `w19`, 

