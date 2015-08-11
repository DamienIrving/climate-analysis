"""
Filename: plot_scatter.py
Author: Damien Irving, d.irving@student.unimelb.edu.au
Description: Create a scatterplot

"""

# Import general Python modules

import os, sys, pdb
import math
import numpy
import pandas, xray
from scipy.signal import argrelextrema
import argparse

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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

season_months = {'annual': None, 'DJF': (12, 1, 2), 'MAM': (3, 4, 5), 
                 'JJA': (6, 7, 8), 'SON': (9, 10, 11)}

def get_datetimes(darray, date_file):
    """Generate a list of datetimes common to darray and date_file."""

    if date_file:
        time_dim = map(str, darray['time'].values)
        date_list, date_metadata = gio.read_dates(date_file)
    
        match_dates, miss_dates = uconv.match_dates(date_list, time_dim)
        match_dates = map(numpy.datetime64, match_dates)

    else:
        match_dates = darray['time'].values
        date_metadata = None

    return match_dates, date_metadata


def find_phase(data, lon_axis):
    """Find the location of the first local minima within the search domain."""

    local_min_indexes = argrelextrema(data, numpy.less)
    local_min_lons = lon_axis[local_min_indexes]

    first_lon = next(lon for lon in local_min_lons if lon > 115)

    return first_lon


def running_mean(data, window):
    """Calculate the running mean.

    This is especially for the case where the start and end points join up.

    """
    
    temp = numpy.append(data, data)
    padded_data = numpy.append(temp, data)

    ds = pandas.Series(padded_data)
    runmean = pandas.rolling_mean(ds, window, center=True).values  #labels are right edge if center=False

    central_runmean = runmean[len(data):len(data)*2]

    return central_runmean


def phase_histogram(darray_selection, data_type, window):
    """Calculate the phase data and bin it (i.e. create histogram)."""

    if data_type == "waveform":
        lon_vals = darray_selection['longitude'].values
        lon_res = lon_vals[1] - lon_vals[0]
        assert darray_selection.dims == ('time', 'longitude')
        phase_vals = numpy.apply_along_axis(find_phase, -1, darray_selection.values, lon_vals)
    else:
        lon_res = 0.75
        phase_vals = darray_selection.values

    bin_edge_start = phase_vals.min() - (lon_res / 2.)
    bin_edge_end = phase_vals.max() + lon_res + (lon_res / 2.)
    bin_centers = numpy.arange(phase_vals.min(), phase_vals.max() + lon_res, lon_res)
    hist, bin_edges = numpy.histogram(phase_vals, bins=numpy.arange(bin_edge_start, bin_edge_end, lon_res))
    smooth_hist = running_mean(hist, window)

    return hist, smooth_hist, bin_centers


def plot_histogram(hist, smooth_hist, bin_centers, nrows, ncols, season, plotnum):
    """Plot the phase histogram."""

    ax = plt.subplot(nrows, ncols, plotnum)
    plt.sca(ax)

    ax.bar(bin_centers, hist, color='0.7')
    ax.plot(bin_centers, smooth_hist) 
    plt.title(season)
    ax.set_ylabel('Frequency', fontsize='x-small')
    ax.set_xlabel('Longitude', fontsize='x-small')


def main(inargs):
    """Run program."""

    # Read the data
    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.var)
    darray = dset_in[inargs.var]
    
    # Filter data so just the date_list dates remain
    dt_list, dt_list_metadata = get_datetimes(darray, inargs.date_file)
    darray_selection = darray.sel(time=dt_list)

    if inargs.seasonal:
        season_list = ['DJF', 'MAM', 'JJA', 'SON']
        nrows, ncols = 2, 2
        figure_size = (12, 10)
    else:
        season_list = ['annual']
        nrows, ncols = 1, 1
        figure_size = None

    fig = plt.figure(figsize=figure_size)
    for plot_num, season in enumerate(season_list):

        if not season == 'annual':
            months_subset = pandas.to_datetime(darray_selection['time'].values).month
            bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
            data_subset = darray_selection.loc[bools_subset]
        else:
            data_subset = darray_selection

        hist, smooth_hist, bin_centers = phase_histogram(data_subset, inargs.type, inargs.window)
        plot_histogram(hist, smooth_hist, bin_centers, nrows, ncols, season, plot_num + 1)	
    
    fig.savefig(inargs.ofile, bbox_inches='tight')

    metadata_dict = {inargs.infile: dset_in.attrs['history'],
                     inargs.date_file: dt_list_metadata}
    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:

author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot the phase information'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required data
    parser.add_argument("infile", type=str, help="Input file to extract phase info from")
    parser.add_argument("var", type=str, help="Variable to get phase info from")
    parser.add_argument("type", type=str, choices=("waveform", "number"), help="Type of input data")    
    parser.add_argument("date_file", type=str, help="Input file for the x-axis")
    parser.add_argument("ofile", type=str, help="Output file name")

    parser.add_argument("--seasonal", action="store_true", default=False,
                        help="switch for plotting the 4 seasons [default: False]")
    parser.add_argument("--window", type=int, default=10, 
                        help="Running mean window [default: 10]")

    
    args = parser.parse_args()            
    main(args)
