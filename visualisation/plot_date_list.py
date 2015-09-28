# Import general Python modules

import os, sys, pdb
from datetime import datetime
import argparse, numpy, pandas, calendar
from pandas.tseries.resample import TimeGrouper
from scipy import stats
from itertools import groupby

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions


def aggregate_data(df, timescale, method):
    """Aggregate data to given timescale."""

    assert timescale in ['monthly', 'seasonal']
    assert method in ['sum', 'mean']
    timescale_dict = {'monthly': '1M', 'seasonal': '3M'}

    aggregated_data = df.groupby(TimeGrouper(freq=timescale_dict[timescale], closed='left'))
    if method == 'sum':
        aggregated_data = aggregated_data.sum()
    elif method == 'mean':
        aggregated_data = aggregated_data.mean()

    aggregated_data = aggregated_data.drop(aggregated_data.index[-1])

    return aggregated_data


def fill_out_dates(df, start_date, end_date):
    """Put a zero entry in a pandas df for all missing dates."""

    date_range = pandas.date_range(start_date, end_date)
    filled_df = df.reindex(date_range, fill_value=0)

    return filled_df


def get_seasonal_bounds(start_date, end_date):
    """Set the start and end date for seasonal analysis.

    Ensures that only full years (Dec-Nov) are included.    

    """

    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_dt = datetime.strptime(end_date, '%Y-%m-%d')

    if start_date_dt.month == 12:
        new_start_date = datetime(start_date_dt.year + 1, 12, 1)
    else:
        new_start_date = datetime(start_date_dt.year, 12, 1)

    if end_date_dt.month < 12:
        new_end_date = datetime(end_date_dt.year - 1, 11, 30)
    else:
        new_end_date = datetime(end_date_dt.year, 11, 30)
        
    return new_start_date.strftime('%Y-%m-%d'), new_end_date.strftime('%Y-%m-%d')


def get_seasonal_index(nc_file, var, start, end):
    """Get seasonal aggregate of metric from netCDF file."""

    dset = xray.open_dataset(nc_file)
    gio.check_xrayDataset(dset, var)

    metric_df = dset[var].to_pandas()
    metric_metadata = dset.attrs['history']

    metric_aggregate_df = aggregate_data(metric_df, timescale='seasonal', method='mean')
    filtered_dates_metric_aggregate_df = time_filter(metric_aggregate_df, start, end)

    return filtered_dates_metric_aggregate_df, metric_metadata


def plot_duration(ax, df, label=None):
    """Plot a bar chart showing the distribution of event duration.

    Args:
      ax (AxesSubplot): plot axis
      date_list (pandas DataFrame): The list of dates

    """

    # Get the duration data
    df['dates'] = df.index
    df['time_delta'] = df['dates'].diff()
    in_event = df['time_delta'] < pandas.tslib.Timedelta('2 days')

    grouped_events = [(k, sum(1 for i in g)) for k,g in groupby(in_event)] 

    duration_data = []
    false_count = 0
    for event in grouped_events:
        if event[0]:
            duration_data.append(event[1])
        else:
            false_count = false_count + event[1]

    #ajust for fact that two consecutive dates are required for a true
    ones = duration_data.count(1)
    false_count = false_count - ones
    duration_data = numpy.array(duration_data) + 1
    duration_data = numpy.concatenate((duration_data, numpy.array([1] * false_count)))

    # Bin it
    bin_res = 1
    bin_edge_start = duration_data.min() - (bin_res / 2.)
    bin_edge_end = duration_data.max() + bin_res + (bin_res / 2.)
    bin_centers = numpy.arange(duration_data.min(), duration_data.max() + bin_res, bin_res)
    hist, bin_edges = numpy.histogram(duration_data, bins=numpy.arange(bin_edge_start, bin_edge_end, bin_res))

    # Plot
    width = 0.8
    ax.bar(bin_centers, hist, width, color='0.7')
    ax.set_ylabel('Duration')
    ax.set_xlabel('Frequency')

    if label:
        ax.text(0.97, 0.95, label, transform=ax.transAxes, fontsize='large')


def plot_index_dots(ax, x, index_data, bar_heights, upper_threshold=1.0, lower_threshold=-1.0):
    """Plot dots."""

    style_dict = {'DJF': (2.0, '#b2df8a'),
                  'MAM': (4.0, '#33a02c'),
                  'JJA': (6.0, '#a6cee3'),
                  'SON': (8.0, '#1f78b4'),}

    for season, style_info in style_dict.iteritems():
        top_buffer, color = style_info
        ax.plot(x + 0.4, numpy.where(index_data[season] > upper_threshold, bar_heights + top_buffer, None), color=color, marker="o", linestyle='None')
        ax.plot(x + 0.4, numpy.where(index_data[season] < lower_threshold, bar_heights + top_buffer, None), color=color, marker="^", linestyle='None')


def plot_monthly_totals(ax, monthly_data, month_days, label=None):
    """Plot a bar chart showing the totals for each month.

    Args:
      ax (AxesSubplot): plot axis
      monthly_data (pandas DataFrame): Totals for each individual month 
        of each year
      month_days (pandas DataFrame): Total number of days in each month 
        over the entire time period  

    """

    # Group the data and count up monthly totals
    grouped_data = monthly_data.groupby(lambda x: x.month)
    monthly_totals = grouped_data.sum()

    # Convert to a percentage
    monthly_pct = (monthly_totals.as_matrix().flatten() / month_days.as_matrix().flatten()) * 100     

    # Plot
    x= numpy.arange(12)
    width = 0.8

    ax.bar(x, monthly_pct, width, color='0.7')

    ax.set_ylabel('Percentage of days')
    ax.xaxis.set_ticks(x+width/2.)
    ax.xaxis.set_ticklabels(calendar.month_abbr[1:])
    if label:
        ax.text(0.03, 0.95, label, transform=ax.transAxes, fontsize='large')


def plot_seasonal_stackplot(ax, seasonal_data, seasonal_index=None, index_var=None, leg_loc=7, label=None):
    """Plot a stacked histogram showing the seasonal values for each year."""
     
    # Count up 
    assert len(seasonal_data['count']) % 4.0 == 0, "Date range must ensure each season is equally represented"

    season_keys = {2: 'DJF', 5: 'MAM', 8: 'JJA', 11: 'SON'}
    season_counts = {}
    season_index_groupings = {}
    for i in range(0,4):
        month = seasonal_data.index[i].month
        season_counts[season_keys[month]] = seasonal_data['count'][i::4]
        if index_var:
            season_index_groupings[season_keys[month]] = seasonal_index[index_var][i::4]

    # Plot
    start_year = season_counts['MAM'].index[0].year
    end_year = season_counts['MAM'].index[-1].year

    x = numpy.arange(start_year, end_year + 1)
    pdjf = ax.bar(x, season_counts['DJF'], color='#b2df8a')
    pmam = ax.bar(x, season_counts['MAM'], color='#33a02c', bottom=season_counts['DJF'])
    pjja = ax.bar(x, season_counts['JJA'], color='#a6cee3', bottom=season_counts['DJF'].as_matrix()+season_counts['MAM'].as_matrix())
    pson = ax.bar(x, season_counts['SON'], color='#1f78b4', bottom=season_counts['DJF'].as_matrix()+season_counts['MAM'].as_matrix()+season_counts['JJA'].as_matrix())

    season_counts['annual'] = season_counts['DJF'].as_matrix() + season_counts['MAM'].as_matrix() + season_counts['JJA'].as_matrix() + season_counts['SON'].as_matrix()
    if index_var:
        plot_index_dots(ax, x, season_index_groupings, annual_totals)

    ax.set_ylabel('Total days')
    ax.legend( (pdjf[0], pmam[0], pjja[0], pson[0]), ('DJF', 'MAM', 'JJA', 'SON') )
    if label:
        ax.text(0.03, 0.95, label, transform=ax.transAxes, fontsize='large')

    # Stats
    for season, counts in season_counts.iteritems():
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, counts)
        print '%s: trend = %f events/year, p = %f' %(season, slope, p_value)

    
def time_filter(df, start_date, end_date):
    """Remove times that are not within the start/end bounds."""

    if start_date:
        datetime_start = datetime.strptime(start_date, '%Y-%m-%d')
        start_selection = df.index >= datetime_start

    if end_date:
        datetime_end = datetime.strptime(end_date, '%Y-%m-%d')
        end_selection = df.index <= datetime_end

    if start_date and end_date:
        selection = start_selection & end_selection
        filtered_df = df[combined_selection] 
    elif start_date:
        filtered_df = df[start_selection] 
    elif end_date:
        filtered_df = df[end_selection]
    else:
        filtered_df = df

    return filtered_df


def main(inargs):
    """Run the program."""

    # Read the data into a pandas data frame   
    datetime_list, datetime_metadata = gio.read_dates(inargs.infile)
    date_list = map(lambda x: x.split('T')[0], datetime_list)
    ones = numpy.ones(len(date_list))
    dates_df = pandas.DataFrame(ones, index=map(lambda x: datetime.strptime(x, '%Y-%m-%d'), date_list), columns=['count'])
    filtered_dates_df = time_filter(dates_df, inargs.start, inargs.end)

    # Create the plot
    fig = plt.figure(figsize=inargs.figure_size)
    if not inargs.figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    if inargs.dimensions:
        nrows, ncols = inargs.dimensions
    else:
        nrows = 1
        ncols = len(inargs.plot_types)

    labels = ['(a)', '(b)', '(c)'] 
    for index, plot_type in enumerate(inargs.plot_types):
        assert plot_type in ('monthly_totals_histogram', 'seasonal_values_stackplot', 'duration_histogram')
        
        plotnum = index + 1
        ax = plt.subplot(nrows, ncols, plotnum)
        plt.sca(ax)

        if plot_type == 'monthly_totals_histogram':
            monthly_filtered_dates_df = fill_out_dates(filtered_dates_df, inargs.start, inargs.end)
            monthly_data = aggregate_data(monthly_filtered_dates_df, timescale='monthly', method='sum') 
            month_days = monthly_filtered_dates_df.groupby(lambda x: x.month).size()
            plot_monthly_totals(ax, monthly_data, month_days, label=labels[index])

        elif plot_type == 'seasonal_values_stackplot':
            seasonal_start, seasonal_end = get_seasonal_bounds(inargs.start, inargs.end)
            seasonal_filtered_dates_df = fill_out_dates(filtered_dates_df, seasonal_start, seasonal_end)
            seasonal_data = aggregate_data(seasonal_filtered_dates_df, timescale='seasonal', method='sum')
            if inargs.seasonal_dots:
                seasonal_index, dots_metadata = get_seasonal_index(inargs.seasonal_dots[0], inargs.seasonal_dots[1], seasonal_start, seasonal_end)
                index_var = inargs.seasonal_dots[1]
                metadata_dict = {inargs.seasonal_dots[0]: dots_metadata}
            else:
                seasonal_index = None
                index_var = None
            plot_seasonal_stackplot(ax, seasonal_data, seasonal_index=seasonal_index, index_var=index_var,
                                    leg_loc=inargs.leg_loc, label=labels[index])

        elif plot_type == 'duration_histogram':
            plot_duration(ax, filtered_dates_df, label=labels[index])

    fig.savefig(inargs.outfile, bbox_inches='tight')
    metadata_dict = {inargs.infile: datetime_metadata}
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:
  
note:
    This script assumes daily input data.
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Generate various plots from a list of dates'
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
    parser.add_argument("--plot_types", type=str, nargs='*', default=('monthly_totals_histogram', 'seasonal_values_stackplot'),
                        choices=('monthly_totals_histogram', 'seasonal_values_stackplot', 'duration_histogram'),
                        help="Types of plots to include")

    # Plot options
    parser.add_argument("--leg_loc", type=int, default=0,
                        help="Location of legend for line graph [default = 0 = top right] (7 = centre right)")
    parser.add_argument("--dimensions", type=int, nargs=2, metavar=("NROWS", "NCOLS"), default=None,
                        help="dimensions of the plot")
    parser.add_argument("--figure_size", type=float, default=(16.0, 7.0), nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
    parser.add_argument("--seasonal_dots", type=str, nargs=2, metavar=("FILE", "VAR"), default=None,
                        help="add some dots to show prominant seasons for a particular metric")

    args = parser.parse_args()            
    main(args)
