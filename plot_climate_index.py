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

from matplotlib.dates import YEARLY, MONTHLY, DateFormatter, rrulewrapper, RRuleLocator, drange
import datetime

import numpy
import numpy.ma as ma
import math


## Define global variables ##


color_list = ['red','blue','green','yellow','orange','purple','brown']


class InputFile(object):
    patterns = [
        ('monthly_timeseries',
         True, #meaning the model file
         re.compile(r'(?P<variable_name>\S+)_(?P<dataset>\S+)_(?P<index>\S+)_(?P<timescale>\S+)_(?P<grid>\S+).txt')),        
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


def get_times(years,months,window):
    """Adjusts time axis according to window"""

    start_year = years[0]
    start_month = months[0]
    end_year = years[-1]
    end_month = months[-1]

    if window > 1.0:
        start_adjust = math.floor(window / 2.0)
	end_adjust = math.ceil(window / 2.0)

	start_month = start_month + start_adjust
	if start_month > 12.0:
	    start_month = start_month - 12
	    start_year = start_year + 1

        end_month = end_month - end_adjust
	if end_month < 1.0:
	    end_month = end_month + 12
	    end_year = end_year - 1

    return start_year,start_month,end_year,end_month


def set_units(index,orig_units,axis):
    """Sets the units for the plot"""
    
    if index[0:4] == 'NINO':
        units = 'Anomaly (deg C)'
    elif index == 'IEMI':
        units = 'Anomaly (deg C)'
    elif index == 'SAMI':
        units = 'Pa'
    else:
        print 'Index not recognised'
        sys.exit(0)
    
    if units != orig_units and orig_units != 'temp':
        print '%s axis data do not have the same units'  %(axis)
	sys.exit(0)
    
    return units


def hi_lo(data_series,current_max,current_min):
    """Determines the new highest and lowest value"""
    
    highest = numpy.max(data_series)
    if highest > current_max:
        new_max = highest
    else:
        new_max = current_max
        
    lowest = numpy.min(data_series)
    if lowest < current_min:
        new_min = lowest
    else:
        new_min = current_min
    
    return new_max,new_min  


def extract_data(file_list,file_list_dims,windowp,windows):
    
    # Extract the index #

    plot_data = {}
    plot_times = {}
    count = 0
    for ifile in file_list:
        
	# Initialise data variables #
	
	years = []
	months = []
	data = []
	
        # Read the input file, read the data and flatten the spatial dimension #
   
        fin = open(ifile.fname,'r')
	line = fin.readline()
	switch = False
	while line:
	
	    if line.split()[0] == 'YR':
	        loc = line.split().index(ifile.index)
		switch = True

	    elif switch: 
		year = line.split()[0]
		month = line.split()[1]
		temp_data = line.split()[loc]
		years.append(int(year))
		months.append(int(month))
		data.append(float(temp_data))
	        
	    line = fin.readline()

	    
	# Apply the smoothing and adjust the time axis as necessary #
	
	if count < file_list_dims[0]:
	    window = windowp
	else:
	    window = windows
	
	smooth_data = genutil.filters.runningaverage(data,window)
	start_year,start_month,end_year,end_month = get_times(years,months,window)


	# Define output values for plotting #
	
        plot_data[ifile.fname] = smooth_data
	plot_times[ifile.fname] = [start_year,start_month,end_year,end_month]
    
        count = count + 1
	

    return plot_data,plot_times

    
def create_plot(file_list,file_list_dims,plot_data,plot_times,windowp,windows,outfile_name,setx,setyp,setys,ybuffer):
    """Creates the plot"""

    # Start the figure #
    
    fig = plt.figure()
    ax1 = fig.add_axes([0.1,0.1,0.78,0.8])  #left side, bottom, right side, top
    if file_list_dims[1] > 0:
        ax2 = ax1.twinx()
    
    # Set the title and units #   ### FIX TO ACCOUNT FOR SECOND PLOT

    title_text = 'Climate indices'
    
    
    # Plot the data for each dataset #

    count = 0
    units_text_ax1 = 'temp'
    units_text_ax2 = 'temp'
    min_year = 1e10
    max_year = -1e10
    min_time = 1e10
    max_time = -1e10
    min_y_ax1 = 1e10
    max_y_ax1 = -1e10
    min_y_ax2 = 1e10
    max_y_ax2 = -1e10
    
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
        
	max_time,min_time = hi_lo(dates,max_time,min_time)
        max_year,min_year = hi_lo(range(int(start_year),int(end_year)+1),max_year,min_year) 

        # Plot the data #
        
	timeseries = plot_data[ifile.fname]
	if ifile.index == 'IEMI':
	    timeseries = timeseries * -1
	label = ifile.index+', '+ifile.dataset
	if count < file_list_dims[0]:
	    units_text_ax1 = set_units(ifile.index,units_text_ax1,'Primary')
	    max_y_ax1,min_y_ax1 = hi_lo(timeseries,max_y_ax1,min_y_ax1)
	    
	    ax1.plot_date(dates,numpy.array(timeseries),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
            
	else:
	    units_text_ax2 = set_units(ifile.index,units_text_ax2,'Secondary')
	    max_y_ax2,min_y_ax2 = hi_lo(timeseries,max_y_ax2,min_y_ax2)
	    
	    ax2.plot_date(dates,numpy.array(timeseries),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
	
	count = count + 1 
        del date1
	del date2
	del delta
        del dates         
  
    # Plot guidelines #
 
    ax1.axhline(y=0.0,linestyle='-',color='0.8')
    
    if units_text_ax1 == 'Anomaly (deg C)':
        ax1.axhline(y=0.5,linestyle='--',color='0.8')
        ax1.axhline(y=-0.5,linestyle='--',color='0.8')
    
    # Define aspects of the time axis #

    if setx:
        time_range = setx[2] - setx[0]
    else:
        time_range = int(max_year) - int(min_year)
    
    if time_range < 4:
        rule_major = rrulewrapper(MONTHLY, interval=3)
        rule_minor = rrulewrapper(MONTHLY, interval=1)
	major_label = '%b %y'
	minor_label = ''
    elif time_range < 20:
        rule_major = rrulewrapper(YEARLY, bymonth=1, interval=1)
        rule_minor = rrulewrapper(MONTHLY, interval=1)
	major_label = '%Y'
	minor_label = ''
    else:
        rule_major = rrulewrapper(YEARLY, bymonth=1, interval=5)
	rule_minor = rrulewrapper(YEARLY, bymonth=1, interval=1)
	major_label = '%Y'
	minor_label = ''
        
    loc_major = RRuleLocator(rule_major)
    formatter_major = DateFormatter(major_label)    # '%m/%d/%y' capital Y for 4-digit year and b or B for full month name

    loc_minor = RRuleLocator(rule_minor)
    formatter_minor = DateFormatter(minor_label)    # '%m/%d/%y'
 
    ax1.xaxis.set_major_locator(loc_major)
    ax1.xaxis.set_major_formatter(formatter_major)
    ax1.xaxis.set_minor_locator(loc_minor)
    ax1.xaxis.set_minor_formatter(formatter_minor)
    
    # Define the range of the axes #
    
    y_maximum_ax1 = max(abs(max_y_ax1),abs(min_y_ax1))
    y_buffer_ax1 = (2 * y_maximum_ax1) * 0.03 
    ax1.axis([min_time,max_time,(-y_maximum_ax1 - y_buffer_ax1),(y_maximum_ax1 + ybuffer*y_buffer_ax1)])
    
    if file_list_dims[1] > 0:
        y_maximum_ax2 = max(abs(max_y_ax2),abs(min_y_ax2))
        y_buffer_ax2 = (2 * y_maximum_ax2) * 0.03 
        ax2.axis([min_time,max_time,(-y_maximum_ax2 - y_buffer_ax2),(y_maximum_ax2 + ybuffer*y_buffer_ax2)])
   
    # Alter the range according to user inputs
    
    if setx: 
        date_start = datetime.date( setx[0], setx[1], 16 ) 
        date_end = datetime.date( setx[2], setx[3], 16 )
        
	if setyp:
	    ax1.axis([date_start,date_end,setyp[0],setyp[1]])
	else:
	    x1,x2,y1,y2 = ax1.axis()
	    ax1.axis([date_start,date_end,y1,y2])
        
	if setys:
	    ax2.axis([date_start,date_end,setys[0],setys[1]])
	else:
	    x1,x2,y1,y2 = ax2.axis()
	    ax2.axis([date_start,date_end,y1,y2])
	
    elif setyp or setys:
         if setyp:
	     x1,x2,y1,y2 = ax1.axis()
	     ax1.axis([x1,x2,setyp[0],setyp[1]])
	 if setys:
	     x1,x2,y1,y2 = ax2.axis()
	     ax2.axis([x1,x2,setys[0],setys[1]])
	
         	 
    # Plot labels (including title, axis labels and legend) #

    labels_ax1 = ax1.get_xticklabels()
    plt.setp(labels_ax1, rotation=0, fontsize='medium')   

    ax1.set_ylabel(units_text_ax1,fontsize='medium')
    ax1.set_title(title_text)
    font = font_manager.FontProperties(size='medium')
    ax1.legend(loc=3,prop=font,ncol=2) #prop=font,numpoints=1,labelspacing=0.3)  #,ncol=2)
    
    if file_list_dims[1] > 0:
        ax2.set_ylabel(units_text_ax2, fontsize='medium')
        font = font_manager.FontProperties(size='medium')
        ax2.legend(loc=1,prop=font) #prop=font,numpoints=1,labelspacing=0.3)  #,ncol=2)
    
    # Output the figure #
    
    if outfile_name:
        plt.savefig(outfile_name)
    else:
        plt.show()


def main(primary_file_list,secondary_file_list,outfile_name,windowp,windows,setx,setyp,setys,ybuffer):
    """Run the program"""
    
    primary_file_list = [InputFile(f) for f in primary_file_list]
    
    if secondary_file_list:
        secondary_file_list = [InputFile(f) for f in secondary_file_list]
        file_list = primary_file_list + secondary_file_list
	file_list_dims = [len(primary_file_list),len(secondary_file_list)]
    else:
        file_list = primary_file_list
	file_list_dims = [len(primary_file_list),0]

    ## Calculate the index ##

    plot_data, plot_times = extract_data(file_list,file_list_dims,windowp,windows)
    
    ## Create the plot ##
        
    create_plot(file_list,file_list_dims,plot_data,plot_times,windowp,windows,outfile_name,setx,setyp,setys,ybuffer)
    

if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-o", "--outfile",dest="outfile",type='str',default=None,help="Name of output file [default = None]")
    parser.add_option("-s", "--secondary",dest="secondary",default=None,help="Comma separated list files to be plotted on the secondary y axis [default = None]")
    parser.add_option("-b", "--buffer",dest="buffer",type='float',default=4.0,help="Scale factor for y axis upper buffer [default = 4]")
    parser.add_option("--windowp",dest="windowp",type='int',default=1,help="window for primary axis running average [default = 1]")
    parser.add_option("--windows",dest="windows",type='int',default=1,help="window for secondary axis running average [default = 1]")
    parser.add_option("-x", "--setx",dest="setx",default=None,help="Comma separated list of time axis bounds (start_year,start_month,end_year,end_month) [default = None]")
    parser.add_option("--setyp",dest="setyp",default=None,help="Comma separated list of primary y axis bounds (min,max) [default = None]")
    parser.add_option("--setys",dest="setys",default=None,help="Comma separated list of secondary y axis bounds (min,max) [default = None]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            python plot_climate_index.py [-M] [-h] [-l] [-o] [-r] {input file 1} {input file 2} ... {input file N}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    -o  ->  Name of the output file [default = None = image is just shown instead]
	    -b  ->  Scale factor for y axis upper buffer [default = 4]
	    -s  ->  Comma separated list files to be plotted on the secondary y axis [default = None]
	    -x  ->  Comma separated list of time axis bounds (start_year,start_month,end_year,end_month) [default = None]
            -wp  ->  Window for primary axis running average [default = 1]
	    -ws  ->  Window for secondary axis running average [default = 1]
	    -setyp  ->  Comma separated list of primary y axis bounds (min,max) [default = None]
	    -setys  ->  Comma separated list of secondary y axis bounds (min,max) [default = None]
	
	Example
	    /opt/cdat/bin/cdat plot_climate_index.py -w 5 /work/dbirving/processed/indices/ts_Merra_NINO34_monthly_native-ocean.txt
	    /work/dbirving/processed/indices/tos_ERSSTv3B_NINO34_monthly_native.txt
	    /work/dbirving/processed/indices/tos_OISSTv2_NINO34_monthly_native.txt
	
	Note
	    The sign of the improved ENSO Modoki Index is automatically reversed to match the Nino indices
	    
	Author
            Damien Irving, 22 Jun 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    else:
        
	if options.secondary:
	    secondary_file_list = [str(s) for s in options.secondary.split(',')]
	else:
	    secondary_file_list = None
	
	if options.setx:
	    setx = [int(s) for s in options.setx.split(',')]
	else:
	    setx = None
	
	if options.setyp:
	    setyp = [int(s) for s in options.setyp.split(',')]
	else:
	    setyp = None
	
	if options.setys:
	    setys = [int(s) for s in options.setys.split(',')]
	else:
	    setys = None
	    
        primary_file_list = args[:]   


        main(primary_file_list,secondary_file_list,options.outfile,options.windowp,options.windows,setx,setyp,setys,options.buffer)
    
