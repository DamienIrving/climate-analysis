#!/usr/bin/env cdat

"""
GIT INFO: $Id$
Filename:     plot_climate_index.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots the selected climate index

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

Updates | By | Description
--------+----+------------
23 February 2012 | Damien Irving | Initial version.


Copyright CSIRO, 2012
"""


__version__= '$Revision$'


### Import required modules ###

import optparse
from optparse import OptionParser
import re
import os
import sys
from datetime import datetime

import cdms2 
import genutil

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from pylab import *

from matplotlib.dates import YEARLY, DateFormatter, rrulewrapper, RRuleLocator, drange
import datetime

import numpy
import numpy.ma as ma
import math


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


color_list = ['red','blue','green','yellow']


class InputFile(object):
    patterns = [
        ('monthly_timeseries',
         True, #meaning the model file
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


def calc_Nino(index,file_list,window):

    # Get the region information #

    region,minlat,maxlat,minlon,maxlon = define_region(index)

    for ifile in file_list:
    
        # Read the input file, read the data and flatten the spatial dimension #
    
        try:
            fin=cdms2.open(ifile.fname,'r')
	except cdms2.CDMSError:
            print 'Unable to open file: ', ifile
            continue

        var_all=fin(ifile.variable_name,region,order='tyx')
	var_base=fin(ifile.variable_name,region,time=('1981-01-01','2010-12-31'),order='tyx')

	ntime_all,nlats,nlons = numpy.shape(var_all)
	ntime_base,nlats,nlons = numpy.shape(var_base)

        var_all_flat = numpy.reshape(var_all,(int(ntime_all),int(nlats * nlons)))
	var_base_flat = numpy.reshape(var_base,(int(ntime_base),int(nlats * nlons)))
	
        # Calculate the index #
		
	print numpy.shape(var_all_flat)	
	all_timeseries = numpy.mean(var_all_flat,axis=1)
	print numpy.shape(all_timeseries)
	
	climatology_timeseries = numpy.mean(var_base_flat,axis=1)
	climatology_mean = numpy.mean(climatology_timeseries)
	
	anomaly_timeseries = all_timeseries - climatology_mean
	
	smooth_anomaly_timeseries = genutil.filters.runningaverage(anomaly_timeseries,window)

        # Create the time axis #

        time = fin.getAxis('time').asComponentTime()
	start_year = int(str(time[0]).split('-')[0])
	start_month = int(str(time[0]).split('-')[1])
	end_year = int(str(time[-1]).split('-')[0])
	end_month = int(str(time[-1]).split('-')[1])
        
	print start_month,start_year,end_month,end_year

        if window > 1.0:
            start_adjust = math.floor(window / 2.0)
	    end_adjust = math.ceil(window / 2.0)
	    time_length = len(time) - (window-1)

	    start_month = start_month + start_adjust
	    if start_month > 12.0:
		start_month = start_month - 12
		start_year = start_year + 1

            end_month = end_month - end_adjust
	    if end_month < 1.0:
		end_month = end_month + 12
		end_year = end_year - 1


	rule_major = rrulewrapper(YEARLY, bymonth=1, interval=5)
	loc_major = RRuleLocator(rule_major)
	formatter_major = DateFormatter('%b %Y')    # '%m/%d/%y'

        rule_minor = rrulewrapper(YEARLY, bymonth=1, interval=1)
	loc_minor = RRuleLocator(rule_minor)
	formatter_minor = DateFormatter('')    # '%m/%d/%y'

        end_month = end_month + 1
	if end_month > 12.0:
	    end_month = end_month - 12
	    end_year = end_year + 1

        print start_month,start_year,end_month,end_year
	date1 = datetime.date( int(start_year), int(start_month), 16 )
	date2 = datetime.date( int(end_year), int(end_month), 16 )
	delta = datetime.timedelta(minutes=43830)   # timedelta doesn't take monnths. For a 365.25 day year, the average month length is 43830 minutes 

	dates = drange(date1, date2, delta)

        fig = plt.figure()

	ax1 = fig.add_axes([0.1,0.15,0.8,0.8])  #left side, bottom, right side, top
	
	print len(dates), numpy.shape(smooth_anomaly_timeseries)
	plot_date(dates, smooth_anomaly_timeseries,color='red',lw=1.0,label=ifile.dataset,linestyle='-',marker='None')
	ax1.xaxis.set_major_locator(loc_major)
	ax1.xaxis.set_major_formatter(formatter_major)
	ax1.xaxis.set_minor_locator(loc_minor)
	ax1.xaxis.set_minor_formatter(formatter_minor)
	labels = ax1.get_xticklabels()
	plt.setp(labels, rotation=0, fontsize=10)

        plt.show()


function_for_index = {
    'NINO':        calc_Nino,
#    'IEMI':        calc_IEMI,
#    'SAM':         calc_SAM,
                	  }     

def main(index,file_list,outfile,location,window):
    """Run the program"""

    file_list = [InputFile(f) for f in file_list]
    
    ## Initialise relevant function ##
    
    calc_index = function_for_index[index[0:4]]

    ## Calculate and plot the index ##

    calc_index(index,file_list,window)
    

if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-l", "--legend", dest="legend",default=2,type='int',help="Location of the figure legend [defualt = 2]")
    parser.add_option("-w", "--window",dest="window",type='int',default=1,help="window for running average [default = 1]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            python plot_climate_index.py [-M] [-h] [-l] [-w] {index} {input file 1} {input file 2} ... {input file N} {output file}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    -l  ->  Location of the legend [default = 2]
	    -w  ->  Window for running average [default = 1]

        Pre-defined indices
            NINO1, NINO2, NINO12, NINO3, NINO34, NINO4
	    IEMI, SAM
        	    		
	Legend options
	    1: upper right
	    2: upper left
	    3: lower left
	    4: lower_right
	    5: right
	    6: center left
	    7: center right
	    8: lower center
	    9: upper center
	    10: center 
	
	Example
	    cdat plot_climate_index.py -l 3 -w 5 NINO34 tos_ERAInterim_surface_monthly_native.nc NINO34_ERAInterim.png
	    
	Author
            Damien Irving, 22 Jun 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
            
    file_list = args[1:-1]
    outfile = args[-1]
    index = args[0]     

    main(index,file_list,outfile,options.legend,options.window)
    
