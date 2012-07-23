#!/usr/bin/env cdat

"""
GIT INFO: $Id$
Filename:     calc_climate_index.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates the selected climate index

Input:        List of netCDF files to plot
Output:       Text file

Updates | By | Description
--------+----+------------
23 February 2012 | Damien Irving | Initial version.


Copyright CSIRO, 2012
"""


__version__= '$Revision$'   ## Get this working for Git


### Import required modules ###

import optparse
from optparse import OptionParser
import os
import sys
from datetime import datetime

import Scientific.IO.NetCDF
from Scientific.IO.NetCDF import NetCDFFile

import cdms2 

import numpy
import numpy.ma as ma


def calc_monthly_climatology(base_data):
    """Calculates the monthly climatology"""
    ntime,nlat,nlon = numpy.shape(base_data)
    monthly_climatology = numpy.zeros([12,nlat,nlon])
    for i in range(0,12):
        monthly_climatology[i,:,:] = numpy.ma.mean(base_data[i:ntime:12,:,:],axis=0)
	
    return monthly_climatology


def calc_monthly_anomaly(complete_data,base_data,months):
    """Calculates the monthly anomaly"""  # assumes that the base_timeseries starts in January
    
    ## Calculate the monthly climatology ##
    
    monthly_climatology = calc_monthly_climatology(base_data)
    
    ## Calculate the monthly anomaly ##
    
    ntime,nlat,nlon = numpy.shape(complete_data)
    monthly_anomaly = numpy.zeros([ntime,nlat,nlon])
    for i in range(0,ntime):
	month_index = months[i]
	monthly_anomaly[i,:,:] = complete_data[i,:,:] - monthly_climatology[month_index-1,:,:]
    
    return monthly_anomaly 


def main(infile_name,infile_variable,outfile_name,start_date,end_date):
    """Run the program"""
    
    ## Read the input file ##

    fin=cdms2.open(infile_name,'r')
    
    ## Get the time axis information ##
    
    time = fin.getAxis('time').asComponentTime()
    months = []
    
    for ii in range(0,len(time)):
	months.append(int(str(time[ii]).split('-')[1]))
    
    ## Calculate the monthly climatology ##
    
    var_base=fin(infile_variable,time=(start_date,end_date),order='tyx')
    var_complete=fin(infile_variable,order='tyx')
    
    ntime,nlat,nlon = numpy.shape(var_complete)
    
    monthly_anomaly = calc_monthly_anomaly(var_complete,var_base,months)

    
    # Write the output file #

    outfile = NetCDFFile(outfile_name, 'w') 

    # Global attributes #

    setattr(outfile,'Title','Monthly anomaly')
    setattr(outfile,'contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(outfile,'history','Calculated monthly anomaly')
    setattr(outfile,'sourcefile',infile_name)
    creation_text = 'Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0])
    setattr(outfile,'created',creation_text)

    # Dimensions #

    outfile.createDimension('time',None)
    outfile.createDimension('latitude',nlat)
    outfile.createDimension('longitude',nlon)

    times = outfile.createVariable('time',numpy.dtype('float32').char,('time',))
    lats = outfile.createVariable('latitude',numpy.dtype('float32').char,('latitude',))
    lons = outfile.createVariable('longitude',numpy.dtype('float32').char,('longitude',))
    
    times.units = getattr(fin.getAxis('time'), 'units')
    times.calendar = getattr(fin.getAxis('time'), 'calendar')
    
    lats.long_name = 'Latitude'
    lats.units = 'degrees_north'
    lats.standard_name = 'latitude'
    lats.axis = 'Y'
    
    lons.long_name = 'Longitude'
    lons.units = 'degrees_east'
    lons.standard_name = 'longitude'
    lons.axis = 'X'
    
    times[:] = var_complete.getTime()
    lats[:] = var_complete.getLatitude()
    lons[:] = var_complete.getLongitude()   

    # Variable #

    anom = outfile.createVariable(infile_variable,numpy.dtype('float32').char,('time','latitude','longitude'))
    anom.units = var_complete.units
    anom.long_name = var_complete.long_name
    anom.history = 'Calculated anomaly relative to the %s to %s monthly climatology.'  %(start_date,end_date)
    anom.standard_name = infile_variable
    #anom._FillValue = var_complete._FillValue

    monthly_anomaly = monthly_anomaly.astype(numpy.float32)
    anom[:] = monthly_anomaly


    outfile.close()
    fin.close()
    
   
if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {u_file} {u_name} {v_file} {v_name} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-s", "--start",dest="start",type='string',default='1981-01-01',help="start date for the base period [default='1981-01-01']")
    parser.add_option("-e", "--end",dest="end",type='string',default='2010-12-31',help="end date for the base period [default='2010-12-31']")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            calc_monthly_anomaly.py [-M] [-h] [-s] [-e] {input_file} {input_variable} {output_file}

	Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -s -> Start date for the base period [default='1981-01-01']
	    -e -> End date for the base period [default='2010-12-31']

	Description
            Takes a monthly timeseries and calculates the monthly anomaly timeseries    

	Environment
            Need to load cdat

	Author
            Damien Irving, 23 Jul 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)

    else:

        # Repeat the command line arguments #

	print 'Input file: ', args[0]
	print 'Ouput file: ', args[2]

    infile_name, infile_variable, outfile_name = args  
    
    main(infile_name,infile_variable,outfile_name,options.start,options.end)

