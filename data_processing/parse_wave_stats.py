import os, sys
import numpy
import pandas

import matplotlib.pyplot as plt

from itertools import groupby
from operator import itemgetter

from datetime import datetime
from dateutil.rrule import *

import argparse

try:
    module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
    sys.path.insert(0, module_dir)
    import general_io as gio
except:
    module_dir = os.path.join(os.environ['HOME'], 'Documents',
                          'Professional', 'Scientific_computing',
			  'git_repo', 'phd', 'modules')
    sys.path.insert(0, module_dir)
    import general_io as gio


def datetime_selector(times_str, season=None, start=None, end=None):
    """Define a datetime selector based on the supplied datetime column""" 
    
    #note that selections can be as complex as:
    #((3 <= month) & (month <= 5)) | ((20 <= month) & (month <= 23))
    
    times_dt = pandas.to_datetime(times_str.apply(int).apply(str), format='%Y%m%d%H')

    month_selection = {}
    month_selection['DJF'] = (12, 1, 2)
    month_selection['MAM'] = (3, 4, 5)
    month_selection['JJA'] = (6, 7, 8)
    month_selection['SON'] = (9, 10, 11)

    combined_selection = times_dt != None  #Initialise with all true

    if season:
        months = times_dt.map(lambda x: x.month)
        season_selection = (months.map(lambda val: val in month_selection[season]))
        combined_selection = combined_selection & season_selection
    
    if start:
        datetime_start = datetime.strptime(start, '%Y-%m-%d')
        start_selection = times_dt >= datetime_start  
	combined_selection = combined_selection & start_selection
    
    if end:
        datetime_end = datetime.strptime(end, '%Y-%m-%d')
        end_selection = times_dt <= datetime_end
	combined_selection = combined_selection & end_selection
    
    return combined_selection


def simple_selector(data_column, threshold):
    """Define a selector that retains all values >= threshold"""
    
    return data_column >= threshold


def plot_duration_histogram(data, outfile):
    """Plot a duration histogram"""
    
    # Group consecutive dates (events) and calculate their duration #
    
    date_strs = list(data['date'])
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_strs]

    date_ints = map(lambda x: x.t oordinal(), dates)
    events = []
    for k, g in groupby(enumerate(data), lambda (i,x):i-x):
        events.append(map(itemgetter(1), g))

    durations = numpy.array(map(len, events))
 
    # Print key stats to screen #
 
    print 'Number of events:', len(durations)
    print 'Average duration:', durations.mean()
    print 'Maximum duration:', durations.max()

    # Plot the historgram #

    bin_max = durations.max() + 1
    bin_edges = numpy.arange(0.5, bin_max, 1) 
    
    n, bins, patches = plt.hist(durations, bins=bin_edges, histtype='bar', rwidth=0.8)
    
    plt.xlabel('Duration (days)')
    plt.ylabel('Frequency')
    
    plt.savefig(outfile)


def plot_extent_histogram(data, outfile):
    """Plot an extent histogram"""
    
    bin_max = data.max() + 1
    bin_edges = numpy.arange(0.5, bin_max, 1) 
    
    n, bins, patches = plt.hist(data, bins=bin_edges, histtype='bar', rwidth=0.8)
    
    plt.xlabel('Extent (degrees longitude)')
    plt.ylabel('Frequency')
    
    plt.savefig(outfile)


def print_stats(data):
    """Print basic statistics to the screen"""
    
    print 'number of days:', len(data['date'])
    print 'maximum extent:', data['extent'].max(), 'degrees' 
    mean_extent = data['extent'].mean()
    print 'mean extent:', "%.2f" % round(mean_extent, 2), 'degrees'


def main(inargs):
    """Run the program"""
   
    # Read data 
    indata = pandas.read_csv(inargs.infile)
    
    # Apply filters
    dt_selection = datetime_selector(indata['date'], inargs.season, inargs.start, inargs.end)  
    extent_selection = simple_selector(indata['extent'], inargs.extent_filter)
    selector = dt_selection & extent_selection
    data = indata[selector]
    data.reset_index(drop=True, inplace=True)

    # Print basic statistics to the screen
    print_stats(data)
    
    # Create optional outputs
    if inargs.date_list:    
        gio.write_dates(inargs.date_list, list(data['date']))

    if inargs.extent_histogram:
        plot_extent_histogram(data['extent'], inargs.extent_histogram)

    if inargs.duration_histogram:
        plot_duration_histogram(data, inargs.duration_histogram)

if __name__ == '__main__':

    extra_info =""" 
example:
  
note:
    This script assumes daily input data.
    Nice addition would be a duration filter.
    At the moment season selection will mess with the duration statistics
    (i.e. cut events short)
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Calculate various statistics from ROIM output'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required arguments
    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    # Time filters
    parser.add_argument("--start", type=str, help="Time start filter (e.g. 1979-02-31)", default=None)
    parser.add_argument("--end", type=str, help="Time end filter (e.g. 1979-02-31)", default=None)
    parser.add_argument("--season", type=str, choices=('DJF', 'MAM', 'JJA', 'SON'), default=None,
                        help="Season selector [default = all]")
    
    # Other filters
    parser.add_argument("--extent_filter", type=float, default=None,
                        help="Zonal extent filter - dates below the provided value are discarded")
    
    # Optional outputs
    parser.add_argument("--extent_histogram", type=str, default=None, 
                        help="Name of output file for a histogram of the extent")
    parser.add_argument("--duration_histogram", type=str, default=None, 
                        help="Name of output file for a histogram of the duration")
    parser.add_argument("--date_list", type=str, deafult=None, 
                        help="Name of output file for list of filtered dates")		

    args = parser.parse_args()            
    main(args)
