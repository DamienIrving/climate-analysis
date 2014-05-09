# Conventions for observational datasets

Note that where possible, the Climate and Forecast Metadata Convention should be followed (CF compliance; 
see [here](http://cf-pcmdi.llnl.gov/) and [here](http://badc.nerc.ac.uk/help/formats/netcdf/index_cf.html) for details)

## File name format

Downloaded data are processed into the following format (all original downloaded datafiles are then deleted):  

```%variable%_%dataset%_%level%_%timescale%_%grid%.nc```  


```%variable%```  
Consistent with the CMIP convention (unless variable is not a CMIP one):  

  * tas = surface air temperature  
  * tos = sea surface temperature  
  * ts = surface skin temperature  
  * z = geopotential  
  * zg = geopotential height  
  * ua = eastward wind component  
  * va = northward wind component  
  * psl = sea level pressure 
  * sic = sea ice area fraction 
  * sftlf = land area fraction  
  * sftof = sea area fraction  
  * sf = streamfunction  
  * vp = velocity potential  

## Variables and dimensions  
(% denotes 'whatever it comes as')

### Longitude

Must go from 0 to 360 and include the following attributes:  
 
  * standard_name = "longitude"  
  * long_name = "longitude"  
  * units = "degrees_east"  
  * axis = "X"  
  * bounds = "lon_bnds"  
 
### Latitude

Must go from -90 to 90 and include the following attributes:  

  * standard_name = "latitude"  
  * long_name = "latitude"  
  * units = "degrees_north"  
  * axis = "Y"  
  * bounds = "lat_bnds" 
 
### Time

  * standard_name = "time"  
  * bounds = "time_bnds"  
  * axis="T"  
  * units = %  
  * calendar = %  

### Variable

Remove offsets and scale factors and have attributes like the following:  

  * standard_name = "precipitation_flux"  
  * long_name = "Precipitation"  
  * original_name = "Name in original dataset"  
  * units = "kg m-2 s-1"  
  * _FillValue = %  
  * missing_value =   
