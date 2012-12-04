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
import re
import os
import sys

import cdms2 
import genutil

import numpy
import numpy.ma
import math

from datetime import datetime


## Define global variables ##

NINO1 = cdms2.selectors.Selector(latitude=(-10,-5,'cc'),longitude=(270,280,'cc'))   # the 'cc' means a closed interval [] e.g. [260,270]
NINO2 = cdms2.selectors.Selector(latitude=(-5,0,'cc'),longitude=(270,280,'cc'))
NINO12 = cdms2.selectors.Selector(latitude=(-10,0,'cc'),longitude=(270,280,'cc'))
NINO3 = cdms2.selectors.Selector(latitude=(-5,5,'cc'),longitude=(210,270,'cc'))
NINO34 = cdms2.selectors.Selector(latitude=(-5,5,'cc'),longitude=(190,240,'cc'))
NINO4 = cdms2.selectors.Selector(latitude=(-5,5,'cc'),longitude=(160,210,'cc'))
EMI_A = cdms2.selectors.Selector(latitude=(-10,10,'cc'),longitude=(165,220,'cc'))
EMI_B = cdms2.selectors.Selector(latitude=(-15,5,'cc'),longitude=(250,290,'cc'))
EMI_C = cdms2.selectors.Selector(latitude=(-10,20,'cc'),longitude=(125,145,'cc'))


version_info = 'Created %s using %s \n' %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"),__file__) #,__version__)  #%(datetime.utcnow().isoformat(), sys.argv[0])


## Define relevant functions and classes ##


class InputFile(object):
    patterns = [
        ('data',
         True,
         re.compile(r'(?P<variable_name>\S+)_(?P<dataset>\S+)_(?P<level>\S+)_(?P<timescale>\S+)_(?P<grid>\S+).nc'))  
    ]
    def __init__(self, fname):
        self.fname = fname
        self.atts = {}

        basename = os.path.basename(fname)
        for name, isfile, pattern in InputFile.patterns:
            m = pattern.match(basename)
            if m:
                self.atts = m.groupdict()
                self.type = name
                self.isfile = isfile
                break
        if not self.atts:
           raise ValueError("Unknown file type: " + fname)

    def __repr__(self):
        return self.fname

    def __getattr__(self, key):
        try:
            return super(InputFile, self).__getattr__(key)
        except AttributeError:
            if key in self.atts:
                return self.atts[key]
            else:
                raise


def define_region(region_name):
    
    # map string region to selector object
    if isinstance(region_name, basestring):
        if region_name in globals():
            region = globals()[region_name]
	else:
            print "Region is not defined in code"
            sys.exit(1)
    
    for selector_component in region.components():
        if selector_component.id == 'lat':
            minlat = selector_component.spec[0]
            maxlat = selector_component.spec[1]
        elif selector_component.id == 'lon':
            minlon = selector_component.spec[0]
            maxlon = selector_component.spec[1]

    return region,minlat,maxlat,minlon,maxlon


def calc_monthly_climatology(base_timeseries):
    ntime_base = len(base_timeseries)
    monthly_climatology_mean = numpy.ma.zeros(12)
    monthly_climatology_std = numpy.ma.zeros(12)
    for i in range(0,12):
        monthly_climatology_mean[i] = numpy.ma.mean(base_timeseries[i:ntime_base:12])
	monthly_climatology_std[i] = numpy.ma.std(base_timeseries[i:ntime_base:12])

    return monthly_climatology_mean, monthly_climatology_std


def calc_monthly_anomaly(complete_timeseries,base_timeseries,months):
    """Calculates the monthly anomaly"""  # assumes that the base_timeseries starts in January
    
    # Calculate the monthly climatology #
    
    monthly_climatology_mean, monthly_climatology_std = calc_monthly_climatology(base_timeseries)
    
    # Calculate the monthly anomaly #
    
    ntime_complete = len(complete_timeseries)
    monthly_anomaly = numpy.ma.zeros(ntime_complete)
    for i in range(0,ntime_complete):
	month_index = months[i]
	monthly_anomaly[i] = numpy.ma.subtract(complete_timeseries[i], monthly_climatology_mean[month_index-1])
    
    
    return monthly_anomaly 


def monthly_normalisation(complete_timeseries,base_timeseries,months):
    """Calculates the monthly anomaly"""  # assumes that the base_timeseries starts in January
    
    # Calculate the monthly climatology #
    
    monthly_climatology_mean, monthly_climatology_std = calc_monthly_climatology(base_timeseries)

    # Normalise the entire timeseries #
    
    ntime_complete = len(complete_timeseries)
    monthly_normalised = numpy.ma.zeros(ntime_complete)
    for i in range(0,ntime_complete):
	month_index = months[i]
	monthly_normalised[i] = numpy.ma.divide((numpy.ma.subtract(complete_timeseries[i], monthly_climatology_mean[month_index-1])), monthly_climatology_std[month_index-1])
    
    
    return monthly_normalised


def read_input(ifile):
    """Reads relevant data from the input file"""

    try:
        fin=cdms2.open(ifile.fname,'r')
    except cdms2.CDMSError:
        print 'Unable to open file: ', ifile
	sys.exit(0)
    
    # Get the time axis information #
    
    time = fin.getAxis('time').asComponentTime()
    years = []
    months = []
    
    for ii in range(0,len(time)):
        years.append(int(str(time[ii]).split('-')[0]))
	months.append(int(str(time[ii]).split('-')[1]))


    return fin, time, years, months


def write_output(index,ifile,outfile_name,base_period,header,years,months,timeseries,error=None):
    """Writes the output file"""
    
    fout = open(outfile_name,'w')
    fout.write(header)
    base = 'Base period = %s  to %s \n' %(base_period[0],base_period[1])
    fout.write(base)  
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    
    if error:
        fout.write(' YR   MON   %s   error \n' %(index)) 
	for ii in range(0,len(timeseries)):
            print >> fout, '%4i %3i %7.2f %7.2f' %(years[ii],months[ii],timeseries[ii],error[ii])
    else:
	fout.write(' YR   MON  %s \n' %(index)) 
	for ii in range(0,len(timeseries)):
            print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],timeseries[ii])

    fout.close()
    

def calc_error(fin,regions):
    """Calculates the error timeseries for SST indices"""
    
    var_error_flat = {}
    for reg in regions: 

	region = globals()[reg]

	var_error=fin('err',region,order='tyx')
	ntime_error,nlats_error,nlons_error = numpy.shape(var_error)

	var_error_flat[reg] = numpy.ma.reshape(var_error,(int(ntime_error),int(nlats_error * nlons_error)))

    if len(regions) == 1:
        var_error_stack = var_error_flat
    elif len(regions) == 2: 
        var_error_stack = numpy.ma.hstack((var_error_flat[regions[0]],var_error_flat[regions[1]]))
    elif len(regions) == 3: 
        var_error_stack = numpy.ma.hstack((var_error_flat[regions[0]],var_error_flat[regions[1]],var_error_flat[regions[2]]))

    error_timeseries = numpy.ma.mean(var_error_stack,axis=1)  #Could use numpy.max for a slightly different error measurement


    return error_timeseries


def calc_reg_anomaly_timeseries(reg,fin,ifile,base_period,months):
    """Calculates the anomaly timeseries for a given region"""
    
    region = globals()[reg]
	
    var_complete=fin(ifile.variable_name,region,order='tyx')
    var_base=fin(ifile.variable_name,region,time=(base_period[0],base_period[1]),order='tyx')

    assert (hasattr(var_complete, 'missing_value')), 'Input variable must have missing_value attribute'

    ntime_complete,nlats,nlons = numpy.shape(var_complete)
    ntime_base,nlats,nlons = numpy.shape(var_base)

    var_complete_flat = numpy.ma.reshape(var_complete,(int(ntime_complete),int(nlats * nlons)))    # Flattens the spatial dimension
    var_base_flat = numpy.ma.reshape(var_base,(int(ntime_base),int(nlats * nlons)))

   # Calculate the anomalies #

    complete_timeseries = numpy.ma.mean(var_complete_flat,axis=1)
    base_timeseries = numpy.ma.mean(var_base_flat,axis=1)

    anomaly_timeseries = calc_monthly_anomaly(complete_timeseries,base_timeseries,months)


    return anomaly_timeseries


def calc_SAM(index,ifile,efile,outfile_name,base_period):
    """Calculates an index of the Southern Annular Mode"""
    
    # Read the input file #
    
    fin, time, years, months = read_input(ifile)
    
    # Read data, extract the required latitudes, calculate zonal mean anomalies #
        
    latitude = fin.getAxis('latitude')
    var_complete=fin(ifile.variable_name,order='tyx')
    var_base=fin(ifile.variable_name,time=(base_period[0],base_period[1]),order='tyx')
     
    lats = [-40,-65]
    monthly_normalised_timeseries = {}
    
    for lat in lats: 
    
	index, value = min(enumerate(latitude), key=lambda x: abs(x[1]-float(lat)))
	print 'File latitude for', lat, '=', value

	complete_timeseries = numpy.ma.mean(var_complete[:,index,:],axis=1)
	base_timeseries = numpy.ma.mean(var_base[:,index,:],axis=1)

        monthly_normalised_timeseries[lat] = monthly_normalisation(complete_timeseries,base_timeseries,months)

    SAMI_timeseries = numpy.ma.subtract(monthly_normalised_timeseries[-40], monthly_normalised_timeseries[-65])

    # Write the text file output #
    
    header = 'SAM Index (as per Marshall 2003 and Gong & Wang 1999) \n'
    write_output(index,ifile,outfile_name,base_period,header,years,months,SAMI_timeseries)
    
    
    fin.close()


def calc_IEMI(index,ifile,efile,outfile_name,base_period):
    """Calculates the Improved ENSO Modoki Index"""
    
    ## Calculate the index ##
    
    # Read the input file #
    
    fin, time, years, months = read_input(ifile)
    
    # Calculate the index #
    
    regions = ['EMI_A','EMI_B','EMI_C']
    anomaly_timeseries = {}
    
    for reg in regions: 
	anomaly_timeseries[reg] = calc_reg_anomaly_timeseries(reg,fin,ifile,base_period,months)
    
    IEMI_timeseries = numpy.ma.subtract(numpy.ma.subtract(numpy.ma.multiply(anomaly_timeseries['EMI_A'],3.0),numpy.ma.multiply(anomaly_timeseries['EMI_B'],2.0)),anomaly_timeseries['EMI_C'])


    ## Calculate the error ##
    
    error_timeseries = calc_error(fin,regions) if efile else None
    
    
    ## Write the text file output ##

    header = 'Improved ENSO Modoki Index (as per Gen et al. 2010) \n'
    write_output(index,ifile,outfile_name,base_period,header,years,months,IEMI_timeseries,error=error_timeseries)

    
    fin.close()
    

def calc_NINO(index,ifile,efile,outfile_name,base_period):
    """Calculates the NINO SST indices"""
    
    ## Calculate the index ##
    
    # Read the input file #
    
    fin, time, years, months = read_input(ifile)
    region,minlat,maxlat,minlon,maxlon = define_region(index)
    
    # Calculate the NINO index
    
    NINO_timeseries = calc_reg_anomaly_timeseries(index,fin,ifile,base_period,months)
 
 
    ## Calculate the error ##
    
    error_timeseries = calc_error(fin,index) if efile else None
 
        
    ## Write the text file output ##

    coords = ' (lat: %s to %s, lon: %s to %s)' %(str(minlat),str(maxlat),str(minlon),str(maxlon))
    header = index+coords+'\n'
    
    write_output(index,ifile,outfile_name,base_period,header,years,months,NINO_timeseries,error=error_timeseries)

    
    fin.close()


def calc_NINO_new(index,ifile,efile,outfile_name,base_period):
    """Calculates the new Nino indices of Ren & Jin (2011)"""
    
    ## Calculate the index ##
    
    # Read the input file #
    
    fin, time, years, months = read_input(ifile)

    # Calculate the traditional NINO3 and NINO4 indices #
    
    regions = ['NINO3','NINO4']
    anomaly_timeseries = {}
    
    for reg in regions: 
	anomaly_timeseries[reg] = calc_reg_anomaly_timeseries(reg,fin,ifile,base_period,months)
	
    # Calculate the new Ren & Jin index #

    ntime = len(anomaly_timeseries['NINO3'])
    
    NINO_new_timeseries = numpy.ma.zeros(ntime)
    for i in range(0,ntime):
        NINO3_val = anomaly_timeseries['NINO3'][i]
	NINO4_val = anomaly_timeseries['NINO4'][i]
        product = NINO3_val * NINO4_val
	
	alpha = 0.4 if product > 0 else 0.0
	
	if index == 'NINOCT':
	    NINO_new_timeseries[i] = numpy.ma.subtract(NINO3_val,(numpy.ma.multiply(NINO4_val,alpha)))
	elif index == 'NINOWP':
	    NINO_new_timeseries[i] = numpy.ma.subtract(NINO4_val,(numpy.ma.multiply(NINO3_val,alpha)))
	

    ## Calculate the error ##
    
    error_timeseries = calc_error(fin,regions) if efile else None
	
    
    ## Write the text file output ##

    header = '%s index of Ren & Jin (2011) \n'  %(index)
    write_output(index,ifile,outfile_name,base_period,header,years,months,NINO_new_timeseries,error=error_timeseries)


    fin.close()


function_for_index = {
    'NINO':        calc_NINO,
    'NINO_new':    calc_NINO_new,
    'IEMI':        calc_IEMI,
    'SAM':         calc_SAM,
                	  }     

def main(index,infile_name,efile,outfile_name,base_period):
    """Run the program"""

    ## Get the input file attributes ##

    ifile = InputFile(infile_name)
        
    ## Initialise relevant index function ##
    
    if index[0:4] == 'NINO':
        if index == 'NINOCT' or index == 'NINOWP':
	    calc_index = function_for_index['NINO_new']
	else:
	    calc_index = function_for_index['NINO']
    else:
        calc_index = function_for_index[index]

    ## Calculate the index ##

    calc_index(index,ifile,efile,outfile_name,base_period)
    
 
if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-e", "--error",action="store_true",dest="error",default=False,help="Input file contains an additional error variable")
    parser.add_option("-b", "--base",dest="base_period",nargs=2,type='string',default=('1981-01-01','2010-12-31'),help="Start and end date for base period [default=('1981-01-01','2010-12-31')]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 3:
	print """
	Usage:
            cdat calc_climate_index.py [-M] [-h] [-e] {index} {input file} {output file}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    -e  ->  Input file contains an additional error variable
	    -b  ->  Start and end date for base period [default=('1981-01-01','2010-12-31')]

        Pre-defined indices
            NINO12, NINO3, NINO4, NINO34
	    NINOCT, NINOWP 
	    IEMI, SAM
	
	Example
	    /opt/cdat/bin/cdat calc_climate_index.py NINO34 /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly_native-ocean.nc 
	    /work/dbirving/processed/indices/data/ts_Merra_surface_NINO34_monthly_native-ocean.txt
	    
	Author
            Damien Irving, 26 Jun 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    else:
                
        print 'Index:', args[0]
        print 'Input file:', args[1]
        print 'Output file:', args[2]

        main(args[0],args[1],options.error,args[2],options.base_period)
    
