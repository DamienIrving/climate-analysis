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


pcolor_list = ['red','blue','green','yellow','orange']
scolor_list = ['purple','brown','aqua']


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
    for i in range(0,len(dates[:])):    # SLOW
        dates_float[i] = dates[i].year + ((dates[i].month - 1) / 12.0) 
    
    return dates_float
    
    
def setup_plot(file_list,file_list_dims,plot_data,plot_times,setx,setyp,setys,ybuffer):
    """Determines all the details for the plot (e.g. data, axis bounds, tick marks)"""

    ## Define the data and details of the plot setup ##
    
    ydata = {}
    xdata = {} 
    ybounds = {}
    
    # Plot the data for each dataset #

    count = 0
    max_time = datetime(1000,1,1)
    min_time = datetime(3000,12,31)
    min_y_a = 1e10
    max_y_a = -1e10
    min_y_b = 1e10
    max_y_b = -1e10
    
    for ifile in file_list:

	# Intialise year and month variables #

	start_year,start_month,end_year,end_month = plot_times[ifile.fname]

        # Subset the data along the time axis if neceassry, according to user defined time bounds #

        timeseries_complete = plot_data[ifile.fname] #read in timeseries data
	dates_complete = rrule(MONTHLY,dtstart=datetime(start_year,start_month,16),until=datetime(end_year,end_month,16))
	
	if setx:
	    start_year_user,start_month_user,end_year_user,end_month_user = setx
	    
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
	         
	
    # Define the full x axis #
    
    xaxis_full_datetime = rrule(MONTHLY,dtstart=min_time,until=max_time)	    
    xaxis_full_float = convert_datetime(xaxis_full_datetime)

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
   

    return xdata,ydata,ybounds,xaxis_full_float


def split_nrows(indata,nrows):
    """Splits a give array according to the number of rows"""

    outdata = {}

    if nrows == 1:
        outdata[1] = indata	
    elif nrows == 2:
	axlen = math.floor(len(indata)/2)
	outdata[1] = indata[0:axlen]
	outdata[2] = indata[axlen:axlen*2]
    elif nrows == 3:
	axlen = math.floor(len(indata)/3)
	outdata[1] = indata[0:axlen]
	outdata[2] = indata[axlen:axlen*2]
	outdata[3] = indata[axlen*2:axlen*3]

    return outdata


def split_data(xaxis_full_float,xdata,ydata,nrows):
    """Splits up the data according to the number of rows"""
    
    #initialise output y data array	
    ydata_full = numpy.ones(len(xaxis_full_float)) * 1.e20
    
    #find location of the first time point
    start_loc = numpy.int(numpy.where(xaxis_full_float==xdata[0])[0])
    
    #drop original y data into ydata_full
    end_loc = start_loc + len(ydata)
    ydata_full[start_loc:end_loc] = ydata
    
    #apply the mask
    ydata_full = ma.masked_values(ydata_full,1.e20)

    #split as necessary
    xplot = split_nrows(xaxis_full_float,nrows)
    yplot = split_nrows(ydata_full,nrows)
    
    return xplot,yplot


def myroundup(x, base=10):
    return int(base * math.ceil(float(x)/base))


def get_xticks(xdata):
    """Determines the x axis ticks and labels"""
    
    # Determine the interval between major and minor ticks #
    
    len_xdata = len(xdata)
    major_interval = (myroundup(len_xdata/12)) / 10
    if major_interval == 1:
        minor_interval = (1.0/12.0)
    elif major_interval == 2:
        minor_interval = 0.5
    else:
        minor_interval = (myroundup(major_interval,base=4)) / 4
        
    # Determine the actual tick locations and values #
    	
    test_major = xdata % major_interval
    test_minor = xdata % minor_interval
     
    major_xticks = numpy.where(test_major == 0, xdata, 0)
    minor_xticks = numpy.where(test_minor < 0.0000001, xdata, 0)
    minor_xticks = numpy.where(major_xticks != 0, 0, minor_xticks)
    
    major_xticks = major_xticks[major_xticks != 0]
    major_xlabels = major_xticks.astype(int)
    minor_xticks = minor_xticks[minor_xticks != 0]

    return minor_xticks,major_xticks,major_xlabels
    
    
def generate_plot(primary_file_list,secondary_file_list,xdata,ydata,ybounds,xaxis_full_float,outfile_name,leglocp,leglocs,nrows):
    """Creates the plot"""
    
    #initialise figure
    fig = plt.figure()
       
    units_text='temp'
    units_text2='temp'
    if secondary_file_list:
        len_sec = len(secondary_file_list)
    else:
        len_sec = 0
    count = 0
    for pfile in primary_file_list:
	
	#split data according to nrows
	xplot,yplot = split_data(xaxis_full_float,xdata[pfile.fname],ydata[pfile.fname],nrows)
	
	if count < len_sec:
	    sfile = secondary_file_list[count]
	    xplot2,yplot2 = split_data(xaxis_full_float,xdata[sfile.fname],ydata[sfile.fname],nrows)
	    
	for row in range(0,nrows):

            pnum = row + 1

	    #initialise plot
	    ax = fig.add_subplot(nrows,1,pnum)  # rows, columns, plot number
            
	    if count < len_sec:
	        ax2 = ax.twinx()
		sfile = secondary_file_list[count]
		
	    #plot data
	    label = pfile.index+', '+pfile.dataset
	    ax.plot_date(numpy.ma.array(xplot[pnum]),numpy.ma.array(yplot[pnum]),color=pcolor_list[count],lw=2.0,label=label,linestyle='-',marker='None')
	    
	    if count < len_sec:
	        label = sfile.index+', '+sfile.dataset
	        ax2.plot_date(numpy.ma.array(xplot2[pnum]),numpy.ma.array(yplot2[pnum]),color=scolor_list[count],lw=2.0,label=label,linestyle='-',marker='None')
		
	    #plot extra guidelines
	    units_text = set_units(pfile.index,units_text,'Primary')

            if count < len_sec:
	        units_text2 = set_units(sfile.index,units_text2,'Secondary')

	    if units_text == 'Anomaly (deg C)' or units_text2 == 'Anomaly (deg C)':
        	ax.axhline(y=0.5,linestyle='--',color='0.5')
        	ax.axhline(y=-0.5,linestyle='--',color='0.5')
            
	    #axis limits
	    ax.set_ylim(ybounds['min','a'],ybounds['max','a'])
	    if count < len_sec:
	        ax2.set_ylim(ybounds['min','b'],ybounds['max','b'])
	    
	    #xticks
	    minor_xticks,major_xticks,major_xlabels = get_xticks(xplot[pnum])
	    
	    ax.set_xticks(major_xticks,minor=False)
	    ax.set_xticks(minor_xticks,minor=True)
	    ax.set_xticklabels(major_xlabels,minor=False,fontsize='medium')
	    
            #gridlines 
	    if secondary_file_list == None:
	        ax.grid(True,'major',color='0.2')
	        ax.grid(True,'minor',color='0.6')
	    else:
	        ax.axhline(y=0,linestyle='-',color='0.5')

	    #axis labels
	    ax.set_ylabel(units_text,fontsize='medium')
            
	    if count < len_sec:
	        ax2.set_ylabel(units_text2,fontsize='medium',rotation=270)

	    #legend
	    font = font_manager.FontProperties(size='medium')
	    if leglocp:
	        ax.legend(loc=leglocp,prop=font,ncol=2)
	    
	    if count < len_sec and leglocs:
                ax2.legend(loc=leglocs,prop=font,ncol=2) 
	
	count = count + 1
    
    # Output the figure #
    
    if outfile_name:
        plt.savefig(outfile_name)
    else:
        plt.show()


def main(primary_file_list,secondary_file_list,outfile_name,windowp,windows,setx,setyp,setys,ybuffer,leglocp,leglocs,nrows):
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
        
    xdata,ydata,ybounds,xaxis_full_float = setup_plot(file_list,file_list_dims,plot_data,plot_times,setx,setyp,setys,ybuffer)
    
    ## Generate the plot ##
    
    generate_plot(primary_file_list,secondary_file_list,xdata,ydata,ybounds,xaxis_full_float,outfile_name,leglocp,leglocs,nrows)
    

if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-o", "--outfile",dest="outfile",type='str',default=None,help="Name of output file [default = None]")
    parser.add_option("-s", "--secondary",dest="secondary",default=None,help="Comma separated list files to be plotted on the secondary y axis [default = None]")
    parser.add_option("-b", "--buffer",dest="buffer",type='float',default=1.0,help="Scale factor for y axis upper buffer [default = 4]")
    parser.add_option("-r", "--rows",dest="nrows",type='int',default=1,help="Number of rows (long time axes can be split onto numerous rows [default = 1]")
    parser.add_option("-x", "--setx",dest="setx",default=None,nargs=4,type='int',help="Time axis bounds (start_year start_month end_year end_month) [default = None]")
    parser.add_option("--lp",dest="legendp",default=None,type='int',help="Location of the primary figure legend [defualt = None]")
    parser.add_option("--ls",dest="legends",default=None,type='int',help="Location of the secondary figure legend [defualt = None]")
    parser.add_option("--wp",dest="windowp",type='int',default=1,help="Window for primary axis running average [default = 1]")
    parser.add_option("--ws",dest="windows",type='int',default=1,help="Window for secondary axis running average [default = 1]")
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
	    -b  ->  Scale factor for y axis upper buffer [default = 1]
	    -r  ->  Number of rows (long time axes can be split onto numerous rows [default = 1]
	    -s  ->  Comma separated list files to be plotted on the secondary y axis [default = None]
	    -x  ->  Time axis bounds (start_year start_month end_year end_month) [default = None]
	    --lp  ->  Location of the primary legend [default = None]
	    --ls  ->  Location of the secondary legend [default = None]
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
            Damien Irving, 22 Jun 2012
	    
	Note
	    The number of primary files must be greater or equal to the number of secondary files
	    
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
	options.setx,options.setyp,options.setys,options.buffer,options.legendp,options.legends,options.nrows)
    
