## Data download and pre-processing

The pre-processing scripts in this directory ensure that my downloaded data are 
compliant with the Climate and Forecast Metadata Convention 
(see [here](http://cf-pcmdi.llnl.gov/) and 
[here](http://badc.nerc.ac.uk/help/formats/netcdf/index_cf.html) for details) and also
my data reference syntax (see `../data_reference_syntax.md`).

The most important and/or common aspects of the process are as follows:

```
(% denotes 'whatever it comes as')

# Longitude

Must go from 0 to 360 and include the following attributes:  
 
  * standard_name = "longitude"  
  * long_name = "longitude"  
  * units = "degrees_east"  
  * axis = "X"  
  * bounds = "lon_bnds"  
 
# Latitude

Must go from -90 to 90 and include the following attributes:  

  * standard_name = "latitude"  
  * long_name = "latitude"  
  * units = "degrees_north"  
  * axis = "Y"  
  * bounds = "lat_bnds" 
 
# Time

  * standard_name = "time"  
  * bounds = "time_bnds"  
  * axis="T"  
  * units = %  
  * calendar = %  

# Variable

Remove offsets and scale factors and have attributes like the following:  

  * standard_name = "precipitation_flux"  
  * long_name = "Precipitation"  
  * original_name = "Name in original dataset"  
  * units = "kg m-2 s-1"  
  * _FillValue = %  
  * missing_value =   

Note that: 
  * missing_value is required for cdat
  * xray doesn't use _FillValue or missing_value - it just puts in NaN
    (cdo and iris seem to be able to handle that) 

```
