# Import general Python modules

import os, sys, pdb
from datetime import datetime
import argparse, numpy, pandas
from pandas.tseries.resample import TimeGrouper

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





def get_date_bounds(date_list):
    """For a given list of dates, return the year/month bounds for 
    months of complete data (i.e. incomplete start or end 
    months are not included)."""
        
    start_date = datetime.strptime(date_list[0], '%Y-%m-%d')
    end_date = datetime.strptime(date_list[-1], '%Y-%m-%d')
    
    monthly_start = inargs.start
    

    return 


def plot_monthly_totals(ax, dates_df):
    """Plot a bar chart showing the totals for each month."""

    # Prepare data
    monthly_data = dates_df.groupby(TimeGrouper(freq='1M', closed='left')).sum()
    monthly_data = monthly_data.drop(monthly_data.index[-1])

    # Group the data and count up
    grouped_data = monthly_data.groupby(lambda x: x.month)
    monthly_totals = grouped_data.sum()

    # Plot


def plot_seasonal_stackplot(ax, dates_df, leg_loc=7):
    """Plot a stacked histogram showing the seasonal values for each year."""
     
    # Prepare data
    seasonal_data = dates_df.groupby(TimeGrouper(freq='3M', closed='left')).sum()
    seasonal_data = seasonal_data.drop(seasonal_data.index[-1])
    
    # Count up 
    assert len(seasonal_data['count']) % 4.0 == 0, "Date range must ensure each season is equally represented"

    season_keys = {2: 'DJF', 5: 'MAM', 8: 'JJA', 11: 'SON'}
    season_counts = {}
    for i in range(0,4):
        month = seasonal_data.index[i].month
        season_counts[season_keys[month]] = seasonal_data['count'][i::4]
    
    # Plot
    start_year = season_counts['MAM'].index[0].year
    end_year = season_counts['MAM'].index[-1].year

    x = numpy.arange(start_year, end_year + 1)

    pdjf = ax.bar(x, season_counts['DJF'], color='yellow')
    pmam = ax.bar(x, season_counts['MAM'], color='orange', bottom=season_counts['DJF'])
    pjja = ax.bar(x, season_counts['JJA'], color='blue', bottom=season_counts['DJF'].as_matrix()+season_counts['MAM'].as_matrix())
    pson = ax.bar(x, season_counts['SON'], color='green', bottom=season_counts['DJF'].as_matrix()+season_counts['MAM'].as_matrix()+season_counts['JJA'].as_matrix())

    ax.legend( (pdjf[0], pmam[0], pjja[0], pson[0]), ('DJF', 'MAM', 'JJA', 'SON') )


def time_filter(df, start_date, end_date):
    """Remove times that are not within the start/end bounds."""

    datetime_start = datetime.strptime(start_date, '%Y-%m-%d')
    start_selection = dates_df.index >= datetime_start

    datetime_end = datetime.strptime(end_date, '%Y-%m-%d')
    end_selection = dates_df.index <= datetime_end

    combined_selection = start_selection & end_selection

    filtered_df = df[combined_selection] 

    return filtered_df


def fill_out_dates(df, start_date, end_date):
    """Put a zero entry in a pandas df for all missing dates."""

    date_range = pandas.date_range(start_dates, end_dates)
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


def main(inargs):
    """Run the program."""

    # Read the data into a pandas data frame   
    date_list, date_metadata = gio.read_dates(inargs.date_file)

    ones = numpy.ones(len(date_list))
    dates_df = pandas.DataFrame(ones, index=map(lambda x: datetime.strptime(x, '%Y-%m-%d'), date_list), columns=['count'])
    filtered_dates_df = time_filter(dates_df, inargs.start, inargs.end)

    # Fill out the date list for monthly and seasonal analyses
    monthly_filtered_dates_df = fill_out_dates(filtered_dates_df, inargs.start, inargs.end)
    
    seasonal_start, seasonal_end = get_seasonal_bounds(inargs.start, inargs.end)
    seasonal_filtered_dates_df = fill_out_dates(filtered_dates_df, seasonal_start, seasonal_end)

    
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
            plot_monthly_totals(ax, monthly_filtered_dates_df)
        elif plot_type == 'seasonal_values_stackplot':
            plot_seasonal_stackplot(ax, seasonal_filtered_dates_df, leg_loc=inargs.leg_loc)

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
