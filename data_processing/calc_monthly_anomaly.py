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
from cdms2 import MV2

import numpy
import numpy.ma as ma


def calc_monthly_climatology(base_data,miss_val,annual_anomaly):
    """Calculates the monthly climatology"""
    
    ntime,nlat,nlon = numpy.shape(base_data)
    monthly_climatology = numpy.ma.ones([12,nlat,nlon]) * miss_val
    
    if annual_anomaly:
	annual_mean = numpy.ma.mean(base_data,axis=0)
	print numpy.shape(annual_mean)
	monthly_climatology[:,:,:] = numpy.resize(annual_mean,numpy.shape(monthly_climatology))
    else:
	for i in range(0,12):
            monthly_climatology[i,:,:] = numpy.ma.mean(base_data[i:ntime:12,:,:],axis=0) 

    return monthly_climatology


def calc_monthly_anomaly(complete_data,base_data,months,miss_val,annual_anomaly):
    """Calculates the monthly anomaly"""  
    
    ## Calculate the monthly climatology ##
    
    monthly_climatology = calc_monthly_climatology(base_data,miss_val,annual_anomaly)
    
    ## Calculate the monthly anomaly ##
    
    ntime,nlat,nlon = numpy.shape(complete_data)
    monthly_anomaly = numpy.ma.ones([ntime,nlat,nlon]) * miss_val
    for i in range(0,ntime):
	month_index = months[i]
	monthly_anomaly[i,:,:] = numpy.ma.subtract(complete_data[i,:,:], monthly_climatology[month_index-1,:,:])
	
    return monthly_anomaly, monthly_climatology 


def write_outfile(fin,infile_name,infile_variable,outfile_name,out_data,var_complete,start_date,end_date,annual_anomaly,stat='anomaly'):
    """Writes output file for either climatology or anomaly stat"""
    
    # Define stat specific info #
    
    if annual_anomaly:
        tscale = 'annual'
    else:
        tscale = 'monthly'
    
    if stat == 'anomaly':
        short_history = 'Calculated monthly anomaly'	 
        long_history = 'Calculated anomaly relative to the %s to %s %s climatology.'  %(start_date,end_date,tscale)
    elif stat == 'climatology':
        short_history = 'Calculated monthly climatology'	 
        long_history = 'Calculated monthly climatology (%s to %s)'  %(start_date,end_date)
	
	
    # Write the output file #

    outfile = netCDF4.Dataset(outfile_name, 'w', format='NETCDF3_CLASSIC')

    # Global attributes #

    for att_name in fin.attributes.keys():
        if att_name != "history":
	    setattr(outfile, att_name, fin.attributes[att_name])

    if 'history' in fin.attributes.keys():
        old_history = fin.attributes['history']
    else:
        old_history = ''
	
    setattr(outfile, 'history', """%s: %s from %s using %s, format=NETCDF3_CLASSIC\n%s""" %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
    short_history,infile_name,sys.argv[0],old_history))

    # Latitude and longitude #
    
    in_lat = var_complete.getLatitude()
    in_lon = var_complete.getLongitude()
    ntime,nlat,nlon = numpy.shape(var_complete)
    
    outfile.createDimension('latitude',nlat)
    outfile.createDimension('longitude',nlon)
    
    lats = outfile.createVariable('latitude','f4',('latitude',))
    lons = outfile.createVariable('longitude','f4',('longitude',))

    for att_name in in_lat.attributes.keys():
        setattr(lats, att_name, in_lat.attributes[att_name])
    for att_name in in_lon.attributes.keys():
	setattr(lons, att_name, in_lon.attributes[att_name])

    lats[:] = in_lat[:]
    lons[:] = in_lon[:]   

    # Time axis (if anomaly) #

    if stat == 'anomaly':
	outfile.createDimension('time', None)
	times = outfile.createVariable('time','f4',('time',)) 
	
	in_time = var_complete.getTime()
	for att_name in in_time.attributes.keys():
	    setattr(times, att_name, in_time.attributes[att_name])
	
	times[:] = in_time[:]
    
    
    # Output variable #
    
    out_data = MV2.array(out_data)
    out_data = out_data.astype(numpy.float32)
    
    if stat == 'anomaly':
	out_var = outfile.createVariable(infile_variable,'f4',('time','latitude','longitude',),fill_value=var_complete.missing_value)
	
	for att_name in var_complete.attributes.keys():
	    if (att_name != "_FillValue") and (att_name != "history"):
                setattr(out_var, att_name, var_complete.attributes[att_name])
        setattr(out_var,'history',long_history)
	setattr(out_var, 'missing_value', var_complete.missing_value)
	
	out_var[:] = out_data
    
    else:
        count = 0
	for i in ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']:
	    out_var = outfile.createVariable(infile_variable+'_'+i,'f4',('latitude','longitude',),fill_value=var_complete.missing_value)
	    
	    for att_name in var_complete.attributes.keys():
		if (att_name != "_FillValue") and (att_name != "history"):
                    setattr(out_var, att_name, var_complete.attributes[att_name])
            setattr(out_var,'history',long_history+' for '+i)
	    setattr(out_var, 'missing_value', var_complete.missing_value)
	        
	    out_var[:] = out_data[count,:,:]
            
	    count = count + 1

 
    outfile.close()
    

def main(infile_name,infile_variable,outfile_name,start_date,end_date,climatology,annual_anomaly):
    """Run the program"""
    
    ## Open the input file ##

    fin=cdms2.open(infile_name,'r')
    
    ## Get the time axis information ##
    
    time_data = fin.getAxis('time').asComponentTime()
    months = []
    for ii in range(0,len(time_data)):
	months.append(int(str(time_data[ii]).split('-')[1]))
    
    
    ## Extract the required data ##
    
    var_base=fin(infile_variable,time=(start_date,end_date),order='tyx')
    var_complete=fin(infile_variable,order='tyx')
    
    assert (hasattr(var_base, 'missing_value')), 'Input variable must have missing_value attribute'

      
    ## Calculate the monthly climatology and anomaly ##
    
    monthly_anomaly, monthly_climatology = calc_monthly_anomaly(var_complete,var_base,months,var_complete.missing_value,annual_anomaly)

    ## Wtite the outfile file/s ##
 
    if climatology:
        write_outfile(fin,infile_name,infile_variable,outfile_name,monthly_climatology,var_complete,start_date,end_date,annual_anomaly,stat='climatology')
    else:
        write_outfile(fin,infile_name,infile_variable,outfile_name,monthly_anomaly,var_complete,start_date,end_date,annual_anomaly)
   
    fin.close()
   
   
if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {u_file} {u_name} {v_file} {v_name} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-s", "--start",dest="start",type='string',default='1981-01-01',help="start date for the base period [default='1981-01-01']")
    parser.add_option("-e", "--end",dest="end",type='string',default='2010-12-31',help="end date for the base period [default='2010-12-31']")
    parser.add_option("-c", "--climatology",action="store_true",dest="climatology",default=False,help="output the climatology instead of the anomaly [default=False]")
    parser.add_option("-a", "--annual",action="store_true",dest="annual",default=False,help="subtract the annual mean instead of the monthly mean in calculating the anomaly [default=False]")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            calc_monthly_anomaly.py [-M] [-h] [-s] [-e] [-c] [-a] {input_file} {input_variable} {output_file}

	Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -a -> Subtract the annual mean instead of the monthly mean in calculating the anomaly
	    -s -> Start date for the base period [default='1981-01-01']
	    -e -> End date for the base period [default='2010-12-31']
	    -c -> Output monthly climatology instead of the monthly anomaly [default=False]

	Description
            Takes a monthly timeseries and calculates the monthly anomaly timeseries    

	Environment
            Need to load cdat

	Author
            Damien Irving, 23 Aug 2012.

	Example
	    abyss.earthsci.unimelb.edu.au
	        /opt/cdat/bin/cdat calc_monthly_anomaly.py 
		/work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly_native-ocean.nc ts
		/work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc
	    	
		
	Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)

    else:

        # Repeat the command line arguments #

	print 'Input file: ', args[0]
	print 'Ouput file: ', args[2]

    infile_name, infile_variable, outfile_name = args  
    
    main(infile_name,infile_variable,outfile_name,options.start,options.end,options.climatology,options.annual)

