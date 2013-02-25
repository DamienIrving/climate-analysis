## Summary - using CDAT in the weather/climate sciences ##

netCDF            - be CF compliant!
                  - use attributes: data should be self-describing

ipython           - excellent interactive development environment (IDE)
                  - use dir() and ? to explore objects
	          - use pdb for debugging
	          - use ! to run any command at the system shell

uvcdat            - for quickly viewing your data

import cdms2      - for netCDF input and output

import cdutil     - climate relevant utilities (climatologies, regions
                    calendars etc)
		 
import genutil    - climate relevant statistics (correlation, percentiles, etc)

import regrid2    - for regirdding

import MV2        - for masked arrays
                  - it's a copy of numpy.ma, but the data keep their attributes 

import matplotlib - for all plotting (timeseries, spatial maps, etc)
                  - from mpl_toolkits.basemap import Basemap, for spatial maps
		  - from mpl_toolkits.basemap import shiftgrid, for longitude axis fiddling

programming tips  - use argparse for parsing the command line
                  - create your own modules to avoid duplication of code
	          - use docstrings as primary documentation method
	          - use pylint to test the quality of your code
