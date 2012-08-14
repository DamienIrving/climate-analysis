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

    
def create_plot(file_list,file_list_dims,plot_data,plot_times,windowp,windows,outfile_name,setx,setyp,setys,ybuffer,legloc,nrows):
    """Creates the plot"""

    # Start the figure #
    
    plt.figure()
    ax1a = plt.subplot(nrows,1,1)  # rows, columns, plot number
    if file_list_dims[1] > 0:
        ax1b = ax1a.twinx()
    
    if nrows > 1:
        ax2a = plt.subplot(nrows,1,2,sharey=ax1a)  
        if file_list_dims[1] > 0:
            ax2b = ax2a.twinx()
    
    if nrows > 2:
        ax3a = plt.subplot(nrows,1,3,sharey=ax1a)
        if file_list_dims[1] > 0:
            ax3b = ax3a.twinx()
        
    # Set the title and units #   

    title_text = 'Climate indices'  ### FIX TO ACCOUNT FOR SECOND PLOT
    
    
    # Plot the data for each dataset #

    count = 0
    units_text_ax1a = 'temp'
    units_text_ax1b = 'temp'
    min_year = 1e10
    max_year = -1e10
    min_time = 1e10
    max_time = -1e10
    min_y_ax1a = 1e10
    max_y_ax1a = -1e10
    min_y_ax1b = 1e10
    max_y_ax1b = -1e10
    
    for ifile in file_list:

	# Intialise year and month variables #

	start_year,start_month,end_year,end_month = plot_times[ifile.fname]

	end_month = end_month + 1
	if end_month > 12.0:
	    end_month = end_month - 12
	    end_year = end_year + 1

        # Create time values and subset data if necessary #

        timeseries_complete = plot_data[ifile.fname] #read in timeseries data

	date1 = datetime.date( int(start_year), int(start_month), 16 )
	date2 = datetime.date( int(end_year), int(end_month), 16 )
	delta = datetime.timedelta(minutes=43830)   # timedelta doesn't take monnths. For a 365.25 day year, the average month length is 43830 minutes 
        
	dates_complete = drange(date1, date2, delta)
	
	if setx:
	    start_year,start_month,end_year,end_month = setx
	    end_month = end_month + 1
	    if end_month > 12.0:
	        end_month = end_month - 12
	        end_year = end_year + 1
	    
	    date1_user = datetime.date( setx[0], setx[1], 16 ) 
            date2_user = datetime.date( setx[2], setx[3], 16 )
	    
	    new_start = len(dates_complete) - len(drange(date1_user,date2,delta))
	    new_end = len(drange(date1,date2_user,delta))
	    
	    dates = dates_complete[new_start:new_end]
	    timeseries = timeseries_complete[new_start:new_end]	
	
	else:
	    dates = dates_complete
	    timeseries = timeseries_complete
	    
	    
	max_time,min_time = hi_lo(dates,max_time,min_time)
	max_year,min_year = hi_lo(range(int(start_year),int(end_year)+1),max_year,min_year) 

        # Plot the data #
        
	label = ifile.index+', '+ifile.dataset
	if count < file_list_dims[0]:
	    units_text_ax1a = set_units(ifile.index,units_text_ax1a,'Primary')
	    max_y_ax1a,min_y_ax1a = hi_lo(timeseries,max_y_ax1a,min_y_ax1a)
	    
	    if nrows == 1:
	        ax1a.plot_date(dates,numpy.array(timeseries),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
	    elif nrows == 2:
	        xlen = math.floor(len(dates)/2)
		dates_1a = dates[0:xlen]
		dates_2a = dates[xlen:xlen*2]
		timeseries_1a = timeseries[0:xlen]
		timeseries_2a = timeseries[xlen:xlen*2]
		ax1a.plot_date(dates_1a,numpy.array(timeseries_1a),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		ax2a.plot_date(dates_2a,numpy.array(timeseries_2a),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
            elif nrows == 2:
	        xlen = math.floor(len(dates)/3)
		dates_1a = dates[0:xlen]
		dates_2a = dates[xlen:xlen*2]
		dates_3a = dates[xlen*2:xlen*3]
		timeseries_1a = timeseries[0:xlen]
		timeseries_2a = timeseries[xlen:xlen*2]
		timeseries_3a = timeseries[xlen*2:xlen*3]
		ax1a.plot_date(dates_1a,numpy.array(timeseries_1a),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		ax2a.plot_date(dates_2a,numpy.array(timeseries_2a),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		ax3a.plot_date(dates_3a,numpy.array(timeseries_3a),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')

	else:
	    units_text_ax1b = set_units(ifile.index,units_text_ax1b,'Secondary')
	    max_y_ax1b,min_y_ax1b = hi_lo(timeseries,max_y_ax1b,min_y_ax1b)
	
	    if nrows == 1:
	        ax1b.plot_date(dates,numpy.array(timeseries),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
	    elif nrows == 2:
	        xlen = math.floor(len(dates)/2)
		dates_1b = dates[0:xlen]
		dates_2b = dates[xlen:xlen*2]
		timeseries_1b = timeseries[0:xlen]
		timeseries_2b = timeseries[xlen:xlen*2]
		ax1b.plot_date(dates_1b,numpy.array(timeseries_1b),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		ax2b.plot_date(dates_2b,numpy.array(timeseries_2b),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
            elif nrows == 2:
	        xlen = math.floor(len(dates)/3)
		dates_1b = dates[0:xlen]
		dates_2b = dates[xlen:xlen*2]
		dates_3b = dates[xlen*2:xlen*3]
		timeseries_1b = timeseries[0:xlen]
		timeseries_2b = timeseries[xlen:xlen*2]
		timeseries_3b = timeseries[xlen*2:xlen*3]
		ax1b.plot_date(dates_1b,numpy.array(timeseries_1b),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		ax2b.plot_date(dates_2b,numpy.array(timeseries_2b),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		ax3b.plot_date(dates_3b,numpy.array(timeseries_3b),color=color_list[count],lw=2.0,label=label,linestyle='-',marker='None')

	count = count + 1 
        del date1
	del date2
	del delta
        del dates         
  
    # Plot guidelines #
 
    #ax1a.axhline(y=0.0,linestyle='-',color='0.8')
    
    if units_text_ax1a == 'Anomaly (deg C)':
        ax1a.axhline(y=0.5,linestyle='--',color='0.5')
        ax1a.axhline(y=-0.5,linestyle='--',color='0.5')
        if nrows > 1:
	    ax2a.axhline(y=0.5,linestyle='--',color='0.5')
            ax2a.axhline(y=-0.5,linestyle='--',color='0.5')
	if nrows > 2:
	    ax3a.axhline(y=0.5,linestyle='--',color='0.5')
            ax3a.axhline(y=-0.5,linestyle='--',color='0.5')
	
    # Define labelling rules for the time axis #

    if setx:
        time_range = (setx[2] - setx[0]) / nrows
    else:
        time_range = (int(max_year) - int(min_year)) / nrows
    
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
    elif time_range < 50:
        rule_major = rrulewrapper(YEARLY, bymonth=1, interval=5)
	rule_minor = rrulewrapper(YEARLY, bymonth=1, interval=1)
	major_label = '%Y'
	minor_label = ''
    else:
        rule_major = rrulewrapper(YEARLY, bymonth=1, interval=20)
	rule_minor = rrulewrapper(YEARLY, bymonth=1, interval=5)
	major_label = '%Y'
	minor_label = ''
        
    loc_major = RRuleLocator(rule_major)
    formatter_major = DateFormatter(major_label)    # '%m/%d/%y' capital Y for 4-digit year and b or B for full month name

    loc_minor = RRuleLocator(rule_minor)
    formatter_minor = DateFormatter(minor_label)    # '%m/%d/%y'
 
    ax1a.xaxis.set_major_locator(loc_major)
    ax1a.xaxis.set_major_formatter(formatter_major)
    ax1a.xaxis.set_minor_locator(loc_minor)
    ax1a.xaxis.set_minor_formatter(formatter_minor)
    if nrows > 1:
        ax2a.xaxis.set_major_locator(loc_major)
        ax2a.xaxis.set_major_formatter(formatter_major)
        ax2a.xaxis.set_minor_locator(loc_minor)
        ax2a.xaxis.set_minor_formatter(formatter_minor)
    if nrows > 2:
        ax3a.xaxis.set_major_locator(loc_major)
        ax3a.xaxis.set_major_formatter(formatter_major)
        ax3a.xaxis.set_minor_locator(loc_minor)
        ax3a.xaxis.set_minor_formatter(formatter_minor)
    
    # Define the range of the y axis #
    
    x1a,x2a,y1a,y2a = ax1a.axis()
    if setyp:
        ax1a.axis([x1a,x2a,setyp[0],setyp[1]])
    else:
        y_maximum_ax1a = max(abs(max_y_ax1a),abs(min_y_ax1a))
        y_buffer_ax1a = (2 * y_maximum_ax1a) * 0.03
  	ax1a.axis([x1a,x2a,(-y_maximum_ax1a - y_buffer_ax1a),(y_maximum_ax1a + ybuffer*y_buffer_ax1a)])
    
    if file_list_dims[1] > 0:
	x1b,x2b,y1b,y2b = ax1b.axis()
	if setys:
	    ax1b.axis([x1b,x2b,setys[0],setys[1]])
	else:
	    y_maximum_ax1b = max(abs(max_y_ax1b),abs(min_y_ax1b))
            y_buffer_ax1b = (2 * y_maximum_ax1b) * 0.03 
            ax1b.axis([x1b,x2b,(-y_maximum_ax1b - y_buffer_ax1b),(y_maximum_ax1b + ybuffer*y_buffer_ax1b)])
   
    # Plot labels (including title, axis labels and legend) #

    #x axis labels
    #plt.axes(ax1a)
    labels_ax1a = ax1a.get_xticklabels()
    plt.setp(labels_ax1a, rotation=0, fontsize='medium')   
    if nrows > 1:
	labels_ax2a = ax2a.get_xticklabels()
        plt.setp(labels_ax2a, rotation=0, fontsize='medium')
    if nrows > 2:
	labels_ax3a = ax3a.get_xticklabels()
        plt.setp(labels_ax3a, rotation=0, fontsize='medium')

    #y axis labels - primary plot
    if nrows > 2:
        ax2a.set_ylabel(units_text_ax1a,fontsize='medium')
    elif nrows > 1:
        ax1a.set_ylabel(units_text_ax1a,fontsize='medium')
	ax2a.set_ylabel(units_text_ax1a,fontsize='medium')
    else:
        ax1a.set_ylabel(units_text_ax1a,fontsize='medium')
    
    #y axis labels - secondary plot
    if file_list_dims[1] > 0:
	if nrows > 2:
            ax2b.set_ylabel(units_text_ax1b,fontsize='medium',rotation=270)
	elif nrows > 1:
            ax1b.set_ylabel(units_text_ax1b,fontsize='medium',rotation=270)
	    ax2b.set_ylabel(units_text_ax1b,fontsize='medium',rotation=270)
	else:
            ax1b.set_ylabel(units_text_ax1b,fontsize='medium',rotation=270)
        
    #title
    ax1a.set_title(title_text)
    
    #legend - primary plot
    font = font_manager.FontProperties(size='medium')
    if legloc:
	if nrows > 2:
	    ax2a.legend(loc=legloc,prop=font,ncol=2) #prop=font,numpoints=1,labelspacing=0.3)  #,ncol=2)
	elif nrows > 1:
	    ax1a.legend(loc=legloc,prop=font,ncol=2)
	    ax2a.legend(loc=legloc,prop=font,ncol=2)
        else:
	    ax1a.legend(loc=legloc,prop=font,ncol=2)
    
        #legend - secondary plot
        if file_list_dims[1] > 0:
	    if nrows > 2:
		ax2b.legend(loc=1,prop=font)
	    elif nrows > 1:
		ax1b.legend(loc=1,prop=font)
		ax2b.legend(loc=1,prop=font)
            else:
		ax1b.legend(loc=1,prop=font)
    
    #gridlines
    ax1a.grid(True,'major',color='0.5')
    ax1a.grid(True,'minor',color='0.7')
    if nrows > 1:
        ax2a.grid(True,'major',color='0.5')
        ax2a.grid(True,'minor',color='0.7')
    if nrows > 2:
        ax3a.grid(True,'major',color='0.5')
        ax3a.grid(True,'minor',color='0.7')
    
    
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
    
    ## Create the plot ##
        
    create_plot(file_list,file_list_dims,plot_data,plot_times,windowp,windows,outfile_name,setx,setyp,setys,ybuffer,legloc,nrows)
    

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
    
