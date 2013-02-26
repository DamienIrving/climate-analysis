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

"""

import os
import sys

import argparse

import cdms2 
import genutil

import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from matplotlib import dates
from pylab import *

import datetime
from dateutil.rrule import *  # it seems to not work unless you import *
#from dateutil.relativedelta import *

import numpy
import numpy.ma as ma
import math

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def round_datetime(dt, freq):
    """Strip information of out datetime instance that is 
    less than the time frequency/resolution."""
    
    freq_list = ['YEARLY', 'MONTHLY', 'WEEKLY', 
                 'DAILY', 'HOURLY', 'MINUTELY', 
		 'SECONDLY']
    
    assert isinstance(dt, datetime.datetime)
    assert freq in freq_list 
    
    year = dt.year
    month = dt.month if eval('dates.'+freq) >= dates.MONTHLY else 1
    day = dt.day if freq_rank >= 2 else 1
    hour = dt.hour if freq_rank >= 4 else 0
    minute = dt.minute if freq_rank >= 5 else 0
    second = dt.second if freq_rank >= 6 else 0
    
    return datetime.datetime(year, month, day, hour, minute, second)
    

def set_datetime_axis(all_files, time_freq, nrows=1, xmax=datetime.datetime.max, 
                                                     xmin=datetime.datetime.min):
    """Return the datetime axis.

    Positional arguments:
      all_files  --  dict netcdf_io.InputData instances as values
      time_freq  --  datetime axis frequency
                     can be: 'YEARLY', 'MONTHLY', 'WEEKLY', 
                             'DAILY', 'HOURLY', 'MINUTELY',
                             'SECONDLY'

    Keyword arguments:
      xmax, xmin --  user supplied max and min bounds on datetime axis 

    """
    
    for item in all_files.values():
        assert isinstance(item, nio.InputData)
    
    assert time_freq in ['YEARLY', 'MONTHLY', 'WEEKLY', 
                         'DAILY', 'HOURLY', 'MINUTELY', 'SECONDLY']
    assert isinstance(xmax, datetime.datetime)
    assert isinstance(xmin, datetime.datetime)

    # Find highest and lowest datetimes from the input file #

    max_datetime = datetime.datetime.min
    min_datetime = datetime.datetime.max
    for item in all_files.values():
        max_datetime, min_datetime = nio.hi_lo(item.datetime_axis(), max_datetime, min_datetime)

    # Check against the user defined upper and lower bounds #

    max_datetime = xmax if xmax < max_datetime else max_datetime
    min_datetime = xmin if xmin > min_datetime else min_datetime
      
    # Create the x-axis #

    min_datetime = round_datetime(min_datetime, time_freq)
    max_datetime = round_datetime(max_datetime, time_freq)
    xaxis = rrule(eval(time_freq), dtstart=min_datetime ,until=max_datetime)
    
    # Adjust the xaxis so it's length is divisible by the number of rows

    while (xaxis.count() % nrows) != 0:
        xaxis = rrule(eval(time_freq), count=(xaxis.count() + 1), dtstart=min_datetime)    
        
    return xaxis


def split_nrows(indata, nrows):
    """Split a given array according to the number of rows"""

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


def redo_to_datetime(all_files, datetime_axis, time_freq, nrows=1):
    """Reconfigure the yaxis data so that it matches the desired xaxis
    and number of rows (i.e. crop or insert missing values as necessary)."""

    new_ydata = {}
    for key, value in all_files.iteritems():
        
	assert isinstance(value, nio.InputData)
	
	# Convert original xaxis to datetime objects #
	
	orig_dtaxis = value.datetime_axis()
	orig_start = round_datetime(orig_dtaxis[0], time_freq)
	orig_len = len(orig_dtaxis)
	dtaxis = rrule(eval(time_freq), count=len(orig_dtaxis), dtstart=orig_start) 
	
	# Check the start point of original xaxis against the new datetime_axis #
	
	new_ydata[key] = value.data[:]
	
        if dtaxis[0] in datetime_axis[:]:
	    index = datetime_axis[:].index(dtaxis[0])
	    new_ydata[key] = new_ydata[index:]
	else:
	    nfill = rrule(eval(time_freq), dtstart=datetime_axis[0], until=dtaxis[0]).count()
	    for i in xrange(nfill):
	        new_ydata[key] = numpy.insert(new_ydata, 0, 1.e20)
		 
        # Check the end point of original xaxis against the new datetime_axis #
	
        if dtaxis[-1] in datetime_axis[:]:
            nfill = rrule(eval(time_freq), dtstart=dtaxis[-1], until=datetime_axis[-1]).count()
	    for i in xrange(nfill):
	        new_ydata[key] = numpy.append(new_ydata, 1.e20)
        else:
	    index = datetime_axis[:].index(dtaxis[-1])
	    new_ydata[key] = new_ydata[:index+1]

        new_ydata[key] = split_nrows(numpy.ma.masked_values(new_ydata[key], 1.e20), nrows)


    return new_ydata


def myroundup(x, base=10):
    return int(base * math.ceil(float(x)/base))

 
def generate_plot(xaxis, yaxis_data, yaxis_error, file_order, freq,
                  nrows=1,
                  secondary=None,
                  ypbounds=None, ysbounds=None,
                  outfile_name=None,
		  ploc=None, sloc=None, legsize='medium',
                  phguide=None, pvguide=None, shguide=None, svguide=None,
		  colors=['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'brown','aqua'],
		  pline='-', sline='--',
		  nrows=1,
		  title=''): 
    """Create timeseries plot.
    
    """
    
    # Initialise figure #
    
    fig = plt.figure()
       
    units_text='temp'
    units_text2='temp'
    
    # Prepare the xaxis #

    xaxis_data = split_nrows(dates.date2num(datetime_axis), nrows)
    locators = {'YEARLY': [dates.YearLocator, '%m/%d %H:%M'],
                'MONTHLY': [dates.MonthLocator, '%m/%d %H:%M'],
                'WEEKLY': [dates.MonthLocator, '%m/%d %H:%M'],
                'DAILY': [dates.DayLocator, '%m/%d %H:%M'],
                'HOURLY': [dates.HourLocator, '%m/%d %H:%M'],
                'MINUTELY': [dates.MinuteLocator, '%m/%d %H:%M'],
                'SECONDLY': [dates.SecondLocator, '%m/%d %H:%M']}

    # Make the plot #
    
    for row in range(0, nrows):

        pnum = row + 1

	#initialise plot
	ax = fig.add_subplot(nrows, 1, pnum)  # rows, columns, plot number
 
	if secondary:
	    ax2 = ax.twinx()

	#plot data	
	count = 0
	for key in file_order:
	    label = yaxis_data[key].tag
            axis, linestyle = ax, linep if yaxis_data[key].set == 'primary' else ax2, lines
	    axis.plot(numpy.ma.array(xaxis_data[pnum]), numpy.ma.array(yaxis_data[key][pnum]), 
                      color=colors[count], lw=2.0, label=label, linestyle=linestyle, marker='None')
	    if key in yaxis_error.keys():
		upper = numpy.ma.array(yaxis_data[key][pnum]) + 2*numpy.ma.array(yaxis_error[key][pnum])   ## should use the numpy.ma addition tool
		lower = numpy.ma.array(yaxis_data[key][pnum]) - 2*numpy.ma.array(yaxis_error[key][pnum])
		axis.plot(numpy.ma.array(xaxis_data[pnum]), upper, color=colors[count], lw=0.5)
        	axis.plot(numpy.ma.array(xaxis_data[pnum]), lower, color=colors[count], lw=0.5)
        	axis.fill_between(numpy.ma.array(xaxis_data[pnum]), upper, lower, facecolor=colors[count], alpha=0.4)
            count = count + 1
	    

	if units_text == 'Anomaly (deg C)' or units_text2 == 'Anomaly (deg C)':
            ax.axhline(y=0.5,linestyle='--',color='0.5')
            ax.axhline(y=-0.5,linestyle='--',color='0.5')

	#axis limits
	ax.set_ylim(ybounds['min','a'],ybounds['max','a'])
	if secondary_file_list:
	    ax2.set_ylim(ybounds['min','b'],ybounds['max','b'])

	ax.set_xlim(xplot[primary_file_list[0].fname][pnum][0],xplot[primary_file_list[0].fname][pnum][-1])
	if secondary_file_list:
	    ax2.set_xlim(xplot[secondary_file_list[0].fname][pnum][0],xplot[secondary_file_list[0].fname][pnum][-1])

	#xticks
	ax.xaxis.set_major_locator(locators[freq][0])
        ax.xaxis.set_major_formatter(locators[freq][0])

	ax.set_xticks(major_xticks,minor=False)
	ax.set_xticks(minor_xticks,minor=True)
	ax.set_xticklabels(major_xlabels,minor=False,fontsize='medium')

        #gridlines 
	if not secondary:
	    ax.grid(True,'major',color='0.2')
	    ax.grid(True,'minor',color='0.6')
	else:
	    ax.axhline(y=0,linestyle='-',color='0.5')

	#axis labels
	ax.set_ylabel(plabel, fontsize='medium')

	if secondary:
	    ax2.set_ylabel(slabel, fontsize='medium', rotation=270)

	#legend

	if row == (nrows-1): 	   
	    font = font_manager.FontProperties(size=legsize)
	    if leglocp:
		ax.legend(loc=leglocp,prop=font,ncol=2)

	    if leglocs:
		ax2.legend(loc=leglocs,prop=font,ncol=2)

	#title
	if title and pnum == 1:
	    ax.set_title(title.replace('_',' ')) 

    count = count + 1
    
    # Output the figure #
    
    if outfile_name:
        plt.savefig(outfile_name)
    else:
        plt.show()


def sort_files(file_list, set_name):
    """Place input files into dict.

    positional arguments:
      file_list -- list of 
      set_name  -- can be primary or secondary

    """
    
    out_dict = {}
    order = []
    
    if file_list:
	for item in file_list:
            key = item[0:2]
            window = int(item[3])
            out_dict[key] = nio.InputData(item[0], item[1], runave=window)
            out_dict[key].tag = item[2]
            out_dict[key].window = window
            out_dict[key].set = set_name
            order.append(key)         
    else:
        outdict = None
	order = None

    return out_dict, order


def main(inargs):
    """Run the program"""
    
    # Sort files - unique identifier is the filename, variable pair #

    primary_dict, primary_order = sort_files(inargs.primary, 'primary')
    secondary_dict, secondary_order = sort_files(inargs.secondary, 'secondary')
    
    allfile_dict = dict(primary_dict.items() + secondary_dict.items()) if secondary_dict else primary_dict
    allfile_order = (primary_order + secondary_order) if secondary_dict else primary_order

    if inargs.error:
        error_dict = {}
	for item in inargs.error:
            key = item[2:4]
            error_dict[key] = nio.InputData(item[0], item[1], runave=allfile_dict[key].window)
    else:
        error_dict = None

    ### FROM HERE DOWN COULD ALL GO IN GENERATE PLOT ##

    # Set the x (datetime) axis #
     
    xaxis = set_datetime_axis(allfile_dict, inargs.freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(set_datetime_axis)))   
    
    # Reconfigure the data to be plotted, so that it is consistent with the new x axis #

    yaxis_data = redo_to_datetime(allfile_dict, xaxis, inargs.freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(redo_to_datetime)))
    yaxis_error = redo_to_datetime(error_dict, xaxis, inargs.freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(redo_to_datetime))) if error_dict else None

    # Generate the plot #
    
    generate_plot(xaxis, yaxis_data, yaxis_error, allfile_order, secondary=secondary_order, **nio.dict_filter(vars(inargs), nio.list_kwargs(generate_plot)))


if __name__ == '__main__':

    extra_info = """   
legend options:
  location:   1 upper right, 2 upper left, 3 lower left, 4 lower_right, 5 right, 6 center left, 
	      7 center right, 8 lower center, 9 upper center, 10 center, None no legend 

examples (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_climate_index.py
  /work/dbirving/processed/indices/data/ts_Merra_surface_NINO34_monthly_native-ocean.nc nino34 Nino34 1
  
  /opt/cdat/bin/cdat plot_climate_index.py 
  /work/dbirving/processed/indices/data/ts_Merra_surface_EOF1_monthly_native-ocean-eqpacific.txt 
  /work/dbirving/processed/indices/data/ts_Merra_surface_EOF2_monthly_native-ocean-eqpacific.txt 
  -s /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF1_monthly_native-eqpacific.txt,
  /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF2_monthly_native-eqpacific.txt 
  -r 3 --wp 5 --ws 5 --lp 2 --ls 1

note:
  The expected measure of error is the standard deviation (twice the standard deviation either side
  of the central estimate is plotted).

improvements:
  The ability to plot seasonal timescale data (e.g. like 3 or 6 month season) could be achieved by
  simply using the interval keyword argument for the rrule method.

"""

    description='Plot timeseries data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("freq", type=str, choices=['YEARLY', 'MONTHLY', 'WEEKLY', 
                        'DAILY', 'HOURLY', 'MINUTELY', 'SECONDLY'],
                        help="Time frequency of the plot")	
    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("tag", type=str, help="Input file tag (or label)")
    parser.add_argument("window", type=str, help="Input file running average window - can be 1 for no smoothing")
				     
    parser.add_argument("--primary", type=str, action='append', default=[], nargs=4,
                        metavar=('FILENAME', 'VAR', 'TAG', 'WINDOW'),  
                        help="Additional primary file name, variable, tag and running average window [default: None]")
    parser.add_argument("--secondary", type=str, action='append', default=None, nargs=4, 
                        metavar=('FILENAME', 'VAR', 'TAG', 'WINDOW'),
                        help="Secondary file name, variable, tag and running average window [default: None]")
    parser.add_argument("--error", type=str, action='append', default=None, nargs=4,
                        metavar=('FILENAME', 'VAR', 'PARENT_FILE_NAME', 'PARENT_VAR'),
                        help="Error file name, variable, parent file name, parent variable [default: None]")
    parser.add_argument("--outfile", type=str, default=None,
                        help="Name of output file [default: None]")
    parser.add_argument("--buffer", type=float,
                        help="Scale factor for y axis upper buffer")
    parser.add_argument("--nrows", type=int, default=1,
                        help="Number of rows (long time axes can be split onto numerous rows [default: %(default)s]")
    parser.add_argument("--xmax", type=str, metavar=('DATE'),
                        help="Maximum time axis value [default: auto]")
    parser.add_argument("--xmin", type=str, metavar=('DATE'),
                        help="Minimum time axis value [default: auto]")
    parser.add_argument("--ploc", type=int, default=None, 
                        help="Location of the primary figure legend [defualt: no legend]")
    parser.add_argument("--sloc", type=int, default=None, 
                        help="Location of the secondary figure legend [defualt: non legend]")
    parser.add_argument("--legsize", type=str, 
                        choices=['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'],
                        help="Size of the legend text [default: medium]")
    parser.add_argument("--colors", type=str, nargs='*',
                        help="Colors for each plot [default: auto]")
    parser.add_argument("--pline", type=str, choices=['-', '--', '-.', ':'],
                        help="Line style for the primary plot [default: solid]")
    parser.add_argument("--sline", type=str, choices=['-', '--', '-.', ':'],
                        help="Line style for the secondary plot [default: dashed]")
    parser.add_argument("--ypbounds", type=float, nargs=2, metavar=('MIN', 'MAX'),
                        help="Primary y axis bounds [default: auto]")
    parser.add_argument("--ysbounds", type=float, nargs=2, metavar=('MIN', 'MAX'),
                        help="Secondary y axis bounds [default: auto]")
    parser.add_argument("--title", type=str, 
                        help="Title for plot [default: None]")
    parser.add_argument("--ylabel", type=str, 
                        help="y axis label [default: None]")
    parser.add_argument("--xlabel", type=str, 
                        help="x axis label [default: None]")    

phguide
shguide
pvguide
svguide

    args = parser.parse_args()  

    args.primary.insert(0, (args.infile, args.variable, args.tag, args.window))

    main(args)
    
