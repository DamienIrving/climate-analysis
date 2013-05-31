### Merra data download, 20 June 2012 ###

## Location ##  

http://disc.sci.gsfc.nasa.gov/daac-bin/DataHoldings.pl
http://disc.sci.gsfc.nasa.gov/daac-bin/FTPSubset.pl

# Process

Use the links on the above site 
wget --content-disposition -i wget_2CUzuIUq


## Documentation ##

Daily data = IAU 2d atmospheric single-level diagnostics (tavg1_2d_slv_Nx)
Monthly data = Monthly IAU 2d atmospheric single-level diagnostics (tavgM_2d_slv_Nx)
 
Sea level pressure (originally slp, now psl)
Geopotential height, 250hPa (originally H, now gz)
Eastward wind component, 250 hPa (originally U, now ua)
Northward wind velocity, 250 hPa (originally V, now va)
Omega (=dp/dt; or vertical pressure velocity), 500 hPa (originally omega500, now wap)


## Post processing ##

# Commands #

cdo mergetime
cdo chname
cdo iften mask.nc infile.nc outfile.nc
cdo sellonlatbox,0,359.9,-90,90       # For having longitude values 0 to 360, instead of -180 to 180
ncatted -O -a units,psl,c,c,Pa        # Adding a units attribute (for psl in this case)
ncatted -O -a comments,psl,d,,        # Removing pointless attributes (comments in psl in this case)

cdo timmean -seldate,1981-01-01,2010-12-31               # For calculating the climatology
/home/dbirving/data_processing/calc_monthly_anomaly.py   # For calculating the anomaly
cdo merge                                                # For merging files with different variables into one file  

cdo divc,1000000                                         # For converting the sf units to something more manageable.
ncatted -O -a units,sf,m,c,"1.e+6 m2 s-1"

# Variables #

Streamfunction (sf)

# Notes #

I got the ocean mask file from NCI (/projects/ua4/)
