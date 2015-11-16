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

import seaborn
seaborn.set_context('paper')

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

    ax.set_ylabel('Percentage of data times')
    ax.xaxis.set_ticks(x+width/2.)
    months = calendar.month_abbr[1:]
    ax.xaxis.set_ticklabels(map(lambda x: x[0], months))
    if label:
        ax.text(0.03, 0.90, label, transform=ax.transAxes, fontsize='large')


def plot_trend_subplot(ax, trend_dict, color_dict, label=None):
    """Insert a subplot showing the linear trend."""
 
    x_vals = []
    colors = []
    for index, season in enumerate(['SON', 'JJA', 'MAM', 'DJF', 'annual']):
        slope, p_value = trend_dict[season]
        print '%s: trend = %f data times per year, p = %f' %(season, slope, p_value)

        x_vals.append(slope)
        colors.append(color_dict[season])
        
        if p_value < 0.05:
            ax.plot(slope + 0.065, numpy.array([index]), color=color_dict[season],
                    marker="*", linestyle='None', markersize=11)
        elif p_value < 0.1:
            ax.plot(slope + 0.065, numpy.array([index]), color=color_dict[season],
                    marker="o", linestyle='None', markersize=11)
        
    y_pos = numpy.arange(0, len(trend_dict.keys()))
    ax.barh(y_pos, numpy.array(x_vals), align='center', color=colors)
    if label:
        ax.text(0.89, 0.90, label, transform=ax.transAxes, fontsize='large')

    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.set_yticklabels([])
    ax.yaxis.set_ticks([])
    ax.xaxis.set_ticks_position('bottom')
    ax.tick_params(axis='x', labelsize='x-small')
    ax.set_xlabel('Trend (data times per year)')
    ax.xaxis.get_label().set_fontsize('xx-small')

    
def plot_seasonal_stackplot(ax, seasonal_data, 
                            seasonal_index=None, index_var=None, 
                            y_buffer=1.0,
                            leg_loc=7, label=None):
    """Plot a stacked histogram showing the seasonal values for each year."""
     
    # Count up 
    assert len(seasonal_data['count']) % 4.0 == 0, "Date range must ensure each season is equally represented"

    season_keys = {2: 'DJF', 5: 'MAM', 8: 'JJA', 11: 'SON'}
    season_colors = {'DJF': '#b2df8a', 'MAM': '#33a02c', 'JJA': '#a6cee3', 'SON': '#1f78b4', 'annual': 'black'}
    season_counts = {}
    season_index_groupings = {}
    for i in range(0,4):
        month = seasonal_data.index[i].month
        season_counts[season_keys[month]] = seasonal_data['count'][i::4]
        if index_var:
            season_index_groupings[season_keys[month]] = seasonal_index[index_var][i::4]
    season_counts['annual'] = season_counts['DJF'].as_matrix() + season_counts['MAM'].as_matrix() + season_counts['JJA'].as_matrix() + season_counts['SON'].as_matrix()

    # Get trends
    season_trends = {}
    for season, data in season_counts.iteritems():
        slope, intercept, r_value, p_value, std_err = stats.linregress(numpy.arange(0, len(data)), data)
        season_trends[season] = [slope, p_value]

    # Plot
    start_year = season_counts['MAM'].index[0].year
    end_year = season_counts['MAM'].index[-1].year

    x = numpy.arange(start_year, end_year + 1)
    pdjf = ax.bar(x, season_counts['DJF'], color=season_colors['DJF'], align='center')
    pmam = ax.bar(x, season_counts['MAM'], color=season_colors['MAM'], align='center',
                  bottom=season_counts['DJF'])
    pjja = ax.bar(x, season_counts['JJA'], color=season_colors['JJA'], align='center',
                  bottom=season_counts['DJF'].as_matrix() + season_counts['MAM'].as_matrix())
    pson = ax.bar(x, season_counts['SON'], color=season_colors['SON'], align='center',
                  bottom=season_counts['DJF'].as_matrix() + season_counts['MAM'].as_matrix() + season_counts['JJA'].as_matrix())

    if index_var:
        plot_index_dots(ax, x, season_index_groupings, annual_totals)
    
    y_lower_limit, y_upper_limit = ax.get_ylim()
    ax.set_ylim([y_lower_limit, y_upper_limit * y_buffer])
    
    x_lower_limit, x_upper_limit = ax.get_xlim()
    ax.set_xlim([start_year - 1, x_upper_limit])
    
    ax.xaxis.set_ticks_position('bottom')
    ax.set_ylabel('Total data times')
    ax.legend( (pdjf[0], pmam[0], pjja[0], pson[0]), ('DJF', 'MAM', 'JJA', 'SON'), fontsize='medium', ncol=4 )
 
    if label:
        ax.text(0.02, 0.94, label, transform=ax.transAxes, fontsize='large')

    return season_trends, season_colors

    
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
        filtered_df = df[selection] 
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

    print 'number of data times:', filtered_dates_df.size

    # Create the plot
    fig = plt.figure(figsize=inargs.figure_size)
    if not inargs.figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    ax0 = plt.subplot2grid((3, 2), (0, 0), rowspan=2, colspan=2)
    ax1 = plt.subplot2grid((3, 2), (2, 0))
    ax2 = plt.subplot2grid((3, 2), (2, 1))

    # Seasonal stackplot
    plt.sca(ax0)
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
    season_trends, season_colors = plot_seasonal_stackplot(ax0, seasonal_data, seasonal_index=seasonal_index, index_var=index_var,
                                                           y_buffer=inargs.y_buffer, leg_loc=inargs.leg_loc, label='(a)')

    # Monthly totals
    plt.sca(ax1)
    monthly_filtered_dates_df = fill_out_dates(filtered_dates_df, inargs.start, inargs.end)
    monthly_data = aggregate_data(monthly_filtered_dates_df, timescale='monthly', method='sum') 
    month_days = monthly_filtered_dates_df.groupby(lambda x: x.month).size()
    plot_monthly_totals(ax1, monthly_data, month_days, label='(b)')

    # Season trends
    plt.sca(ax2)
    plot_trend_subplot(ax2, season_trends, season_colors, label='(c)')

    # Output
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

    # Plot options
    parser.add_argument("--leg_loc", type=int, default=0,
                        help="Location of legend for line graph [default = 0 = top right] (7 = centre right)")
    parser.add_argument("--y_buffer", type=float, default=1.0,
                        help="Multiply y-axis upper bound by this amount [default = 1.0]")

    parser.add_argument("--figure_size", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
    parser.add_argument("--seasonal_dots", type=str, nargs=2, metavar=("FILE", "VAR"), default=None,
                        help="add some dots to show prominant seasons for a particular metric") 

    args = parser.parse_args()
    
    print "Input file:", args.infile
    print "Output file:", args.outfile
      
    main(args)
