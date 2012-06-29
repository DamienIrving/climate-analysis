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
        ('climate_index',
         True,
         re.compile(r'(?P<variable_name>\S+)_(?P<dataset>\S+)_(?P<level>\S+)_(?P<timescale>\S+)_(?P<grid>\S+).nc')),        
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


def calc_monthly_anomaly(complete_timeseries,base_timeseries,months):
    """Calculates the monthly anomaly"""  # assumes that the base_timeseries starts in January
    
    # Calculate the monthly climatology #
    
    ntime_base = len(base_timeseries)
    monthly_climatology = numpy.zeros(12)
    for i in range(0,12):
        monthly_climatology[i] = numpy.mean(base_timeseries[i:ntime_base:12])
    
    # Calculate the monthly anomaly #
    
    ntime_complete = len(complete_timeseries)
    monthly_anomaly = numpy.zeros(ntime_complete)
    for i in range(0,ntime_complete):
	month_index = months[i]
	monthly_anomaly[i] = complete_timeseries[i] - monthly_climatology[month_index-1]
    
    
    return monthly_anomaly 


def calc_SAM(ifile,outfile_name):
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
    var_base=fin(ifile.variable_name,time=('1981-01-01','2010-12-31'),order='tyx')
    
    lats = [-40,-65]
    anomaly_timeseries = {}
    
    for lat in lats: 
    
	index, value = min(enumerate(latitude), key=lambda x: abs(x[1]-float(lat)))
	print 'File latitude for', lat, '=', value

	var_complete = numpy.squeeze(var_complete[:,index,:])
	var_base = numpy.squeeze(var_base[:,index,:])

	complete_timeseries = numpy.mean(var_complete,axis=1)
	base_timeseries = numpy.mean(var_base,axis=1)

	anomaly_timeseries[lat] = calc_monthly_anomaly(complete_timeseries,base_timeseries,months)

    
    SAM_timeseries = anomaly_timeseries[-40] - anomaly_timeseries[-65]


    # Write the text file output #

    fout = open(outfile_name,'w')
    fout.write('SAM Index (as per Marshall 2003 and Gong & Wang 1999) \n')
    fout.write('Base period = 1981-2010 \n')  
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    fout.write(' YR   MON  SAM \n') 

    for ii in range(0,len(time)):
        print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],SAM_timeseries[ii])
    
    fout.close()


def calc_IEMI(ifile,outfile_name):
    """Calculates the Improved ENSO Modoki Index"""
    
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
        var_base=fin(ifile.variable_name,region,time=('1981-01-01','2010-12-31'),order='tyx')

        ntime_complete,nlats,nlons = numpy.shape(var_complete)
        ntime_base,nlats,nlons = numpy.shape(var_base)

        var_complete_flat = numpy.reshape(var_complete,(int(ntime_complete),int(nlats * nlons)))    # Flattens the spatial dimension
        var_base_flat = numpy.reshape(var_base,(int(ntime_base),int(nlats * nlons)))

       # Calculate the index #

        complete_timeseries = numpy.mean(var_complete_flat,axis=1)
        base_timeseries = numpy.mean(var_base_flat,axis=1)
        
	anomaly_timeseries[reg] = calc_monthly_anomaly(complete_timeseries,base_timeseries,months)	


    IEMI_timeseries = 3*anomaly_timeseries['EMI_A'] - 2*anomaly_timeseries['EMI_B'] - anomaly_timeseries['EMI_C']


    # Write the text file output #

    fout = open(outfile_name,'w')
    fout.write('Improved ENSO Modoki Index \n')
    fout.write('Base period = 1981-2010 \n')  
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    fout.write(' YR   MON  IEMI \n') 

    for ii in range(0,len(time)):
        print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],IEMI_timeseries[ii])
    
    fout.close()
    

def calc_Nino(ifile,outfile_name):
    """Calculates the NINO SST indices"""

    nino_indices = ['NINO12','NINO3','NINO4','NINO34']
    
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

    raw_data = {}
    anomaly_data = {}
    for index in nino_indices:

        region,minlat,maxlat,minlon,maxlon = define_region(index)

        var_complete=fin(ifile.variable_name,region,order='tyx')
	var_base=fin(ifile.variable_name,region,time=('1981-01-01','2010-12-31'),order='tyx')

	ntime_complete,nlats,nlons = numpy.shape(var_complete)
	ntime_base,nlats,nlons = numpy.shape(var_base)

        var_complete_flat = numpy.reshape(var_complete,(int(ntime_complete),int(nlats * nlons)))    # Flattens the spatial dimension
	var_base_flat = numpy.reshape(var_base,(int(ntime_base),int(nlats * nlons)))

        # Calculate the index #

	complete_timeseries = numpy.mean(var_complete_flat,axis=1)
	base_timeseries = numpy.mean(var_base_flat,axis=1)
	
	monthly_anomaly_timeseries = calc_monthly_anomaly(complete_timeseries,base_timeseries,months)	

        # Write the data into arrays that get printed to file #

        if complete_timeseries[0] > 200.0:
            raw_data[index] = complete_timeseries - 273.15
	else:
	    raw_data[index] = complete_timeseries
        
	anomaly_data[index] = monthly_anomaly_timeseries


    # Write the text file output #

    fout = open(outfile_name,'w')
    fout.write('Nino indices \n')
    fout.write('Base period = 1981-2010 \n')  
    fout.write(version_info)
    fout.write('Input file = '+ifile.fname+'\n')
    fout.write(' YR   MON  NINO12   ANOM   NINO3    ANOM   NINO4    ANOM   NINO34   ANOM \n') 

    for ii in range(0,len(time)):
        print >> fout, '%4i %3i %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f %7.2f' %(years[ii],months[ii],
                                                                                   raw_data['NINO12'][ii],anomaly_data['NINO12'][ii],
                                                                                   raw_data['NINO3'][ii],anomaly_data['NINO3'][ii],
                                                                                   raw_data['NINO4'][ii],anomaly_data['NINO4'][ii],
                                                                                   raw_data['NINO34'][ii],anomaly_data['NINO34'][ii])
    fout.close()
	    
 
function_for_index = {
    'NINO':        calc_Nino,
    'IEMI':        calc_IEMI,
    'SAM':         calc_SAM,
                	  }     

def main(index,infile_name,outfile_name):
    """Run the program"""

    ## Get the input file attributes ##

    infile = InputFile(infile_name)
    
    ## Initialise relevant index function ##
    
    calc_index = function_for_index[index]

    ## Calculate the index ##

    calc_index(infile,outfile_name)
    
 

if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 3:
	print """
	Usage:
            cdat calc_climate_index.py [-M] [-h] {index} {input file} {output file}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit

        Pre-defined indices
            NINO, IEMI, SAM
        
	Note
	    The base period is hard-wired as 1981-01-01 to 2010-12-31
	
	Example
	    /opt/cdat/bin/cdat calc_climate_index.py NINO /work/dbirving/datasets/Merra/data/ts_Merra_surface_monthly_native.nc 
	    /work/dbirving/processed/indices/ts_Merra_NINO_monthly_native.txt
	    
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

        main(args[0],args[1],args[2])
    
