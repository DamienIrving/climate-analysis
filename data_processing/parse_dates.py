"""
Filename:     parse_dates.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Parse a list of dates and output simple statistics relating to 
              the monthly totals

"""

import datetime
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta
from matplotlib.dates import date2num
import calendar

import numpy
import argparse
from collections import OrderedDict

import cdms2

import os
import sys
module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio
import general_io as gio

import matplotlib.pyplot as plt


def bin_dates(date_list, start, end):
    """Take a list of dates and return totals in bins, according to 
    the requested timescale.
    
    Arguments:
      start  -- tuple: (year, month)
      end    -- tuple: (year, month) 
    
    Output:
      Returns an ordered dictionary
    
    """
        
    dt_list = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), date_list)
    num_list = map(date2num, dt_list)
    
    start_dt = datetime.datetime(start[0], start[1], 1)
    end_dt = datetime.datetime(end[0], end[1], 1) + relativedelta(months=1)
    dt_bin_edges = list(rrule(MONTHLY, dtstart=start_dt, until=end_dt)) #interval=1
    num_bin_edges = date2num(dt_bin_edges)
    
    hist_data, edges = numpy.histogram(num_list, bins=num_bin_edges)
    assert len(hist_data) == len(dt_bin_edges[:-1])

    histogram = {}
    for i in range(0, len(hist_data)):
        histogram[dt_bin_edges[i]] = hist_data[i]
    
    return OrderedDict(sorted(histogram.items(), key=lambda t: t[0])) 
    #t[1] would sort by value instead of key  


def show_summary(histogram, hist_file=False, year_bounds=None):
    """Print summary statistics to the screen and plot if hist_file given"""

    # Calculate monthly totals
    monthly_totals = dict((month, 0) for month in range(1,13))
    for key, value in histogram.iteritems():
        monthly_totals[key.month] = monthly_totals[key.month] + value

    # Print to screen
    print 'Total days'
    for i in range(1,13):
        print calendar.month_name[i], monthly_totals[i]

    # Create plot (bar chart)
    if hist_file and year_bounds:
        nyears = year_bounds[1] - year_bounds[0] + 1
        monthly_pct = numpy.zeros(12)
        for i in range(0, 12):
            monthly_pct[i] = (monthly_totals[i+1] / (float(calendar.mdays[i+1]) * nyears)) * 100     

        ind = numpy.arange(12)    # the x locations for the bars
        width = 0.8            # the width of the bars
        p1 = plt.bar(ind, monthly_pct, width)

        plt.ylabel('Percentage of days')
        plt.xticks(ind+width/2., ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec') )

        plt.savefig(hist_file)
        

def write_totals(histogram, outfile):
    """Write the monthly totals to a netCDF file"""

    # Create time axis
    assert histogram.keys() == sorted(histogram.keys()), \
    'Time values in histogram dictionary are not monotonic'
    time_vals = date2num(histogram.keys()) - 1  #date2num converts to days since 0001-01-01 UTC + 1
    
    time_axis = cdms2.createAxis(time_vals)
    time_axis.id = 'time'
    time_axis.standard_name = 'time'
    time_axis.calendar = 'standard' 
    time_axis.units = 'days since 0001-1-1'
    time_axis.axis = 'T'

    # Define variable attributes
    outvar_atts = {'id': 'total',
                   'standard_name': 'total',
                   'long_name': 'total days for each month',
                   'units': 'days'}
    global_atts = {}

    # Write output file
    nio.write_netcdf(outfile, " ".join(sys.argv), 
                     global_atts, 
                     [histogram.values(),],
                     [outvar_atts,], 
                     [(time_axis,),])


def main(inargs):
    """Run the program"""

    # Read in the date list
    date_list = gio.read_dates(inargs.dates)
     
    # Put the data into monthly or seasonal bins
    histogram = bin_dates(date_list, inargs.start, inargs.end)
    
    # Print summary stats to screen and plot if desired
    show_summary(histogram, inargs.hist_file, (inargs.start[0], inargs.end[0]) )
    
    # Write the output file
    if inargs.totals_file:
        write_totals(histogram, inargs.totals_file)
    

if __name__ == '__main__':

    extra_info =""" 
example:
    python parse_dates.py 
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates.txt 
    --totals_file hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_monthly-totals.nc
    --hist_file hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_monthly-totals.png

note:
    Assumes daily or higher timescale input data
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Parse a list of dates and output various statistics relating to the monthly totals'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("dates", type=str, help="Name of input file containing the list of dates")
    
    parser.add_argument("--start", type=int, nargs=2, metavar=('YEAR', 'MONTH'), default=(1979, 1), 
                        help="Time start filter (e.g. 1979 1)")
    parser.add_argument("--end", type=int, nargs=2, metavar=('YEAR', 'MONTHS'), default=(2012, 12),
                        help="Time end filter (e.g. 2012 12)")
    parser.add_argument("--hist_file", type=str, default=None,
                        help="Name of the .png output file for the histogram of monthly totals")
    parser.add_argument("--totals_file", type=str, default=None,
                        help="Name of the netCDF output file for the monthly totals")    


    args = parser.parse_args()            
    main(args)
    
