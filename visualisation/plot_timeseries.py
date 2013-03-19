"""
Filename:     plot_timeseries.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots timeseries

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

Updates | By | Description
--------+----+------------
23 February 2012 | Damien Irving | Initial version.
28 February 2013 | Damien Irving | Generalised beyond monthly data.

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



class YaxisElement:    
    """Element to be plotted on yaxis."""

    def __init__(self, data, label, group):
	"""Define attributes."""
  
        self.data = data
        self.label = label
        self.group = group


class DatetimeAxis:
    """Datetime axis for a plot."""
    
    def __init__(self, dtdata, freq, nrows=1):
	"""Convert datetime values to numeric and split according to nrows."""
  
        assert isinstance(dtdata, (list, tuple))
        assert isinstance(dtdata[0], datetime.datetime)
        assert freq in ['YEARLY', 'MONTHLY', 'WEEKLY', 
                        'DAILY', 'HOURLY', 'MINUTELY', 
		        'SECONDLY']

        self.data_orig = dtdata
        self.data_dt = split_nrows(dtdata[:], nrows)
        self.data_numeric = split_nrows(dates.date2num(dtdata[:]), nrows)
        self.freq = freq
        self.nrows = nrows
    

    def major_ticks(self, startint=None, majorint=None):
	"""Determine axis ticks and labels.

	This method is necessary because matplotlib 
	locators, which would usually be used to automate
	the process of creating x axis labels, can't be 
	shared among axes. The set_major_locator() method 
	assigns its axis to that locator, overwriting any 
	axis that was previously assigned. This is 
	problematic for multi-panel plots.

	Keyword arguments (description [type]):
          startint -- index for start of major ticks
          majorint -- interval between major ticks 

	"""

	# Set major interval if not supplied #

	if majorint:
            assert type(majorint) == int
        else: 
            majorint = myroundup(len(self.data_dt[1]) / 7.)    

	print 'major tick interval:', majorint   

	# Determine the ticks #

	if startint:
            assert type(startint) == int
        else:
            startint = 0
	tick_points = range(startint, len(self.data_orig[:]), majorint)  

	formats  = {'YEARLY': '%y',
                    'MONTHLY': '%b %y',
                    'WEEKLY': '%d/%m/%y',
                    'DAILY': '%d/%m/%y',
                    'HOURLY': '%m/%d %H:%M',
                    'MINUTELY': '%m/%d %H:%M',
                    'SECONDLY': '%m/%d %H:%M'}

	major_xticks = {}
	major_xlabels = {}
	count = 0
	for row in range(1, self.nrows+1):
	    xticks = []
	    labels = []
	    for index, dt in enumerate(self.data_dt[row]):
        	place = index + count
        	if place in tick_points:
        	    xticks.append(dates.date2num(dt))
        	    labels.append(dt.strftime(formats[self.freq]))      

            major_xticks[row] = xticks
            major_xlabels[row] = labels
            count = count + len(self.data_dt[row])

	return major_xticks, major_xlabels


def generate_plot(xaxis, yaxis_data, yaxis_error, file_order,
                  secplot=None,
                  startint=None, majorint=None,
                  ypbounds=None, ysbounds=None, ybuffer=0.1,
                  plabel='', slabel='',
                  outfile=None,
		  ploc=None, sloc=None, legsize='medium',
                  grid=False, phguide=None, shguide=None, vguide=None,
		  colors=['red', 'blue', 'green', 'yellow', 
                          'orange', 'purple', 'brown','aqua'],
		  pline='-', sline='--',
		  nrows=1,
		  title=''): 
    """Create timeseries plot.
    
    Positional arguments (description [type]):
      xaxis        -- DatetimeAxis instance
      yaxis_data   -- y axis data to be plotted
                      [dict (keys: (filename, var, window)) of YaxisElement instances]
      yaxis_error  -- error of y data
                      [dict (keys: (filename, var, window)) of YaxisElement instances]
      file_order   -- List of tuples (filename, var, window) indicating order for plotting
      
    Keyword arguments (description [type]):
      secplot      -- Secondary plot flag [None or anything else]
      startint     -- Starting index for x-axis ticks [int]
      majorint     -- Interval between x-axis ticks [int]
      ypbounds     -- y-axis bounds, primary plot [tuple or list: (min, max)]
      ysbounds     -- y-axis bounds, secondary plot [tuple or list: (min, max)]
      ybuffer      -- Buffer above max y value (and below min value) [float]
                      Expressed as fraction of data range     
      plabel       -- Label for primary y-axis [str]
      slabel       -- Label for secondary y-axis [str]       
      outfile      -- Name of output file [str]
                      If none, figure will be shown instead
      ploc         -- Position of primary legend [int]
      sloc         -- Position of secondary legend [int]
      legsize      -- Size of text in legend
      grid         -- Flag for plotting automatic gridlines
      phguide      -- List of primary axis y-values for horizontal guidelines
      shguide      -- List of secondary axis y-values for horizontal guidelines
      vguide       -- List of datetimes for vertical guidelines 
      colors       -- List of colours for plots
      pline        -- Primary plot linestyle
      sline        -- Secondary plot linestyle
      nrows        -- Number of rows for the plot
      title        -- Plot title

    """
    
    # Initialise figure #
    
    fig = plt.figure()
    plt.subplots_adjust(wspace=0.5) # make a little extra space between the subplots
    
    major_xticks, major_xlabels = xaxis.major_ticks(startint=startint, majorint=majorint)

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
	    xdata = xaxis.data_numeric[pnum]
            ydata = numpy.ma.array(yaxis_data[key].data[pnum])
            label = yaxis_data[key].label
            group = yaxis_data[key].group
            (axis, linestyle) = (ax, pline) if group == 'primary' else (ax2, sline)
	    
            axis.plot(xdata, ydata, color=colors[count], lw=2.0, label=label, linestyle=linestyle, marker='None')
	    
            if yaxis_error and (key in yaxis_error.keys()):
		upper = ydata + 2*numpy.ma.array(yaxis_error[key].data[pnum])   ## should use the numpy.ma addition tool
		lower = ydata - 2*numpy.ma.array(yaxis_error[key].data[pnum])
		axis.plot(xdata, upper, color=colors[count], lw=0.5)
        	axis.plot(xdata, lower, color=colors[count], lw=0.5)
        	axis.fill_between(xdata, upper, lower, facecolor=colors[count], alpha=0.4)
            
            count = count + 1
	    
	#yaxis limits
        pad = (ypbounds[1] - ypbounds[0]) * ybuffer
	ax.set_ylim(ypbounds[0] - pad, ypbounds[1] + pad)
	if secplot:
	    pad = (ysbounds[1] - ysbounds[0]) * ybuffer
            ax2.set_ylim(ysbounds[0] - pad, ysbounds[1] + pad)

	#xticks
        ax.set_xlim(xaxis.data_numeric[pnum][0], xaxis.data_numeric[pnum][-1])
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
        if vguide:
            for xval in nio.get_datetime(vguide):
                ax.axvline(x=dates.date2num(xval), linestyle='--', color='0.5')         

        #gridlines 
        if grid:
	    if not secplot and grid == 'full':
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


def myroundup(x, base=1):
    return int(base * math.ceil(float(x)/base))


def reconfig_to_datetime(all_files, datetime_axis, time_freq, nrows=1):
    """Reconfigure the yaxis data so that it matches the desired x-axis
    and number of rows (i.e. crop or insert missing values as necessary).
      
    Positional arguments:
      all_files      --  dict with netcdf_io.InputData instances as values
      datetime_axis  --  list of datetime instances corresponding to the x-axis
      time_freq      --  datetime axis frequency
                         can be: 'YEARLY', 'MONTHLY', 'WEEKLY', 
                                 'DAILY', 'HOURLY', 'MINUTELY',
                                 'SECONDLY'

    Keyword arguments:
      nrows  --  number of rows in plot

    """

    new_ydata = {}
    max_primary = max_secondary = float("-inf")
    min_primary = min_secondary = float("inf")
    for key, value in all_files.iteritems():
        
	assert isinstance(value, nio.InputData)
	
	# Convert original xaxis to datetime objects #
	
	orig_dtaxis = value.datetimes
	
	# Check the start point of original xaxis against the new datetime_axis #
	
	missval = value.data.missing_value
	ydata = value.data[:]
	
        if orig_dtaxis[0] in datetime_axis[:]:
	    nfill = rrule(eval(time_freq), dtstart=datetime_axis[0], until=orig_dtaxis[0]).count() - 1
	    for i in xrange(nfill):
	        ydata = numpy.insert(ydata, 0, missval)
	else:
	    count = 0
	    while not orig_dtaxis[count] in datetime_axis[:]:
	        count = count + 1
	    ydata = ydata[count:]
		 
        # Check the end point of original xaxis against the new datetime_axis #
	
        if orig_dtaxis[-1] in datetime_axis[:]:
            nfill = rrule(eval(time_freq), dtstart=orig_dtaxis[-1], until=datetime_axis[-1]).count() - 1
	    for i in xrange(nfill):
	        ydata = numpy.append(ydata, missval)
        else:
	    count = -1
	    while not orig_dtaxis[count] in datetime_axis[:]:
	        count = count - 1
	    ydata = ydata[:count+1]

        # Update the minimum and maximum value #

        ydata = numpy.ma.masked_values(ydata, missval)

        if value.set == 'primary':
            max_primary, min_primary = nio.hi_lo(ydata, max_primary, min_primary)
        elif value.set == 'secondary':
            max_secondary, min_secondary = nio.hi_lo(ydata, max_secondary, min_secondary)

        new_ydata[key] = YaxisElement(split_nrows(ydata, nrows), 
                                      all_files[key].tag, 
                                      all_files[key].set)
    
    primary_bounds = (min_primary, max_primary)
    secondary_bounds = None if max_secondary == float("inf") else (min_secondary, max_secondary)


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
      all_files  --  dict with netcdf_io.InputData instances as values
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
    
    if not isinstance(xmax, datetime.datetime):
        xmax = nio.get_datetime([xmax,])[0]    
    
    if not isinstance(xmin, datetime.datetime):
        xmin = nio.get_datetime([xmin,])[0]
	
    # Find highest and lowest datetimes from the input file #

    max_datetime = datetime.datetime.min
    min_datetime = datetime.datetime.max
    for item in all_files.values():
        max_datetime, min_datetime = nio.hi_lo(item.datetimes, max_datetime, min_datetime)

    # Check against the user defined upper and lower bounds #

    max_datetime = xmax if xmax < max_datetime else max_datetime
    min_datetime = xmin if xmin > min_datetime else min_datetime
      
    # Create the x-axis #

    min_datetime = round_datetime(min_datetime, time_freq)
    max_datetime = round_datetime(max_datetime, time_freq)
    xaxis = rrule(eval(time_freq), dtstart=min_datetime, until=max_datetime)
    
    # Adjust the xaxis so it's length is divisible by the number of rows

    while (xaxis.count() % nrows) != 0:
        xaxis = rrule(eval(time_freq), count=(xaxis.count() + 1), dtstart=min_datetime)    
        
    return xaxis

def runave_time_correction(xaxis, time_freq):
    """Resets time axis, because genutil.filters.runningaverage()
    can mess them up."""
    
    return rrule(eval(time_freq), dtstart=round_datetime(xaxis[0], time_freq), count=len(xaxis))


def sort_files(file_list, set_name, time_freq):
    """Place input files into dict.

    positional arguments:
      file_list -- list of 
      set_name  -- can be primary or secondary

    output:
      out_dict  -- dict of nio.InputData instances
                   (key: (filename, var))
      order     -- key order for plotting

    """
    
    out_dict = {}
    order = []
    
    if file_list:
	for item in file_list:
            key = tuple(item[0:3])
            window = int(item[2])
            out_dict[key] = nio.InputData(item[0], item[1], runave=window)
            out_dict[key].tag = item[3]
            out_dict[key].window = window
            out_dict[key].set = set_name
            out_dict[key].datetimes =  runave_time_correction(out_dict[key].datetime_axis()[:], time_freq)
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

    # Extract and sort data - unique identifier is the (filename, variable) pair #

    pdata_dict, pplot_order = sort_files(inargs.primary, 'primary', inargs.freq)
    sdata_dict, splot_order = sort_files(inargs.secondary, 'secondary', inargs.freq)
    
    psdata_dict = dict(pdata_dict.items() + sdata_dict.items()) if sdata_dict else pdata_dict
    psplot_order = (pplot_order + splot_order) if splot_order else pplot_order

    if inargs.error:
        edata_dict = {}
	for item in inargs.error:
            key = item[2:5]
            edata_dict[key] = nio.InputData(item[0], item[1], runave=psdata_dict[key].window)
            edata_dict[key].tag = None
            edata_dict[key].set = 'error'
            edata_dict[key].datetimes =  runave_time_correction(edata_dict[key].datetime_axis()[:], inargs.freq)
    else:
        edata_dict = None

    # Set the x (or datetime) axis #
     
    dtaxis = set_datetime_axis(psdata_dict, inargs.freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(set_datetime_axis)))   
    
    # Reconfigure the data to be plotted, so that it is consistent with the new x-axis #

    yaxis_data, pbounds, sbounds = reconfig_to_datetime(psdata_dict, dtaxis, inargs.freq, 
                                                        **nio.dict_filter(vars(inargs), nio.list_kwargs(reconfig_to_datetime)))
    yaxis_error, epbounds, esbounds = reconfig_to_datetime(edata_dict, dtaxis, inargs.freq, 
                                      **nio.dict_filter(vars(inargs), nio.list_kwargs(reconfig_to_datetime))) if edata_dict else (None, None, None)

    xaxis = DatetimeAxis(dtaxis[:], inargs.freq, **nio.dict_filter(vars(inargs), ['nrows',]))

    # Generate the plot #

    if not inargs.ypbounds:
        inargs.ypbounds = pbounds
   
    if not inargs.ysbounds:
        inargs.ysbounds = sbounds

    generate_plot(xaxis, yaxis_data, yaxis_error, psplot_order, 
                  secplot=splot_order, **nio.dict_filter(vars(inargs), nio.list_kwargs(generate_plot)))


if __name__ == '__main__':

    extra_info = """   
legend options:
  location:   1 upper right, 2 upper left, 3 lower left, 4 lower_right, 5 right, 6 center left, 
	      7 center right, 8 lower center, 9 upper center, 10 center, None no legend 

examples (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_timeseries.py MONTHLY
  /work/dbirving/processed/indices/data/ts_Merra_surface_NINO34_monthly_native-ocean.nc nino34 Nino34 1

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
    parser.add_argument("window", type=str, help="Input file running average window - can be 1 for no smoothing")
    parser.add_argument("tag", type=str, help="Input file tag (or label)")
				     
    parser.add_argument("--primary", type=str, action='append', default=[], nargs=4,
                        metavar=('FILENAME', 'VAR', 'WINDOW', 'TAG'),  
                        help="Additional primary file name, variable, running average window and tag [default: None]")
    parser.add_argument("--secondary", type=str, action='append', default=None, nargs=4, 
                        metavar=('FILENAME', 'VAR', 'WINDOW', 'TAG'),
                        help="Secondary file name, variable, running average window and tag [default: None]")
    parser.add_argument("--error", type=str, action='append', default=None, nargs=5,
                        metavar=('FILENAME', 'VAR', 'PARENT_FILE_NAME', 'PARENT_VAR', 'WINDOW'),
                        help="Error file name, variable, parent file name, parent variable [default: None]")
    parser.add_argument("--outfile", type=str,
                        help="Name of output file [default: None]")

    parser.add_argument("--nrows", type=int, default=1,
                        help="Number of rows (long time axes can be split onto numerous rows [default: %(default)s]")
    parser.add_argument("--title", type=str, 
                        help="Title for plot [default: None]")
    parser.add_argument("--plabel", type=str, 
                        help="primary y-axis label [default: None]")
    parser.add_argument("--slabel", type=str, 
                        help="secondary y-axis label [default: None]")    

    parser.add_argument("--ypbounds", type=float, default=None, nargs=2, metavar=('MIN', 'MAX'),
                        help="Primary y-axis bounds [default: auto]")
    parser.add_argument("--ysbounds", type=float, default=None, nargs=2, metavar=('MIN', 'MAX'),
                        help="Secondary y-axis bounds [default: auto]")
    parser.add_argument("--ybuffer", type=float,
                        help="Scale factor for y-axis upper buffer (i.e. expressed as a fraction)")
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

    parser.add_argument("--grid", type=str, choices=['full', 'zero'], 
                        help="Type of automatic gridlines [default: None]")
    parser.add_argument("--phguide", type=str, nargs='*',
                        help="Primary axis values for horizontal guidelines [default: None]")
    parser.add_argument("--shguide", type=str, nargs='*',
                        help="Secondary axis values for horizontal guidelines [default: None]")
    parser.add_argument("--vguide", type=str, nargs='*',
                        help="Datetimes for vertical guidelines (e.g. 1979-01-01 [default: None]")


    args = parser.parse_args()  

    args.primary.insert(0, [args.infile, args.variable, args.window, args.tag])

    main(args)
    
