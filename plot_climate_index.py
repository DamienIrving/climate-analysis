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


color_list = ['red','blue','green','yellow']


class InputFile(object):
    patterns = [
        ('monthly_timeseries',
         True, #meaning the model file
         re.compile(r'(?P<variable_name>\S+)_(?P<dataset>\S+)_(?P<index_class>\S+)_(?P<timescale>\S+)_(?P<grid>\S+).txt')),        
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


def get_times(time_axis,window):
    """Adjusts time axis according to window"""

    start_year = int(str(time_axis[0]).split('-')[0])
    start_month = int(str(time_axis[0]).split('-')[1])
    end_year = int(str(time_axis[-1]).split('-')[0])
    end_month = int(str(time_axis[-1]).split('-')[1])

    if window > 1.0:
        start_adjust = math.floor(window / 2.0)
	end_adjust = math.ceil(window / 2.0)
	time_length = len(time_axis) - (window-1)

	start_month = start_month + start_adjust
	if start_month > 12.0:
	    start_month = start_month - 12
	    start_year = start_year + 1

        end_month = end_month - end_adjust
	if end_month < 1.0:
	    end_month = end_month + 12
	    end_year = end_year - 1

    return start_year,start_month,end_year,end_month


def extract_Nino(file_list,index,window):
    """Calculates SST indices"""

    # Extract the index #

    plot_data = {}
    plot_times = {}
    
    for ifile in file_list:
        
	# Initialise data variables #
	
	years = []
	months = []
	anomaly_data = {}
	anomaly_data['NINO12'] = []
	anomaly_data['NINO3'] = []
	anomaly_data['NINO34'] = []
	anomaly_data['NINO4'] = []
	
        # Read the input file, read the data and flatten the spatial dimension #
   
        fin = open(ifile.fname,'r')
	line = fin.readline()
	count = 0.0
	while line:
	    if count != 0.0:
		year,month,temp1,anom_NINO12,temp2,anom_NINO3,temp3,anom_NINO4,temp4,anom_NINO34 = line.split()
		years.append(int(year))
		months.append(int(month))
		anomaly_data['NINO12'].append(float(anom_NINO12))
		anomaly_data['NINO3'].append(float(anom_NINO3))
		anomaly_data['NINO4'].append(float(anom_NINO4))
		anomaly_data['NINO34'].append(float(anom_NINO34))
	    
	    count = count + 1
	    line = fin.readline()
	    
	
	# Define output values for plotting #
	
	# Data	
        plot_data[ifile.fname] = anomaly_data[index]
	plot_times[ifile.fname] = [years[0],months[0],years[-1],months[-1]]
    
	# Title
	if window > 1.0:
	    add_on = ' ('+str(window)+' month running mean)'
	else:
	    add_on = ''
	title_text = index+add_on 

        # Units
	units_text = 'Anomaly (deg C)'


    return plot_data,plot_times,title_text,units_text
    
    
def create_plot(file_list,plot_data,plot_times,title_text,units_text,location,outfile_name):
    """Creates the plot"""

    # Start the figure #
    
    fig = plt.figure()
    ax1 = fig.add_axes([0.1,0.1,0.85,0.8])  #left side, bottom, right side, top

    # Plot the data for each dataset #

    count = 0
    for ifile in file_list:

	# Intialise year and month variables #

	start_year,start_month,end_year,end_month = plot_times[ifile.fname]

	end_month = end_month + 1
	if end_month > 12.0:
	    end_month = end_month - 12
	    end_year = end_year + 1

        # Create time values #

	date1 = datetime.date( int(start_year), int(start_month), 16 )
	date2 = datetime.date( int(end_year), int(end_month), 16 )
	delta = datetime.timedelta(minutes=43830)   # timedelta doesn't take monnths. For a 365.25 day year, the average month length is 43830 minutes 

	dates = drange(date1, date2, delta)

        # Plot the data #

        ax1.plot_date(dates,numpy.array(plot_data[ifile.fname]),color=color_list[count],lw=2.0,label=ifile.dataset,linestyle='-',marker='None')
        
	count = count + 1 
        del date1
	del date2
	del delta
        del dates         
  
    # Plot guidelines #
 
    ax1.axhline(y=0.0,linestyle='-',color='0.8')
    ax1.axhline(y=0.5,linestyle='--',color='0.8')
    ax1.axhline(y=-0.5,linestyle='--',color='0.8')
    
    # Define aspects of the time axis #

    rule_major = rrulewrapper(YEARLY, bymonth=1, interval=5)
    loc_major = RRuleLocator(rule_major)
    formatter_major = DateFormatter('%Y')    # '%m/%d/%y' capital Y for 4-digit year and b or B for full month name

    rule_minor = rrulewrapper(YEARLY, bymonth=1, interval=1)
    loc_minor = RRuleLocator(rule_minor)
    formatter_minor = DateFormatter('')    # '%m/%d/%y'
 
    ax1.xaxis.set_major_locator(loc_major)
    ax1.xaxis.set_major_formatter(formatter_major)
    ax1.xaxis.set_minor_locator(loc_minor)
    ax1.xaxis.set_minor_formatter(formatter_minor)
     
    # Plot labels (including title, axis labels and legend) #

    labels = ax1.get_xticklabels()
    plt.setp(labels, rotation=0, fontsize=10)

    plt.ylabel(units_text)
    ax1.set_title(title_text)
    font = font_manager.FontProperties(size='medium')
    ax1.legend(loc=location) #prop=font,numpoints=1,labelspacing=0.3)  #,ncol=2)
    
    # Output the figure #
    
    if outfile_name:
        plt.savefig(outfile_name)
    else:
        plt.show()


function_for_index = {
    'NINO':        extract_Nino,
#    'IEMI':        extract_IEMI,
#    'SAM':         extract_SAM,
                	  }     

def main(file_list,index,outfile_name,location,window):
    """Run the program"""

    file_list = [InputFile(f) for f in file_list]
    
    ## Initialise relevant function ##
    
    extract_index = function_for_index[index[0:4]]

    ## Calculate the index ##

    plot_data, plot_times, title_text, units_text = extract_index(file_list,index,window)
    
    ## Create the plot ##
    
    create_plot(file_list,plot_data,plot_times,title_text,units_text,location,outfile_name)
    

if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-l", "--legend", dest="legend",default=2,type='int',help="Location of the figure legend [defualt = 2]")
    parser.add_option("-o", "--outfile",dest="outfile",type='str',default=None,help="Name of output file [default = None]")
    parser.add_option("-w", "--window",dest="window",type='int',default=1,help="window for running average [default = 1]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            python plot_climate_index.py [-M] [-h] [-l] [-o] [-w] {index} {input file 1} {input file 2} ... {input file N}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    -l  ->  Location of the legend [default = 2]
	    -o  ->  Name of the output file [default = None = image is just shown instead]
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
	    /opt/cdat/bin/cdat plot_climate_index.py -w 5 NINO34 /work/dbirving/processed/indices/ts_Merra_NINO_monthly_native.nc
	    /work/dbirving/processed/indices/tos_ERSSTv3B_NINO_monthly_native.txt
	    /work/dbirving/processed/indices/tos_OISSTv2_NINO_monthly_native.txt
	    
	Author
            Damien Irving, 22 Jun 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
            
    file_list = args[1:]
    index = args[0]     

    print 'Input_files:',file_list
    print 'Index:',index 

    main(file_list,index,options.outfile,options.legend,options.window)
    
