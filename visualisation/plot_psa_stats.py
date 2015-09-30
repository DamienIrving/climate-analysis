# Import general Python modules

import os, sys, pdb
import math
import numpy
import pandas
import argparse
from scipy import stats

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

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

def plot_event_summary(df, phase_freq, min_duration, ofile):
    """Line graph showing phase/amplitude throughout the lifecycle of each PSA event."""

    amp_max = df['env_max'].max()
    amp_min = df['env_max'].min()
    duration_max =  df['event_duration'].max()
    event_numbers = numpy.unique(df['event_number'].values)

    # Create the plot
    fig = plt.figure(figsize=(8,11))
    for event in event_numbers:
        phase_data = df['event_phase'].loc[df['event_number'] == event].values
        amp_data = df['env_max'].loc[df['event_number'] == event].values
        gradient = df['event_gradient'].loc[df['event_number'] == event].values[0]
        x_axis = numpy.arange(0, len(phase_data))

        if gradient > 0.2:
            cmap = 'Reds'
        elif gradient < -0.2:
            cmap = 'Blues'
        else:
            cmap = 'Greys'

        points = numpy.array([x_axis, phase_data]).T.reshape(-1, 1, 2)
        segments = numpy.concatenate([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments, cmap=plt.get_cmap(cmap), norm=plt.Normalize(amp_min, amp_max))
        lc.set_array(amp_data)
        lc.set_linewidth(3)
        plt.gca().add_collection(lc)

    plt.xlim(0, duration_max)
    plt.ylim(0, 83)

    plt.xlabel('day')
    plt.ylabel(phase_freq)
   
    plt.savefig(ofile, bbox_inches='tight')


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


def plot_phase_distribution(df, phase_freq, phase_res, window, seasonal=False):
    """Plot a phase distribution histogram."""    
    
    if seasonal:
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
            months_subset = pandas.to_datetime(df['time'].values).month
            bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
            df_subset = df.loc[bools_subset]
        else:
            df_subset = df

        hist, smooth_hist, bin_centers = phase_histogram(df_subset[phase_freq].values, window)
        plot_histogram(hist, smooth_hist, bin_centers, nrows, ncols, season, plot_num + 1)	
    
    fig.savefig(inargs.ofile, bbox_inches='tight')


def phase_histogram(phase_data, smoothing_window, phase_res=1.0):
    """Calculate the phase data and bin it (i.e. create histogram)."""

    assert type(phase_data) == numpy.ndarray

    bin_edge_start = phase_data.min() - (phase_res / 2.)
    bin_edge_end = phase_data.max() + phase_res + (phase_res / 2.)
    bin_centers = numpy.arange(phase_data.min(), phase_data.max() + phase_res, phase_res)
    hist, bin_edges = numpy.histogram(phase_data, bins=numpy.arange(bin_edge_start, bin_edge_end, phase_res))
    smooth_hist = running_mean(hist, smoothing_window)

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

    # Read the data and apply filters
    df = pandas.read_csv(inargs.infile)
    filtered_df = df.loc[df['event_duration'] >= inargs.min_duration]

    # Create the desired plot
    phase_freq = 'wave%i_phase' %(inargs.freq)
    if inargs.type == 'phase_distribution':
        plot_phase_distribution(filtered_df, phase_freq, inargs.phase_res, 
                                inargs.window, seasonal=inargs.seasonal)
    elif inargs.type == 'event_summary':
        plot_event_summary(filtered_df, phase_freq, inargs.min_duration, inargs.ofile)

    # Sort out metadata
    file_body = inargs.infile.split('.')[0]
    with open (file_body+'.met', 'r') as metfile:
        date_metadata=metfile.read()
    metadata_dict = {inargs.infile: date_metadata}
    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:

author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot PSA pattern statistics'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required data
    parser.add_argument("infile", type=str, help="PSA statistics file from psa_date_list.py")
    parser.add_argument("type", type=str, choices=("phase_distribution", "event_summary"), 
                        help="Desired plot")    
    parser.add_argument("ofile", type=str, help="Output file name")

    parser.add_argument("--freq", type=int, default=6, 
                        help="Frequency to use to indicate the wave phase [default: 6]")
    parser.add_argument("--phase_res", type=float, default=1.0, 
                        help="Phase resolution (e.g. if phase data is deg lon, res is spacing between lons [default: 1.0]")
    parser.add_argument("--window", type=int, default=10, 
                        help="Running mean window [default: 10]")
    parser.add_argument("--min_duration", type=int, default=0, 
                        help="Minimum event duration [default: 0]")

    parser.add_argument("--seasonal", action="store_true", default=False,
                        help="switch for plotting the 4 seasons for phase distribution plot [default: False]")

    args = parser.parse_args()            
    main(args)
