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
import numpy.ma as ma
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


version_info = 'Created %s using %s \n' %(datetime.utcnow().isoformat(),__file__) #,__version__)  #%(datetime.utcnow().isoformat(), sys.argv[0])


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
    monthly_climatology_mean = numpy.zeros(12)
    monthly_climatology_std = numpy.zeros(12)
    for i in range(0,12):
        monthly_climatology_mean[i] = numpy.mean(base_timeseries[i:ntime_base:12])
	monthly_climatology_std[i] = numpy.std(base_timeseries[i:ntime_base:12])

    return monthly_climatology_mean, monthly_climatology_std


def calc_monthly_anomaly(complete_timeseries,base_timeseries,months):
    """Calculates the monthly anomaly"""  # assumes that the base_timeseries starts in January
    
    # Calculate the monthly climatology #
    
    monthly_climatology_mean, monthly_climatology_std = calc_monthly_climatology(base_timeseries)
    
    # Calculate the monthly anomaly #
    
    ntime_complete = len(complete_timeseries)
    monthly_anomaly = numpy.zeros(ntime_complete)
    for i in range(0,ntime_complete):
	month_index = months[i]
	monthly_anomaly[i] = complete_timeseries[i] - monthly_climatology_mean[month_index-1]
    
    
    return monthly_anomaly 


def monthly_normalisation(complete_timeseries,base_timeseries,months):
    """Calculates the monthly anomaly"""  # assumes that the base_timeseries starts in January
    
    # Calculate the monthly climatology #
    
    monthly_climatology_mean, monthly_climatology_std = calc_monthly_climatology(base_timeseries)

    # Normalise the entire timeseries #
    
    ntime_complete = len(complete_timeseries)
    monthly_normalised = numpy.zeros(ntime_complete)
    for i in range(0,ntime_complete):
	month_index = months[i]
	monthly_normalised[i] = (complete_timeseries[i] - monthly_climatology_mean[month_index-1]) / monthly_climatology_std[month_index-1]
    
    
    return monthly_normalised


def calc_SAM(index,ifile,efile,outfile_name,base_period):
    """Calculates an index of the Southern Annular Mode"""
    
    # Read the input file #

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
    
    # Read data, extract the required latitudes, calculate zonal mean anomalies #
        
    latitude = fin.getAxis('latitude')
    var_complete=fin(ifile.variable_name,order='tyx')
    var_base=fin(ifile.variable_name,time=(base_period[0],base_period[1]),order='tyx')
    
    lats = [-40,-65]
    monthly_normalised_timeseries = {}
    
    for lat in lats: 
    
	index, value = min(enumerate(latitude), key=lambda x: abs(x[1]-float(lat)))
	print 'File latitude for', lat, '=', value

	complete_timeseries = numpy.mean(var_complete[:,index,:],axis=1)
	base_timeseries = numpy.mean(var_base[:,index,:],axis=1)

        monthly_normalised_timeseries[lat] = monthly_normalisation(complete_timeseries,base_timeseries,months)

    
    SAMI_timeseries = monthly_normalised_timeseries[-40] - monthly_normalised_timeseries[-65]


    # Write the text file output #

    fout = open(outfile_name,'w')
    fout.write('SAM Index (as per Marshall 2003 and Gong & Wang 1999) \n')
    base = 'Base period = %s  to %s \n' %(base_period[0],base_period[1])
    fout.write(base)   
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    fout.write(' YR   MON  SAMI \n') 

    for ii in range(0,len(time)):
        print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],SAMI_timeseries[ii])
    
    fout.close()


def calc_IEMI(index,ifile,efile,outfile_name,base_period):
    """Calculates the Improved ENSO Modoki Index"""
    
    ## Calculate the index ##
    
    # Read the input file #

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
    
    # Calculate the index #
    
    regions = ['EMI_A','EMI_B','EMI_C']
    anomaly_timeseries = {}
    
    for reg in regions: 
        
	region = globals()[reg]
	
	var_complete=fin(ifile.variable_name,region,order='tyx')
        var_base=fin(ifile.variable_name,region,time=(base_period[0],base_period[1]),order='tyx')

        ntime_complete,nlats,nlons = numpy.shape(var_complete)
        ntime_base,nlats,nlons = numpy.shape(var_base)

        var_complete_flat = numpy.reshape(var_complete,(int(ntime_complete),int(nlats * nlons)))    # Flattens the spatial dimension
        var_base_flat = numpy.reshape(var_base,(int(ntime_base),int(nlats * nlons)))

       # Calculate the index #

        complete_timeseries = numpy.mean(var_complete_flat,axis=1)
        base_timeseries = numpy.mean(var_base_flat,axis=1)
        
	anomaly_timeseries[reg] = calc_monthly_anomaly(complete_timeseries,base_timeseries,months)	


    IEMI_timeseries = 3*anomaly_timeseries['EMI_A'] - 2*anomaly_timeseries['EMI_B'] - anomaly_timeseries['EMI_C']


    ## Calculate the error ##
    
    if efile:
    
        # Calculate the mean error at each timestep #
	
	var_error_flat = {}
	for reg in regions: 
        
	    region = globals()[reg]
	
	    var_error=fin('err',region,order='tyx')
	    ntime_error,nlats_error,nlons_error = numpy.shape(var_error)
	    
	    var_error_flat[reg] = numpy.reshape(var_error,(int(ntime_error),int(nlats_error * nlons_error)))
	
	var_error_stack = numpy.hstack((var_error_flat['EMI_A'],var_error_flat['EMI_B'],var_error_flat['EMI_C']))
	
        error_timeseries = numpy.mean(var_error_stack,axis=1)


    fin.close()
    
    ## Write the text file output ##

    fout = open(outfile_name,'w')
    fout.write('Improved ENSO Modoki Index (as per Gen et al. 2010) \n')
    base = 'Base period = %s  to %s \n' %(base_period[0],base_period[1])
    fout.write(base)  
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    
    if efile:
        fout.write(' YR   MON   IEMI   error \n') 
	for ii in range(0,len(time)):
            print >> fout, '%4i %3i %7.2f %7.2f' %(years[ii],months[ii],IEMI_timeseries[ii],error_timeseries[ii])
    else:
	fout.write(' YR   MON  IEMI \n') 
	for ii in range(0,len(time)):
            print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],IEMI_timeseries[ii])
    
    fout.close()
    

def calc_NINO(index,ifile,efile,outfile_name,base_period):
    """Calculates the NINO SST indices"""
    
    ## Calculate the index ##
    
    # Read the input file #

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
    
    # Calculate each index #

    region,minlat,maxlat,minlon,maxlon = define_region(index)

    var_complete=fin(ifile.variable_name,region,order='tyx')
    var_base=fin(ifile.variable_name,region,time=(base_period[0],base_period[1]),order='tyx')

    ntime_complete,nlats,nlons = numpy.shape(var_complete)
    ntime_base,nlats,nlons = numpy.shape(var_base)

    var_complete_flat = numpy.reshape(var_complete,(int(ntime_complete),int(nlats * nlons)))    # Flattens the spatial dimension
    var_base_flat = numpy.reshape(var_base,(int(ntime_base),int(nlats * nlons)))

    # Calculate the index #

    complete_timeseries = numpy.mean(var_complete_flat,axis=1)
    base_timeseries = numpy.mean(var_base_flat,axis=1)

    NINO_timeseries = calc_monthly_anomaly(complete_timeseries,base_timeseries,months)	

    
    
    ## Calculate the error ##
    
    if efile:
 
        # Calculate the mean error at each timestep #
	
	var_error=fin('err',region,order='tyx') 
	ntime_error,nlats_error,nlons_error = numpy.shape(var_error)
	
	var_error_flat = numpy.reshape(var_error,(int(ntime_error),int(nlats_error * nlons_error)))
	
	error_timeseries = numpy.mean(var_error_flat,axis=1)   #Could use numpy.max for a slightly different error measurement

    fin.close()

    ## Write the text file output ##

    fout = open(outfile_name,'w')
    coords = ' (lat: %s to %s, lon: %s to %s)' %(str(minlat),str(maxlat),str(minlon),str(maxlon))
    title = index+coords+'\n'
    fout.write(title)
    base = 'Base period = %s  to %s \n' %(base_period[0],base_period[1])
    fout.write(base)  
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    
    if efile:
        headers = ' YR   MON  %s   error \n' %(index)
        fout.write(headers) 
        for ii in range(0,len(time)):
            print >> fout, '%4i %3i %7.2f %7.2f' %(years[ii],months[ii],NINO_timeseries[ii],error_timeseries[ii])
    else:
        headers = ' YR   MON  %s \n' %(index)
        fout.write(headers) 
        for ii in range(0,len(time)):
            print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],NINO_timeseries[ii])
    
    fout.close()

	    
function_for_index = {
    'NINO':        calc_NINO,
    'IEMI':        calc_IEMI,
    'SAMI':        calc_SAM,
                	  }     

def main(index,infile_name,efile,outfile_name,base_period):
    """Run the program"""

    ## Get the input file attributes ##

    ifile = InputFile(infile_name)
        
    ## Initialise relevant index function ##
    
    calc_index = function_for_index[index[0:4]]

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
	    IEMI, SAMI
	
	Example
	    /opt/cdat/bin/cdat calc_climate_index.py NINO34 /work/dbirving/datasets/Merra/data/ts_Merra_surface_monthly_native.nc 
	    /work/dbirving/processed/indices/data/ts_Merra_NINO34_monthly_native.txt
	    
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
    
