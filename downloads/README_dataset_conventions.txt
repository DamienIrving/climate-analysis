### Conventions for observational datasets ###

Note that where possible, the Climate and Forecast Metadata Convention should
be followed (CF compliance):
http://cf-pcmdi.llnl.gov/
http://badc.nerc.ac.uk/help/formats/netcdf/index_cf.html


## File name format ##

Downloaded data are processed into the following format:
(all original downloaded datafiles are then deleted)

%variable%_%dataset%_%level%_%timescale%_%grid%.nc


%variable%
Consistent with the CMIP convention (unless variable is not a CMIP one)
tas = surface air temperature
tos = sea surface temperature
ts = surface skin temperature
z = geopotential
zg = geopotential height
ua = eastward wind component
va = northward wind component
psl = sea level pressure
sftlf = land area fraction
sftof = sea area fraction

sf = streamfunction
vp = velocity potential


## File attributes ##
(% denotes 'whatever it comes as')

# lon/lat

standard_name = "longitude"  or "latitude"
long_name = "longitude"
units = "degrees_east"
axis = "X"
bounds = "lon_bnds"

# time

standard_name = "time"
bounds = "time_bnds"
units = %
calendar = "proleptic_gregorian"

# variable
(remove offsets and scale factors)

standard_name = "precipitation_flux"
long_name = "Precipitation"
original_name = "Name in original dataset"
units = "kg m-2 s-1"
_FillValue = %
missing_value = 





