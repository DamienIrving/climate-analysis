### ERA-Interim data download, 14 June 2012 ###

## Location ##  

http://data-portal.ecmwf.int/data/d/interim_full_daily


## Variables - surface, monthly mean of daily means ## 

Mean sea level pressure (originally msl, now psl)
2m temperature (originally t2m, now tas)
Sea surface temperature (originally sstk, now tos)


## Variables - pressure levels, monthly mean of daily means ##

Geopotential, 200 hPa and 500 hPa (z)
U velocity, 200 hPa (originally u, now ua)
V velocity, 200 hPa (originally v, now va)


## Post processing ##

# Commands #

cdo chname
cdo sellevel
cdo selname
cdo invertlat (the original files go from N to S instead of S to N)

# Notes #

Most of the data have a scale_factor (which you must multiply by) and add_offset
(which you must add) attribute. The following is an example of how you might
deal with these:

# Extract velocity fields.
u = g.variables['10u']
v = g.variables['10v']

# Extract scale factors and offsets.
u_scale = u.scale_factor
u_offset = u.add_offset
v_scale = v.scale_factor
v_offset = v.add_offset

# Apply scale factors and offsets.
up = u_scale*u[:] + u_offset
vp = v_scale*v[:] * v_offsetl
 

cdo invertlat (Warning): Some data values (min=-28365 max=32767) are outside the
valid range (-32768 - 32767) of the used output precision!
Use the CDO option -b 32 or -b 64 to increase the output precision.

# How I did it (e.g. temp) #

cdo chname,t2m,tas -selname,t2m in.nc out.nc
cdo -b 64 invertlat
cdo -b 64 mulc,[scale_factor]
cdo -b 64 addc,[offset]


