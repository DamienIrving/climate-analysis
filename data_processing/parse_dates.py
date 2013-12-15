"""
Filename:     parse_dates.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Parse a list of dates and output a simple statistic

"""

import datetime
from dateutil.rrule import *
from matplotlib.dates import date2num
import calendar

import numpy
import argparse

import os
import sys
module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import general_io as gio


def bin_dates(date_list, timescale, start, end):
    """Take a list of dates and return totals in bins, according to 
    the requested timescale.
    
    Arguments:
      start  -- tuple: (year, month)
      end    -- tuple: (year, month) 
    
    """
        
    dt_list = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), date_list)
    num_list = map(date2num, dt_list)
    
    start_dt = datetime.datetime(start[0], start[1], 1)
    end_dt = datetime.datetime(end[0], start[1], 1) + datetime.timedelta(months=1)
    dt_bin_edges = rrule(MONTHLY, dtstart=start_dt, until=end_dt) #interval=1
    num_bin_edges = map(date2num, dt_bin_edges)
    
    hist_data, edges = numpy.histogram(num_list, bins=num_bin_edges)
    assert len(hist_data) == len(dt_bin_edges[:-1])

    histogram = {}
    for i in range(0, len(hist_data)):
        histogram[dt_bin_edges[i]] = hist_data[i]
    
    return histogram


def print_summary(histogram, dt_labels):
    """Print summary statistics to the screen"""

    monthly_totals = dict((month, 0) for month in range(1,13))
    for key, value in historgram.iteritems():
        monthly_totals[key.month] = monthly_totals[key.month] + value

    print 'Total days'
    for i in range(1,13):
        print calendar[i], monthly_totals[i]

     
def main(inargs):
    """Run the program"""

    # Read in the date list
    date_list = gio.read_dates(inargs.dates)
     
    # Put the data into monthly or seasonal bins
    histogram = bin_dates(date_list, inargs.totals, inargs.start, inargs.end)
    
    # Print summary stats to screen
    print_summary(histogram)
    

if __name__ == '__main__':

    extra_info =""" 
example:
    python parse_dates.py 
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates.txt 

note:
    Assumes daily or higher timescale input data
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Parse a list of dates and output various statistics'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required arguments
    parser.add_argument("dates", type=str, help="Name of input file containing the list of dates")
    
    # Time filters
    parser.add_argument("--start", type=int, nargs=2, metavar=('YEAR', 'MONTH'), default=(1979, 1), 
                        help="Time start filter (e.g. 1979 1)")
    parser.add_argument("--end", type=int, nargs=2, metavar=('YEAR', 'MONTHS'), default=(2012, 12),
                        help="Time end filter (e.g. 2012 12)")

    args = parser.parse_args()            
    main(args)
    