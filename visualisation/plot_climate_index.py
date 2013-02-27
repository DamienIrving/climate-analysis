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

import datetime
from dateutil.rrule import *  # it seems to not work unless you import *

import numpy
import numpy.ma as ma
import math

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def generate_plot(xaxis_data, major_xticks, major_xlabels, 
                  yaxis_data, yaxis_error, file_order, freq,
                  secplot=None,
                  ypbounds=None, ysbounds=None, ybuffer=0.1,
                  xlabel=None, plabel=None, slabel=None,
                  outfile=None,
		  ploc=None, sloc=None, legsize='medium',
                  phguide=None, shguide=None,
		  colors=['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'brown','aqua'],
		  pline='-', sline='--',
		  nrows=1,
		  title=''): 
    """Create timeseries plot.
    
    """
    
    # Initialise figure #
    
    fig = plt.figure()
    plt.subplots_adjust(wspace=0.5) # make a little extra space between the subplots
    
    # Make the plot #
    
    for row in range(0, nrows):

        pnum = row + 1

	#initialise plot
	ax = fig.add_subplot(nrows, 1, pnum)  # rows, columns, plot number
        if secplot:
	    ax2 = ax.twinx()

	#plot data	
	count = 0
	for key in file_order:
	    xdata = xaxis_data[pnum]
            ydata = numpy.ma.array(yaxis_data[key][0][pnum])
            label = yaxis_data[key][1]
            group = yaxis_data[key][2]
            (axis, linestyle) = (ax, pline) if group == 'primary' else (ax2, sline)
	    
            axis.plot(xdata, ydata, color=colors[count], lw=2.0, label=label, linestyle=linestyle, marker='None')
	    
            if yaxis_error and (key in yaxis_error.keys()):
		upper = ydata + 2*numpy.ma.array(yaxis_error[key][pnum])   ## should use the numpy.ma addition tool
		lower = ydata - 2*numpy.ma.array(yaxis_error[key][pnum])
		axis.plot(xdata, upper, color=colors[count], lw=0.5)
        	axis.plot(xdata, lower, color=colors[count], lw=0.5)
        	axis.fill_between(xdata, upper, lower, facecolor=colors[count], alpha=0.4)
            
            count = count + 1
	    
	#yaxis limits
	ax.set_ylim(ypbounds[0]*(1 + ybuffer), ypbounds[1]*(1 + ybuffer))
	if secplot:
	    ax2.set_ylim(ysbounds[0]*(1 + ybuffer), ysbounds[1]*(1 + ybuffer))

	#xticks
        ax.set_xlim(xaxis_data[pnum][0], xaxis_data[pnum][-1])
        ax.set_xticks(major_xticks[pnum], minor=False)
#        ax.set_xticks(minor_xticks, minor=True)
        ax.set_xticklabels(major_xlabels[pnum], minor=False, rotation=0, fontsize='small')

        #guidelines
	if phguide:
            for yval in phguide:
                ax.axhline(y=yval, linestyle='--', color='0.5') 
        if shguide:
            for yval in shguide:
                ax2.axhline(y=yval, linestyle='--', color='0.5')
        
        #gridlines 
	if not secplot:
	    ax.grid(True, 'major', color='0.2')
	    ax.grid(True, 'minor', color='0.6')
	else:
	    ax.axhline(y=0, linestyle='-', color='0.5')

	#axis labels
	ax.set_ylabel(plabel, fontsize='medium')
	if secplot:
	    ax2.set_ylabel(slabel, fontsize='medium', rotation=270)

	#legend
	if row == (nrows-1): 	   
	    font = font_manager.FontProperties(size=legsize)
	    if ploc:
		ax.legend(loc=ploc, prop=font, ncol=2)
            if sloc:
		ax2.legend(loc=sloc, prop=font, ncol=2)

	#title
	if title and pnum == 1:
	    ax.set_title(title.replace('_',' ')) 

        count = count + 1
    
    # Output the figure #
    
    if outfile:
        plt.savefig(outfile)
    else:
        print 'showing...'
        plt.show()


def get_xticks(xdata, freq, startint=None, majorint=None, nrows=1):
    """Determines the x axis ticks and labels.

    This function is necessary because matplotlib 
    locators, which would usually be used to automate
    this process, can't be shared among axes. The 
    set_major_locator() method assigns its axis to 
    that locator, overwriting any axis that was 
    previously assigned. This is problematic for 
    multi-panel plots.
    """
    
    # Split xdata according to the number of rows #
    
    xdata_dt_split = split_nrows(xdata[:], nrows)
    xdata_num_split = split_nrows(dates.date2num(xdata[:]), nrows)

    # Set major interval if not supplied #
        
    if not majorint: 
        majorint = myroundup(len(xdata_dt_split[1]) / 7.)    
    
    print 'major tick interval:', majorint   

    # Determine the ticks #
        
    if not startint:
        startint = 0
    tick_points = range(startint, len(xdata[:]), majorint)  

    formats  = {'YEARLY': '%Y',
                'MONTHLY': '%b %Y',
                'WEEKLY': '%d/%m/%y',
                'DAILY': '%d/%m/%y',
                'HOURLY': '%m/%d %H:%M',
                'MINUTELY': '%m/%d %H:%M',
                'SECONDLY': '%m/%d %H:%M'}

    major_xticks = {}
    major_xlabels = {}
    count = 0
    for row in range(1, nrows+1):
	xticks = []
	labels = []
	for index, dt in enumerate(xdata_dt_split[row]):
            place = index + count
            if place in tick_points:
        	xticks.append(dates.date2num(dt))
        	labels.append(dt.strftime(formats[freq]))      
        
        major_xticks[row] = xticks
        major_xlabels[row] = labels
        count = count + len(xdata_dt_split[row])

    return xdata_num_split, major_xticks, major_xlabels


def myroundup(x, base=1):
    return int(base * math.ceil(float(x)/base))


def redo_to_datetime(all_files, datetime_axis, time_freq, nrows=1):
    """Reconfigure the yaxis data so that it matches the desired xaxis
    and number of rows (i.e. crop or insert missing values as necessary)."""

    new_ydata = {}
    max_primary = max_secondary = float("-inf")
    min_primary = min_secondary = float("inf")
    for key, value in all_files.iteritems():
        
	assert isinstance(value, nio.InputData)
	
	# Convert original xaxis to datetime objects #
	
	orig_dtaxis = value.datetime_axis()
	orig_start = round_datetime(orig_dtaxis[0], time_freq)
	orig_len = len(orig_dtaxis)
	dtaxis = rrule(eval(time_freq), count=len(orig_dtaxis), dtstart=orig_start) 
	
	# Check the start point of original xaxis against the new datetime_axis #
	
	missval = value.data.missing_value
	ydata = value.data[:]
	
        if dtaxis[0] in datetime_axis[:]:
	    index = datetime_axis[:].index(dtaxis[0])
	    ydata = ydata[index:]
	else:
	    nfill = rrule(eval(time_freq), dtstart=datetime_axis[0], until=dtaxis[0]).count()
	    for i in xrange(nfill):
	        ydata = numpy.insert(ydata, 0, missval)
		 
        # Check the end point of original xaxis against the new datetime_axis #
	
        if dtaxis[-1] in datetime_axis[:]:
            nfill = rrule(eval(time_freq), dtstart=dtaxis[-1], until=datetime_axis[-1]).count() - 1
	    for i in xrange(nfill):
	        ydata = numpy.append(ydata, missval)
        else:
	    index = datetime_axis[:].index(dtaxis[-1])
	    ydata = ydata[:index+1]

        # Update the minimum and maximum value #

        ydata = numpy.ma.masked_values(ydata, missval)

        if value.set == 'primary':
            max_primary, min_primary = nio.hi_lo(ydata, max_primary, min_primary)
        elif value.set == 'secondary':
            max_secondary, min_secondary = nio.hi_lo(ydata, max_secondary, min_secondary)

        new_ydata[key] = [split_nrows(ydata, nrows), all_files[key].tag, all_files[key].set]
    
    primary_bounds = (max_primary, min_primary)
    secondary_bounds = None if max_secondary == float("inf") else (max_secondary, min_secondary)


    return new_ydata, primary_bounds, secondary_bounds 


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
    day = dt.day if eval('dates.'+freq) >= dates.WEEKLY else 1
    hour = dt.hour if eval('dates.'+freq) >= dates.HOURLY else 0
    minute = dt.minute if eval('dates.'+freq) >= dates.MINUTELY else 0
    second = dt.second if eval('dates.'+freq) >= dates.SECONDLY else 0
    
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


def split_nrows(indata, nrows):
    """Split a given array according to the number of rows"""

    outdata = {}

    if nrows == 1:
        outdata[1] = indata	
    elif nrows == 2:
	axlen = int(math.floor(len(indata)/2))
	outdata[1] = indata[0:axlen]
	outdata[2] = indata[axlen:axlen*2]
    elif nrows == 3:
	axlen = int(math.floor(len(indata)/3))
	outdata[1] = indata[0:axlen]
	outdata[2] = indata[axlen:axlen*2]
	outdata[3] = indata[axlen*2:axlen*3]

    return outdata


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
            error_dict[key].tag = None
            error_dict[key].set = 'error'
    else:
        error_dict = None

    # Set the x (datetime) axis #
     
    xaxis = set_datetime_axis(allfile_dict, inargs.freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(set_datetime_axis)))   
    
    # Reconfigure the data to be plotted, so that it is consistent with the new x axis #

    yaxis_data, pbounds, sbounds = redo_to_datetime(allfile_dict, xaxis, inargs.freq, 
                                                    **nio.dict_filter(vars(inargs), nio.list_kwargs(redo_to_datetime)))
    yaxis_error, epbounds, esbounds = redo_to_datetime(error_dict, xaxis, inargs.freq, 
                                      **nio.dict_filter(vars(inargs), nio.list_kwargs(redo_to_datetime))) if error_dict else (None, None, None)

    xaxis_data, major_xticks, minor_xlabels = get_xticks(xaxis, inargs.freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(get_xticks)))

    # Generate the plot #

    if not inargs.ypbounds:
        inargs.ypbounds = pbounds
   
    if not inargs.ysbounds:
        inargs.ysbounds = sbounds

    print vars(inargs)

    generate_plot(xaxis_data, major_xticks, minor_xlabels, yaxis_data, yaxis_error, allfile_order, inargs.freq, 
                  secplot=secondary_order, **nio.dict_filter(vars(inargs), nio.list_kwargs(generate_plot)))


if __name__ == '__main__':

    extra_info = """   
legend options:
  location:   1 upper right, 2 upper left, 3 lower left, 4 lower_right, 5 right, 6 center left, 
	      7 center right, 8 lower center, 9 upper center, 10 center, None no legend 

examples (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_climate_index.py MONTHLY
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
  Include the error shading in the automatic ybounds calculation
  Minor tick marks 

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
    parser.add_argument("--outfile", type=str,
                        help="Name of output file [default: None]")

    parser.add_argument("--nrows", type=int, default=1,
                        help="Number of rows (long time axes can be split onto numerous rows [default: %(default)s]")
    parser.add_argument("--title", type=str, 
                        help="Title for plot [default: None]")
    parser.add_argument("--ylabel", type=str, 
                        help="y axis label [default: None]")
    parser.add_argument("--xlabel", type=str, 
                        help="x axis label [default: None]")    

    parser.add_argument("--ypbounds", type=float, default=None, nargs=2, metavar=('MIN', 'MAX'),
                        help="Primary y axis bounds [default: auto]")
    parser.add_argument("--ysbounds", type=float, default=None, nargs=2, metavar=('MIN', 'MAX'),
                        help="Secondary y axis bounds [default: auto]")
    parser.add_argument("--ybuffer", type=float,
                        help="Scale factor for y axis upper buffer (i.e. expressed as a fraction)")
    parser.add_argument("--xmax", type=str, metavar=('DATE'),
                        help="Maximum time axis value [default: auto]")
    parser.add_argument("--xmin", type=str, metavar=('DATE'),
                        help="Minimum time axis value [default: auto]")
    parser.add_argument("--startint", type=int, 
                        help="Start index for the x-axis ticks [default: 0]")
    parser.add_argument("--majorint", type=int, 
                        help="Interval between x-axis labels")

    parser.add_argument("--ploc", type=int, 
                        help="Location of the primary figure legend [defualt: no legend]")
    parser.add_argument("--sloc", type=int, 
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

    parser.add_argument("--phguide", type=str, nargs='*',
                        help="Primary axis values for which a horizontal guideline should be plotted [default: None]")
    parser.add_argument("--shguide", type=str, nargs='*',
                        help="Secondary axis values for which a horizontal guideline should be plotted [default: None]")

    args = parser.parse_args()  

    args.primary.insert(0, (args.infile, args.variable, args.tag, args.window))

    main(args)
    
