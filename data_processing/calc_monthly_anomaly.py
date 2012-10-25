#!/usr/bin/env cdat

"""
GIT INFO: $Id$
Filename:     calc_monthly_anomaly.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  


Updates | By | Description
--------+----+------------
23 August 2012 | Damien Irving | Initial version.

"""


__version__= '$Revision$'   ## Get this working for Git


### Import required modules ###

import optparse
from optparse import OptionParser
import os
import sys
from datetime import datetime

import netCDF4

import cdms2 

import numpy
import numpy.ma as ma


def calc_monthly_climatology(base_data,miss_val):
    """Calculates the monthly climatology"""
    
    ntime,nlat,nlon = numpy.shape(base_data)
    monthly_climatology = numpy.ones([12,nlat,nlon]) * miss_val
    for i in range(0,12):
        monthly_climatology[i,:,:] = numpy.ma.mean(base_data[i:ntime:12,:,:],axis=0) 
	## FIX: Note that for the Merra ts land masked data, the assignment of the numpy.mean values to monthly_climatology
	## changes the -- values to 0.0. 

    return monthly_climatology


def calc_monthly_anomaly(complete_data,base_data,months,miss_val):
    """Calculates the monthly anomaly"""  
    
    ## Calculate the monthly climatology ##
    
    monthly_climatology = calc_monthly_climatology(base_data,miss_val)
    
    ## Calculate the monthly anomaly ##
    
    ntime,nlat,nlon = numpy.shape(complete_data)
    monthly_anomaly = numpy.ones([ntime,nlat,nlon]) * miss_val
    for i in range(0,ntime):
	month_index = months[i]
	monthly_anomaly[i,:,:] = numpy.ma.subtract(complete_data[i,:,:], monthly_climatology[month_index-1,:,:])
	# FIX: Note that for the Merra ts land masked data, the assignment of the numpy.substract values to monthly_anomaly
	## changes the -- values to 0.0. 
    
    return monthly_anomaly, monthly_climatology 


def write_outfile(infile_name,infile_variable,outfile_name,outfile_data,var_complete,start_date,end_date,time_units,time_calendar,stat='anomaly'):
    """Writes output file for either climatology or anomaly stat"""
    
    # Define stat specific info #
    
    if stat == 'anomaly':
        short_history = 'Calculated monthly anomaly'	 
        long_history = 'Calculated anomaly relative to the %s to %s monthly climatology.'  %(start_date,end_date)
    elif stat == 'climatology':
        short_history = 'Calculated monthly climatology'	 
        long_history = 'Calculated monthly climatology (%s to %s)'  %(start_date,end_date)
	
	
    # Write the output file #

    outfile = netCDF4.Dataset(outfile_name, 'w', format='NETCDF3_CLASSIC')

    # Global attributes #

    setattr(outfile,'Title','Monthly anomaly')
    setattr(outfile,'Contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(outfile,'History',short_history)
    setattr(outfile,'Sourcefile',infile_name)
    setattr(outfile,'Created','Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0]))
    setattr(outfile,'Format','NETCDF3_CLASSIC')

    # Latitude and longitude #
    
    ntime,nlat,nlon = numpy.shape(var_complete)
    
    outfile.createDimension('latitude',nlat)
    outfile.createDimension('longitude',nlon)
    
    lats = outfile.createVariable('latitude',numpy.dtype('float32').char,('latitude',))
    lons = outfile.createVariable('longitude',numpy.dtype('float32').char,('longitude',))

    lats.long_name = 'Latitude'
    lats.units = 'degrees_north'
    lats.standard_name = 'latitude'
    lats.axis = 'Y'
    
    lons.long_name = 'Longitude'
    lons.units = 'degrees_east'
    lons.standard_name = 'longitude'
    lons.axis = 'X'

    lats[:] = var_complete.getLatitude()
    lons[:] = var_complete.getLongitude()   

    # Time axis (if anomaly) #

    if stat == 'anomaly':
	outfile.createDimension('time',None)
	times = outfile.createVariable('time',numpy.dtype('float32').char,('time',)) 
	times.units = time_units
	times.calendar = time_calendar
	times[:] = var_complete.getTime()
    
    
    # Output variable #

    outfile_data = outfile_data.astype(numpy.float32)
    if stat == 'anomaly':
	anom = outfile.createVariable(infile_variable,numpy.dtype('float32').char,('time','latitude','longitude'),fill_value=var_complete._FillValue[0])
	anom.units = var_complete.units
	anom.long_name = var_complete.long_name
	anom.history = long_history
	anom.standard_name = infile_variable

	anom[:] = outfile_data
    
    else:
        count = 0
	for i in ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']:
	    clim = outfile.createVariable(infile_variable+'_'+i,numpy.dtype('float32').char,('latitude','longitude'),fill_value=var_complete._FillValue[0])
	    clim.units = var_complete.units
	    clim.long_name = var_complete.long_name
	    clim.history = long_history+' for '+i
	    clim.standard_name = infile_variable
	    
	    clim[:] = outfile_data[count,:,:]
            
	    count = count + 1
	    
    outfile.close()
    

def main(infile_name,infile_variable,outfile_name,start_date,end_date,climatology):
    """Run the program"""
    
    ## Read the input file ##

    fin=cdms2.open(infile_name,'r')
    
    ## Get the time axis information ##
    
    time_data = fin.getAxis('time').asComponentTime()
    time_units = getattr(fin.getAxis('time'), 'units')
    time_calendar = getattr(fin.getAxis('time'), 'calendar')
    
    months = []
    for ii in range(0,len(time_data)):
	months.append(int(str(time_data[ii]).split('-')[1]))
    
    ## Calculate the monthly climatology and anomaly ##
    
    var_base=fin(infile_variable,time=(start_date,end_date),order='tyx')
    var_complete=fin(infile_variable,order='tyx')
    
    #Make sure missing values are masked
    
    var_base_ma = ma.masked_values(var_base,var_base._FillValue)
    var_complete_ma = ma.masked_values(var_complete,var_complete._FillValue)
    
    fin.close()
    
    monthly_anomaly, monthly_climatology = calc_monthly_anomaly(var_complete_ma,var_base_ma,months,var_complete._FillValue)

    ## Wtite the outfile file/s ##
 
    if climatology:
        write_outfile(infile_name,infile_variable,outfile_name,monthly_climatology,var_complete,start_date,end_date,time_units,time_calendar,stat='climatology')
    else:
        write_outfile(infile_name,infile_variable,outfile_name,monthly_anomaly,var_complete,start_date,end_date,time_units,time_calendar)
   
   
if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {u_file} {u_name} {v_file} {v_name} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-s", "--start",dest="start",type='string',default='1981-01-01',help="start date for the base period [default='1981-01-01']")
    parser.add_option("-e", "--end",dest="end",type='string',default='2010-12-31',help="end date for the base period [default='2010-12-31']")
    parser.add_option("-c", "--climatology",action="store_true",dest="climatology",default=False,help="output the climatology instead of the anomaly [default=False]")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            calc_monthly_anomaly.py [-M] [-h] [-s] [-e] [-c] {input_file} {input_variable} {output_file}

	Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -s -> Start date for the base period [default='1981-01-01']
	    -e -> End date for the base period [default='2010-12-31']
	    -c -> Output monthly climatology instead of the monthly anomaly [default=False]

	Description
            Takes a monthly timeseries and calculates the monthly anomaly timeseries    

	Environment
            Need to load cdat

	Author
            Damien Irving, 23 Aug 2012.

	Bugs
            The script currently has issues with missing values (e.g. with land masked files). A short-term
	    work around would be to use the skin temperature (which has no missing data) and then apply a mask 
	    after the climatology or anomaly has been calculated.  
	    
	    Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)

    else:

        # Repeat the command line arguments #

	print 'Input file: ', args[0]
	print 'Ouput file: ', args[2]

    infile_name, infile_variable, outfile_name = args  
    
    main(infile_name,infile_variable,outfile_name,options.start,options.end,options.climatology)

