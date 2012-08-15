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

import cdms2 
import genutil

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from pylab import *

#import datetime
from datetime import datetime
from dateutil.rrule import *

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
        units = 'Monthly SAM index'
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


def convert_datetime(dates):
    """Converts a series of datetime instances to floating point numbers"""
    
    dates_float = numpy.zeros(len(dates[:]))
    for i in range(0,len(dates[:])):
        dates_float[i] = dates[i].year + (dates[i].month / 12.0) 
    
    return dates_float
    
    
def setup_plot(file_list,file_list_dims,plot_data,plot_times,setx,setyp,setys,ybuffer):
    """Determines all the details for the plot (e.g. data, axis bounds, tick marks)"""

    ## Define the data and details of the plot setup ##
    
    ydata = {}
    xdata = {} 
    ybounds = {}
    
    # Plot the data for each dataset #

    count = 0
    max_time = datetime(0,1,1)
    min_time = datetime(20000,12,31)
    min_y_a = 1e10
    max_y_a = -1e10
    min_y_b = 1e10
    max_y_b = -1e10
    
    for ifile in file_list:

	# Intialise year and month variables #

	start_year,start_month,end_year,end_month = plot_times[ifile.fname]

	end_month = end_month + 1
	if end_month > 12.0:
	    end_month = end_month - 12
	    end_year = end_year + 1

        # Subset the data along the time axis if neceassry, according to user defined time bounds #

        timeseries_complete = plot_data[ifile.fname] #read in timeseries data
	dates_complete = rrule(MONTHLY,dtstart=datetime(start_year,start_month,16),until=datetime(end_year,end_month,16))
	
	if setx:
	    start_year_user,start_month_user,end_year_user,end_month_user = setx
	    end_month_user = end_month_user + 1
	    if end_month_user > 12.0:
	        end_month_user = end_month_user - 12
	        end_year_user = end_year_user + 1
	    
	    if datetime(start_year_user,start_month_user,16) > datetime(start_year,start_month,16):
	        dates_user_a = rrule(MONTHLY,dtstart=datetime(start_year_user,start_month_user,16),until=datetime(end_year,end_month,16)) 
	        new_start = len(dates_complete[:]) - len(dates_user_a[:])
	    else:
	        new_start = 0
	    
	    if datetime(end_year_user,end_month_user,16) < datetime(end_year,end_month,16):
	        dates_user_b = rrule(MONTHLY,dtstart=datetime(start_year,start_month,16),until=datetime(end_year_user,end_month_user,16))
	        new_end = len(dates_user_b[:])
	    else:
	        new_end = len(dates_complete[:])
	    
	    dates = dates_complete[new_start:new_end]
	    timeseries = timeseries_complete[new_start:new_end]	
	
	else:
	    dates = dates_complete
	    timeseries = timeseries_complete
	
	# Alter maximum time values, if appropriate #
	
	if max_time < dates[-1]:
	    max_time = dates[-1]
	
	if min_time > dates[0]:
	    min_time = dates[0]
	
	# Alter the maximum y axis bounds, if appropriate #
	
	if count < file_list_dims[0]:
	    max_y_a,min_y_a = hi_lo(timeseries,max_y_a,min_y_a)	
	else:
	    max_y_b,min_y_b = hi_lo(timeseries,max_y_b,min_y_b)
	
	
	# Write the data to be plotted #
	
	#Convert the x values to floats
	dates_float = convert_datetime(dates)  
	
	xdata[ifile.fname] = dates_float
        ydata[ifile.fname] = timeseries

	count = count + 1 
	         
	
    # Define x ticks and labels #
    
    xaxis_full_datetime = rrule(MONTHLY,dtstart=min_time,until=max_time)
    xaxis_full_float = convert_datetime(xaxis_full_datetime)
    len_xaxis = len(xaxis_full_datetime[:])
        
    minor_xticks = []
    major_xticks = []
    major_xlabels = []
    for i in range(0,len_xaxis):
        value = xaxis_full_float[i]
        test = math.floor(value) / value
	if test == 1.0:
	    major_xticks.append(value)
	    major_xlabels.append(int(xaxis_full_datetime[i].year))
	else:
	    minor_xticks.append(value)
	    

    # Define the range of the y axis #
    
    if setyp:
        ybounds['min','a'] = setyp[0]
	ybounds['max','a'] = setyp[1]
    else:
        y_maximum_a = max(abs(max_y_a),abs(min_y_a))
        y_buffer_a = (2 * y_maximum_a) * 0.03
  	
	ybounds['min','a'] = -y_maximum_a - y_buffer_a
	ybounds['max','a'] = y_maximum_a + ybuffer*y_buffer_a
    
    if file_list_dims[1] > 0:
	if setys:
	    ybounds['min','b'] = setys[0]
	    ybounds['max','b'] = setys[1]
	else:
	    y_maximum_b = max(abs(max_y_b),abs(min_y_b))
            y_buffer_b = (2 * y_maximum_b) * 0.03 
            
	    ybounds['min','b'] = -y_maximum_b - y_buffer_b
	    ybounds['max','b'] = y_maximum_b + ybuffer*y_buffer_b
   

    return xdata,ydata,ybounds,major_xticks,minor_xticks,major_xlabels
    
    
def generate_plot(file_list,file_list_dims,xdata,ydata,ybounds,major_xticks,minor_xticks,major_xlabels,outfile_name,legloc,nrows):
    """Creates the plot"""
    
    fig = plt.figure()
       
    units_text='temp'
    for ifile in file_list:
        count = 0
	for row in range(nrows,0,-1):
	    #if count < file_list_dims[0]:

            pnum = row  #plot number

	    #initialise plot
	    ax = fig.add_subplot(nrows,1,pnum)  # rows, columns, plot number

## TRICKY BIT 2: twin axes
#	    if file_list_dims[1] > 0:
#        	ax1b = ax1a.twinx()
#
#	    if nrows > 1:
#        	ax2a = fig.add_subplot(nrows,1,2,sharey=ax1a)  
#        	if file_list_dims[1] > 0:
#        	    ax2b = ax2a.twinx()
#
#	    if nrows > 2:
#        	ax3a = fig.add_subplot(nrows,1,3,sharey=ax1a)
#        	if file_list_dims[1] > 0:
#        	    ax3b = ax3a.twinx()

## TRICKY BIT 1: PUT THE TIMESERIES IN THE FULL X-AXIS (i.e. there will be missing values) 
##               BEFORE SLICING IT UP FOR MULTIPLE ROWS
#            elif nrows == 2:
#	        xlen = math.floor(len(dates)/2)
#		xdata[ifile.fname,1,'a'] = dates_float[0:xlen]
#		xdata[ifile.fname,2,'a'] = dates_float[xlen:xlen*2]
#		ydata[ifile.fname,1,'a'] = timeseries[0:xlen]
#		ydata[ifile.fname,2,'a'] = timeseries[xlen:xlen*2]
#            elif nrows == 3:
#	        xlen = math.floor(len(dates)/3)
#		xdata[ifile.fname,1,'a'] = dates_float[0:xlen]
#		xdata[ifile.fname,2,'a'] = dates_float[xlen:xlen*2]
#		xdata[ifile.fname,3,'a'] = dates_float[xlen*2:xlen*3]
#		ydata[ifile.fname,1,'a'] = timeseries[0:xlen]
#		ydata[ifile.fname,2,'a'] = timeseries[xlen:xlen*2]
#		ydata[ifile.fname,3,'a'] = timeseries[xlen*2:xlen*3]


	    #plot data
	    label = ifile.index+', '+ifile.dataset
	    plot_date(numpy.array(xdata[ifile.fname,pnum,'a']),numpy.array(ydata[ifile.fname,pnum,'a']),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')

	    #plot extra guidelines
	    units_text = set_units(ifile.index,units_text,'Primary')

	    if units_text == 'Anomaly (deg C)':
        	axhline(y=0.5,linestyle='--',color='0.5')
        	axhline(y=-0.5,linestyle='--',color='0.5')
            
	    #axis limits
	    ax.set_ylim(ybounds['min','a'],ybounds['max','a'])
	    
	    #ticks
	    ax.set_ticks(major_xticks,minor=False)
	    ax.set_ticks(minor_xticks,minor=True)
	    ax.set_xticklabels(major_xlabels,minor=False,fontsize='medium')
	    
            #gridlines 
	    ax.grid(True,'major',color='0.5')
	    ax.grid(True,'minor',color='0.7')

	    #axis labels
	    #plt.setp(ax.get_xticklabels(), rotation=0, fontsize='medium') 
	    #ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize='medium')
	    ax.set_ylabel(units_text,fontsize='medium')  # rotation=270 for twin axis

	    #legend
	    font = font_manager.FontProperties(size='medium')
	    legend(loc=legloc,prop=font,ncol=2)
        
	count = count + 1
    
    # Output the figure #
    
    if outfile_name:
        plt.savefig(outfile_name)
    else:
        plt.show()


def main(primary_file_list,secondary_file_list,outfile_name,windowp,windows,setx,setyp,setys,ybuffer,legloc,nrows):
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
    
    ## Get all the setup details for the plot ##
        
    xdata,ydata,ybounds,major_xticks,minor_xticks,major_xlabels = setup_plot(file_list,file_list_dims,plot_data,plot_times,setx,setyp,setys,ybuffer)
    
    ## Generate the plot ##
    
    generate_plot(file_list,file_list_dims,xdata,ydata,ybounds,major_xticks,minor_xticks,major_xlabels,outfile_name,legloc,nrows)
    

if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-o", "--outfile",dest="outfile",type='str',default=None,help="Name of output file [default = None]")
    parser.add_option("-s", "--secondary",dest="secondary",default=None,help="Comma separated list files to be plotted on the secondary y axis [default = None]")
    parser.add_option("-l", "--legend",dest="legend",default=None,type='int',help="Location of the figure legend [defualt = None]")
    parser.add_option("-b", "--buffer",dest="buffer",type='float',default=1.0,help="Scale factor for y axis upper buffer [default = 4]")
    parser.add_option("-r", "--rows",dest="nrows",type='int',default=1,help="Number of rows (long time axes can be split onto numerous rows [default = 1]")
    parser.add_option("--wp",dest="windowp",type='int',default=1,help="Window for primary axis running average [default = 1]")
    parser.add_option("--ws",dest="windows",type='int',default=1,help="Window for secondary axis running average [default = 1]")
    parser.add_option("-x", "--setx",dest="setx",default=None,nargs=4,type='int',help="Time axis bounds (start_year start_month end_year end_month) [default = None]")
    parser.add_option("--setyp",dest="setyp",default=None,nargs=2,type='float',help="Primary y axis bounds (min max) [default = None]")
    parser.add_option("--setys",dest="setys",default=None,nargs=2,type='float',help="Secondary y axis bounds (min max) [default = None]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            python plot_climate_index.py [-h] [options] {input file 1} {input file 2} ... {input file N}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    -o  ->  Name of the output file [default = None = image is just shown instead]
	    -l  ->  Location of the legend [default = None]
	    -b  ->  Scale factor for y axis upper buffer [default = 1]
	    -r  ->  Number of rows (long time axes can be split onto numerous rows [default = 1]
	    -s  ->  Comma separated list files to be plotted on the secondary y axis [default = None]
	    -x  ->  Time axis bounds (start_year start_month end_year end_month) [default = None]
            --wp  ->  Window for primary axis running average [default = 1]
	    --ws  ->  Window for secondary axis running average [default = 1]
	    --setyp  ->  Primary y axis bounds (min,max) [default = None]
	    --setys  ->  Secondary y axis bounds (min,max) [default = None]
	
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
	    None: no legend 
	
	Example
	    /opt/cdat/bin/cdat plot_climate_index.py --wp 5 /work/dbirving/processed/indices/data/ts_Merra_NINO34_monthly_native-ocean.txt
	    /work/dbirving/processed/indices/data/tos_ERSSTv3b_NINO34_monthly_native.txt
	    
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
	
	    
        primary_file_list = args[:]   

        main(primary_file_list,secondary_file_list,options.outfile,options.windowp,options.windows,
	options.setx,options.setyp,options.setys,options.buffer,options.legend,options.nrows)
    
