# Import general Python modules

import os, sys, re, pdb
from collections import OrderedDict

import operator
import numpy
import pandas

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from itertools import groupby
from operator import itemgetter

from datetime import datetime
from dateutil.rrule import *
from dateutil.relativedelta import relativedelta
from matplotlib.dates import date2num
import calendar

import argparse

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
    import netcdf_io as nio
    import convenient_anaconda as aconv
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

def bin_dates(date_list, start_year, start_month, end_year, end_month):
    """Take a list of dates and return totals in bins."""
    
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


def calc_seasonal_values(monthly_values, month_years):
    """Calculate the seasonal values from the monthly values."""
    
    months = {'DJF': [12, 1, 2], 'MAM': [3, 4, 5],
              'JJA': [6, 7, 8], 'SON': [9, 10, 11]}
    
    seasonal_values = {}
    for season in months.keys():
        seasonal_values[season] = []
    
    year_lists = {}
    for season, months in months.iteritems():    
        years = get_intersection(month_years, months)
        for year in years:
            season_total = 0
            for month in months:
                index = month_years[month].index(year)
                month_total = monthly_values[month][index]
                season_total = season_total + month_total
            seasonal_values[season].append(season_total)
        year_lists[season] = years

    return seasonal_values, year_lists


def crop_dates(start_date, end_date):
    """Adjust a start and end date so the data only includes complete months."""
    
    # Crop to complete month
    if start_date.day != 1:
        start_date = start_date + relativedelta(months=1)
    
    if end_date.day != calendar.monthrange(end_date.year, end_date.month)[1]:
        end_date = end_date - relativedelta(months=1)
    
    # Get the year corresponding to each month
    month_years = {}
    for month in range(1,13):
        month_years[month] = []
    date_list = list(rrule(MONTHLY, dtstart=start_date, until=end_date))
    for date in date_list:
        month_years[date.month].append(date.year)

    return start_date, end_date, month_years


def get_date_bounds(date_list):
    """For a given list of dates, return the year/month bounds for 
    months of complete data (i.e. incomplete start or end 
    months are not included)."""
        
    start_date = datetime.strptime(date_list[0], '%Y-%m-%d')
    end_date = datetime.strptime(date_list[-1], '%Y-%m-%d')
    
    start_date, end_date, month_years = crop_dates(start_date, end_date)

    return start_date.year, start_date.month, end_date.year, end_date.month, month_years


def get_intersection(dictionary, key_list):
    """Return the common values from a dictionary of lists."""
  
    base_key = key_list[0]
    result = set(dictionary[base_key])
    for key in key_list[1:]:
        result.intersection_update(dictionary[key])

    return list(result)


def get_years(date_list):
    """Return a list of integer years."""
    
    start_year = int(date_list[0][0:4])
    end_year = int(date_list[-1][0:4])
    
    return numpy.arange(start_year, end_year + 1, 1)


def plot_monthly_totals(ax, date_list, start_year, start_month, end_year, end_month, month_years):
    """Plot a bar chart showing the totals for each month."""

    monthly_totals, monthly_values = bin_dates(date_list, start_year, start_month, end_year, end_month)
    monthly_pct = numpy.zeros(12)
    for i in range(0, 12):
        ndays = calendar.mdays[i+1] * len(month_years[i+1])
        if i == 1:
            start = start_year if start_month <= 2 else start_year + 1
            end = end_year if end_month >= 2 else end_year - 1
            nleap = calendar.leapdays(start, end)
            ndays = ndays + nleap
        monthly_pct[i] = (monthly_totals[i+1] / float(ndays)) * 100     

    ind = numpy.arange(12)    #the x locations for the bars
    width = 0.8               #the width of the bars
    p1 = plt.bar(ind, monthly_pct, width)

    plt.ylabel('Percentage of days')
    plt.xticks(ind+width/2., calendar.month_abbr[1:])


def plot_seasonal_values(ax, date_list, 
                         start_year, start_month, end_year, end_month, month_years,
                         leg_loc=7):
    """Plot a line graph showing the seasonal values for each year."""
    
    for month, years in month_years.iteritems():
        assert len(years) > 1, \
        """Must have more than one year of data for each season or plot_seasonal_values() won't work""" 

    monthly_totals, monthly_values = bin_dates(date_list, start_year, start_month, end_year, end_month)
    seasonal_values, years = calc_seasonal_values(monthly_values, month_years)

    colors = {'DJF': 'red', 'MAM': 'orange',
             'JJA': 'blue', 'SON': 'green'}

    ax.stackplot(x, seasonal_values['DJF'], seasonal_values['MAM'], seasonal_values['JJA'], seasonal_values['SON'])

    ax.set_xlim(start_year, end_year)
    ax.set_xlabel('year')
    ax.set_ylabel('total days')
    ax.legend(loc=leg_loc, fontsize='small', ncol=5)


def main(inargs):
    """Run the program."""
   
    date_list, date_metadata = gio.read_dates(inargs.date_file)
    start_year, start_month, end_year, end_month, month_years = get_date_bounds(date_list)

    fig = plt.figure(figsize=inargs.figure_size)
    if not inargs.figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    if inargs.dimensions:
        nrows, ncols = inargs.dimensions
    else:
        nrows = 1
        ncols = len(inargs.plot_types)

    for index, plot_type in enumerate(inargs.plot_types):
        assert plot_type in ('monthly_totals_histogram', 'seasonal_values_stackplot')
        
        plotnum = index + 1
        ax = plt.subplot(nrows, ncols, plotnum)
        plt.sca(ax)

        if plot_type == 'monthly_totals_histogram':
            plot_monthly_totals(ax, date_list, 
                                start_year, start_month, end_year, end_month, month_years)
        elif plot_type == 'seasonal_values_stackplot':
            plot_seasonal_values(ax, date_list, 
                                 start_year, start_month, end_year, end_month, month_years,
                                 leg_loc=inargs.leg_loc)

    fig.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:
  
note:
    This script assumes daily input data.
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Calculate various plots from a list of dates'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required arguments
    parser.add_argument("infile", type=str, help="File that contains the list of dates (one date per line)")
    parser.add_argument("outfile", type=str, help="Name of the output file")

    # Selectors
    parser.add_argument("--start", type=str, help="Time start filter (e.g. 1979-02-31)", default=None)
    parser.add_argument("--end", type=str, help="Time end filter (e.g. 2012-12-31)", default=None)
    parser.add_argument("--plot_types", type=str, nargs='*', default=('seasonal_values_stackplot', 'monthly_totals_histogram'),
                        choices=('monthly_totals_histogram', 'seasonal_values_stackplot'),
                        help="Types of plots to include")

    # Plot options
    parser.add_argument("--leg_loc", type=int, default=0,
                        help="Location of legend for line graph [default = 0 = top right] (7 = centre right)")
    parser.add_argument("--dimensions", type=int, nargs=2, metavar=("NROWS", "NCOLS"), default=None,
                        help="dimensions of the plot")
    parser.add_argument("--figure_size", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")

    args = parser.parse_args()            
    main(args)
