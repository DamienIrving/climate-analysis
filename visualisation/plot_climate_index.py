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
from pylab import *

import datetime
from dateutil.rrule import *  # it seems to not work unless you import *

import numpy
import numpy.ma as ma
import math

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio

    

def set_datetime_axis(all_files, time_freq, xmax=datetime.min, xmin=datetime.max):
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

    assert isinstance(all_files, nio.InputData)
    assert time_freq in ['YEARLY', 'MONTHLY', 'WEEKLY', 
                         'DAILY', 'HOURLY', 'MINUTELY', 'SECONDLY']
    assert isinstance(xmax, datetime.datetime)
    assert isinstance(xmin, datetime.datetime)


    max_datetime = datetime.min
    min_datetime = datetime.max
    for item in all_files.values():
        max_datetime, min_datetime = nio.hi_lo(item.datetime_axis(), max_datetime, min_datetime)

    max_datetime, min_datetime = nio.hi_lo([xmax, xmin], max_datetime, min_datetime)
    
    return rrule(eval(timeres), dtstart=min_datetime ,until=max_datetime)


def split_nrows(indata,nrows):
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


def split_data(datetime_axis, xdata, ydata, nrows):
    """Splits up the data according to the number of rows"""
    
    ydata_full = numpy.ma.ones(len(datetime_axis)) * 1.e20
    
    #find location of first time point


    min(range(len(xdata)), key=lambda i: abs(a[i] - datetime_axis[0]))
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

 
def generate_plot(xaxis, ydata, 
                  ybounds=None,
                  outfile_name=None, 
		  leglocp=None, leglocs=None, legsize='medium',
		  pcolor_list=['red', 'blue', 'green', 'yellow', 'orange'], 
		  scolor_list=['purple', 'brown','aqua'],
		  linep='-', lines='--',
		  nrows=1,
		  title=''):
    """Create timeseries plot.
    
    """
    
    # Initialise figure #
    
    fig = plt.figure()
       
    units_text='temp'
    units_text2='temp'
    
    # Prepare the data according to the number of rows #
   
    if secondary_file_list:
        all_file_list = primary_file_list + secondary_file_list
    else:
        all_file_list = primary_file_list
    
    xplot = {}
    yplot = {}
    yplot_error = {}
    for afile in all_file_list:
	xplot[afile.fname],yplot[afile.fname] = split_data(xaxis_full_float,xdata[afile.fname],ydata[afile.fname],nrows)
	if (afile.fname in error_list):
	    xplot[afile.fname],yplot_error[afile.fname] = split_data(xaxis_full_float,xdata[afile.fname],ydata[afile.fname,'error'],nrows)

    # Make the plot #
    
    for row in range(0,nrows):

        pnum = row + 1

	#initialise plot
	ax = fig.add_subplot(nrows,1,pnum)  # rows, columns, plot number

	if secondary_file_list:
	    ax2 = ax.twinx()

	#plot primary axis data	
	count = 0
	for pfile in primary_file_list:
	    label = pfile.variable_name+', '+pfile.index+', '+pfile.dataset
	    ax.plot(numpy.ma.array(xplot[pfile.fname][pnum]),numpy.ma.array(yplot[pfile.fname][pnum]),color=pcolor_list[count],lw=2.0,label=label,linestyle=linep,marker='None')
	    if (pfile.fname in error_list):
		upper = numpy.ma.array(yplot[pfile.fname][pnum]) + 2*numpy.ma.array(yplot_error[pfile.fname][pnum])
		lower = numpy.ma.array(yplot[pfile.fname][pnum]) - 2*numpy.ma.array(yplot_error[pfile.fname][pnum])
		ax.plot(numpy.ma.array(xplot[pfile.fname][pnum]),upper,color=pcolor_list[count],lw=0.5)
        	ax.plot(numpy.ma.array(xplot[pfile.fname][pnum]),lower,color=pcolor_list[count],lw=0.5)
        	ax.fill_between(numpy.ma.array(xplot[pfile.fname][pnum]),upper,lower,facecolor=pcolor_list[count],alpha=0.4)
            count = count + 1
	    
        #plot secondary axis data
	if secondary_file_list:
	    count = 0
	    for sfile in secondary_file_list:
		label = sfile.variable_name+', '+sfile.index+', '+sfile.dataset
		ax2.plot(numpy.ma.array(xplot[sfile.fname][pnum]),numpy.ma.array(yplot[sfile.fname][pnum]),color=scolor_list[count],lw=2.0,label=label,linestyle=lines,marker='None')
		if (sfile.fname in error_list):
		    upper = numpy.ma.array(yplot[sfile.fname][pnum]) + 2*numpy.ma.array(yplot_error[sfile.fname][pnum])
		    lower = numpy.ma.array(yplot[sfile.fname][pnum]) - 2*numpy.ma.array(yplot_error[sfile.fname][pnum])
		    ax2.plot(numpy.ma.array(xplot[sfile.fname][pnum]),upper,color=scolor_list[count],lw=0.5)
        	    ax2.plot(numpy.ma.array(xplot[sfile.fname][pnum]),lower,color=scolor_list[count],lw=0.5)
        	    ax2.fill_between(numpy.ma.array(xplot[sfile.fname][pnum]),upper,lower,facecolor=scolor_list[count],alpha=0.4)
                count = count + 1

	#plot extra guidelines
	units_text = set_units(primary_file_list[0].variable_name,primary_file_list[0].index,units_text,'Primary')

        if secondary_file_list:
	    units_text2 = set_units(secondary_file_list[0].variable_name,secondary_file_list[0].index,units_text2,'Secondary')

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
	minor_xticks,major_xticks,major_xlabels = get_xticks(xplot[primary_file_list[0].fname][pnum])

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

	if secondary_file_list:
	    ax2.set_ylabel(units_text2,fontsize='medium',rotation=270)

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
      set_name -- can be primary or secondary

    """

    out_dict = {}
    order = []
    for item in file_list:
        key = item[0:2]
        window = int(item[3])
        out_dict{key} = nio.InputData(item[0], item[1], runave=window)
        out_dict{key}.tag = item[2]
        out_dict{key}.window = window
        out_dict{key}.set = set_name
        order.append(key)         

    return out_dict, order


def main(inargs):
    """Run the program"""
    
    # Sort files - unique identifier is the filename, variable pair #

    primary_dict, primary_order = sort_files(inargs.primary, 'primary')
    secondary_dict, secondary_order = sort_files(inargs.secondary, 'secondary')
    
    allfile_dict = dict(primary_file_list.items() + secondary_file_list.items())
    allfile_order = primary_order + secondary_order

    error_files = {}
    for item in inargs.error:
        key = item[2:4]
        error_files{key} = nio.InputData(item[0], item[1], runave=allfile_dict[key].window)
        

    ### FROM HERE DOWN COULD ALL GO IN GENERATE PLOT ##

    # Set the x (datetime) axis #
     
    xaxis = set_datetime_axis(allfile_dict, freq, **nio.dict_filter(vars(inargs), nio.list_kwargs(set_datetime_axis)))   
    
    # Split the data according to the number of rows #

    data = split_data()    

    # Set the y-axis bounds #

    define_function

    
    ## Generate the plot ##
    
    generate_plot(primary_file_list, secondary_file_list, error_list, xdata, ydata, ybounds, xaxis_full_float,
                  outfile_name, leglocp, leglocs, legsize, pcolor_list, scolor_list, linep, lines, nrows, title)
    

if __name__ == '__main__':

    extra_info = """   
legend options:
  location:   1 upper right, 2 upper left, 3 lower left, 4 lower_right, 5 right, 6 center left, 
	      7 center right, 8 lower center, 9 upper center, 10 center, None no legend 

examples (abyss.earthsci.unimelb.edu.au):
  /opt/cdat/bin/cdat plot_climate_index.py --wp 5 
  /work/dbirving/processed/indices/data/ts_Merra_NINO34_monthly_native-ocean.txt
  /work/dbirving/processed/indices/data/tos_ERSSTv3b_NINO34_monthly_native.txt

  /opt/cdat/bin/cdat plot_climate_index.py 
  /work/dbirving/processed/indices/data/ts_Merra_surface_EOF1_monthly_native-ocean-eqpacific.txt 
  /work/dbirving/processed/indices/data/ts_Merra_surface_EOF2_monthly_native-ocean-eqpacific.txt 
  -s /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF1_monthly_native-eqpacific.txt,
  /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF2_monthly_native-eqpacific.txt 
  -r 3 --wp 5 --ws 5 --lp 2 --ls 1

note:
  The expected measure of error is the standard deviation (twice the standard deviation either side
  of the central estimate is plotted).

"""

    description='Plot timeseries data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
	
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
    parser.add_argument("--buffer", type=float, default=1.0,
                        help="Scale factor for y axis upper buffer [default: %(default)s]")
    parser.add_argument("--nrows", type=int, default=1,
                        help="Number of rows (long time axes can be split onto numerous rows [default: %(default)s]")
    parser.add_argument("--xmax", type=str, metavar=('DATE'),
                        help="Maximum time axis value [default: auto]")
    parser.add_argument("--xmin", type=str, metavar=('DATE'),
                        help="Minimum time axis value [default: auto]")
    parser.add_argument("--locp", type=int, default=None, 
                        help="Location of the primary figure legend [defualt: no legend]")
    parser.add_argument("--locs", type=int, default=None, 
                        help="Location of the secondary figure legend [defualt: non legend]")
    parser.add_argument("--legsize", type=str, 
                        choices=['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'],
                        help="Size of the legend text [default: medium]")
    parser.add_argument("--colorp", type=str, nargs='*',
                        help="Colors for the primary plot [default: auto]")
    parser.add_argument("--colors", type=str, nargs='*',
                        help="Colors for the secondary plot [default: auto]")
    parser.add_argument("--linep", type=str, choices=['-', '--', '-.', ':'],
                        help="Line style for the primary plot [default: solid]")
    parser.add_argument("--lines", type=str, choices=['-', '--', '-.', ':'],
                        help="Line style for the secondary plot [default: dashed]")
    parser.add_argument("--windowp", type=int, default=1,
                        help="Window for primary axis running average [default: %(default)s]")
    parser.add_argument("--windows", type=int, default=1,
                        help="Window for secondary axis running average [default: %(default)s]")
    parser.add_argument("--setyp", type=float, default=None, nargs=2, metavar=('MIN', 'MAX'),
                        help="Primary y axis bounds [default: auto]")
    parser.add_argument("--setys", type=float, default=None, nargs=2, metavar=('MIN', 'MAX'),
                        help="Secondary y axis bounds [default: auto]")
    parser.add_argument("--title", type=str, default=None, 
                        help="Title for plot [default: None]")
    parser.add_argument("--ylabel", type=str, default=None, 
                        help="y axis label [default: None]")
    parser.add_argument("--xlabel", type=str, default=None, 
                        help="x axis label [default: None]")    


    args = parser.parse_args()  

    args.primary.insert(0, (args.infile, args.variable, args.tag, args.window))

    main(args)
    
