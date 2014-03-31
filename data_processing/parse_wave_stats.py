import os, sys
from collections import OrderedDict

import numpy
import pandas


import matplotlib.pyplot as plt

from itertools import groupby
from operator import itemgetter

from datetime import datetime
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta
from matplotlib.dates import date2num
import calendar

import argparse

import pdb

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



def bin_dates(date_list, start_year, start_month, end_year, end_month):
    """Take a list of dates and return totals in bins, according to 
    the requested timescale.
    
    """
    
    dt_list = map(lambda x: datetime.strptime(x, '%Y-%m-%d'), date_list)
    num_list = map(date2num, dt_list)
    
    start_dt = datetime(start_year, start_month, 1)
    end_dt = datetime(end_year, end_month, 1) + relativedelta(months=1)
    dt_bin_edges = list(rrule(MONTHLY, dtstart=start_dt, until=end_dt)) #interval=1
    num_bin_edges = date2num(dt_bin_edges)
    
    hist_data, edges = numpy.histogram(num_list, bins=num_bin_edges)
    assert len(hist_data) == len(dt_bin_edges[:-1])

    histogram = {}
    for i in range(0, len(hist_data)):
        histogram[dt_bin_edges[i]] = hist_data[i]
    
    bins_dict = OrderedDict(sorted(histogram.items(), key=lambda t: t[0])) 
    #t[1] would sort by value instead of key  

    # Calculate monthly totals and values
    monthly_totals = dict((month, 0) for month in range(1,13))
    monthly_values = dict((month, []) for month in range(1,13))
    for key, value in histogram.iteritems():
        monthly_totals[key.month] = monthly_totals[key.month] + value
        monthly_values[key.month].append(value)

    return monthly_totals, monthly_values


def calc_seasonal_values(monthly_values):
    """Calculate the seasonal values from the monthly values"""
    
    months = {'DJF': [12, 1, 2], 'MAM': [3, 4, 5],
              'JJA': [6, 7, 8], 'SON': [9, 10, 11],
	      'annual': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
    
    nyears = len(monthly_values[1])
    seasonal_values = {}
    
    for season in months.keys():    
        yrs = nyears - 1 if season == 'DJF' else nyears
	values = numpy.zeros(yrs)
	for month in months[season]:
            if season == 'DJF' and month in (1, 2):
		data = monthly_values[month][1:]
	    elif season == 'DJF' and month == 12:
		data = monthly_values[month][:-1]
	    else: 
		data = monthly_values[month]

            values = values + numpy.array(data)

        seasonal_values[season] = values

    return seasonal_values
    

def datetime_selector(times_str, season=None, start=None, end=None):
    """Define a datetime selector based on the supplied datetime column""" 
    
    #note that selections can be as complex as:
    #((3 <= month) & (month <= 5)) | ((20 <= month) & (month <= 23))
    
    times_dt = pandas.to_datetime(times_str, format='%Y-%m-%d')

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


def get_years(date_list):
    """Return a list of integer years"""
    
    start_year = int(date_list[0][0:4])
    end_year = int(date_list[-1][0:4])
    
    return numpy.arange(start_year, end_year + 1, 1)


def plot_duration_histogram(data, outfile):
    """Plot a duration histogram"""
    
    # Group consecutive dates (events) and calculate their duration #
    
    date_strs = data['date'].tolist()
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_strs]

    date_ints = map(lambda x: x.toordinal(), dates)
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
    
    edges = numpy.arange(-0.5, 361, 1) 
    counts, bins = numpy.histogram(data, edges)
    counts = (counts.astype(float) / len(data)) * 100
    width = (bins[1]-bins[0]) * .9
    plt.bar(bins[:-1], counts, width=width)
    
    plt.xlim(edges[0], edges[-1])    
    plt.xlabel('Extent (degrees longitude)')
    plt.ylabel('Frequency (% total days)')
    
    plt.savefig(outfile)


def plot_monthly_totals(data, ofile, start_year, start_month, end_year, end_month):
    """Plot a bar chart showing the totals for each month"""
    
    date_list = data['date'].tolist()
    monthly_totals, monthly_values = bin_dates(date_list, start_year, start_month, end_year, end_month)
    years = get_years(date_list)
    monthly_pct = numpy.zeros(12)
    for i in range(0, 12):
        monthly_pct[i] = (monthly_totals[i+1] / (float(calendar.mdays[i+1]) * len(years))) * 100     

    ind = numpy.arange(12)    # the x locations for the bars
    width = 0.8               # the width of the bars
    p1 = plt.bar(ind, monthly_pct, width)

    plt.ylabel('Percentage of days')
    plt.xticks(ind+width/2., calendar.month_abbr[1:])

    plt.savefig(ofile)


def plot_seasonal_values(data, ofile, legend_loc, start_year, start_month, end_year, end_month):
    """Plot a line graph showing the seasonal values for each year"""
    
    date_list = data['date'].tolist()
    monthly_totals, monthly_values = bin_dates(date_list, start_year, start_month, end_year, end_month)
    seasonal_values = calc_seasonal_values(monthly_values)
    years = get_years(date_list)
    assert len(years) > 1, \
    """Must have more than one year of data or plot_seasonal_values() won't work""" 
    
    colors = {'DJF': 'red', 'MAM': 'orange',
             'JJA': 'blue', 'SON': 'green',
	     'annual': 'black'}
    
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    pdb.set_trace()
    for season, values in seasonal_values.iteritems():
	xvals = years[1:] if season == 'DJF' else years
	ax.plot(xvals, seasonal_values[season], color=colors[season], lw=2.0, label=season)       

    ax.set_xlim(start_year, end_year)
    ax.set_xlabel('year')
    ax.set_ylabel('total days')
    ax.legend(loc=legend_loc, fontsize='small', ncol=5)

    plt.savefig(ofile)


def print_stats(data):
    """Print basic statistics to the screen"""
    
    print 'total number of days:', len(data['date'])
    extent_list = data['extent'].tolist()
    print 'zero extent days:', extent_list.count(0.0)
    print 'maximum extent:', data['extent'].max(), 'degrees' 
    mean_extent = data['extent'].mean()
    print 'mean extent:', "%.2f" % round(mean_extent, 2), 'degrees'


def simple_selector(data_column, threshold):
    """Define a selector that retains all values >= threshold"""
    
    return data_column >= threshold


def get_date_bounds(indata, dt_selection):
    """For a given list of dates, return the year/month bounds for 
    months of complete data (i.e. incomplete start or end months are
    not included"""
    
    temp_data = indata[dt_selection]
    date_list = temp_data['date'].tolist()
    
    start_date = datetime.strptime(date_list[0], '%Y-%m-%d')
    end_date = datetime.strptime(date_list[-1], '%Y-%m-%d')
    
    if start_date.day != 1:
        start_date = start_date + relativedelta(months=1)
    
    if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
        end_date = end_date - relativedelta(months=1)

    month_diff = start_date.month - end_date.month
    assert month_diff in [-11, 1], \
    """Select a time period for which each month has the same amount of complete
    records (i.e. all days)"""

    return start_date.year, start_date.month, end_date.year, end_date.month


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
        gio.write_dates(inargs.date_list, data['date'].tolist())

    if inargs.extent_histogram:
        plot_extent_histogram(data['extent'], inargs.extent_histogram)

    if inargs.duration_histogram:
        plot_duration_histogram(data, inargs.duration_histogram)

    if inargs.monthly_totals_histogram or inargs.seasonal_values_line:
        start_year, start_month, end_year, end_month = get_date_bounds(indata, dt_selection)

    if inargs.monthly_totals_histogram:
        plot_monthly_totals(data, inargs.monthly_totals_histogram,
                            start_year, start_month, end_year, end_month)
    
    if inargs.seasonal_values_line:
        plot_seasonal_values(data, inargs.seasonal_values_line, inargs.leg_loc, 
	                     start_year, start_month, end_year, end_month)
    

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

    description='Calculate various statistics from calc_wave_stat.py output'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required arguments
    parser.add_argument("infile", type=str, help="Input file name")
    
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
    parser.add_argument("--monthly_totals_histogram", type=str, default=None,
                        help="Name of the output file for a histogram of the monthly totals")
    parser.add_argument("--seasonal_values_line", type=str, default=None,
                        help="Name of the output file for a line graph of the seasonal counts")
    parser.add_argument("--date_list", type=str, default=None, 
                        help="Name of output file for list of filtered dates")		

    parser.add_argument("--leg_loc", type=int, default=7,
                        help="Location of legend for line graph [default = 7 = centre right]")

    args = parser.parse_args()            
    main(args)
