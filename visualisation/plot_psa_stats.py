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
import matplotlib.font_manager as font_manager

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

def plot_event_summary(df, phase_freq, ofile):
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


def plot_epochs(ax, df_subset, phase_freq, window, phase_res):
    """Add epoch lines."""

    year_subset = pandas.to_datetime(df_subset['time'].values).year
    early_bools = year_subset < 1991
    late_bools = year_subset > 2002 
    mid_bools = numpy.invert(early_bools + late_bools)

    df_subset_early = df_subset.loc[early_bools]
    df_subset_mid = df_subset.loc[mid_bools]
    df_subset_late = df_subset.loc[late_bools]

    hist_early, smooth_hist_early, bin_centers_early = phase_histogram(df_subset_early[phase_freq].values, window, phase_res)
    hist_mid, smooth_hist_mid, bin_centers_mid = phase_histogram(df_subset_mid[phase_freq].values, window, phase_res)
    hist_late, smooth_hist_late, bin_centers_late = phase_histogram(df_subset_late[phase_freq].values, window, phase_res)

    plot_histogram(ax, hist_early, smooth_hist_early, bin_centers_early, no_hist=True, label='1979-1990')
    plot_histogram(ax, hist_mid, smooth_hist_mid, bin_centers_mid, no_hist=True, label='1991-2002')
    plot_histogram(ax, hist_late, smooth_hist_late, bin_centers_late, no_hist=True,label='2003-2014')


def plot_phase_distribution(df, phase_freq, phase_res, window, ofile, seasonal=False, epochs=False):
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

        ax = plt.subplot(nrows, ncols, plot_num + 1)
        plt.sca(ax)

        if not season == 'annual':
            months_subset = pandas.to_datetime(df['time'].values).month
            bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
            df_subset = df.loc[bools_subset]
        else:
            df_subset = df

        hist, smooth_hist, bin_centers = phase_histogram(df_subset[phase_freq].values, window, phase_res)
        plot_histogram(ax, hist, smooth_hist, bin_centers, label='1979-2014')

        if epochs:
            plot_epochs(ax, df_subset, phase_freq, window, phase_res) 
    
        ax.set_title(season)
        font = font_manager.FontProperties(size='x-small')
        ax.legend(loc=1, prop=font)
        ax.set_ylabel('Frequency', fontsize='x-small')
        ax.set_xlabel('Longitude', fontsize='x-small')

    fig.savefig(ofile, bbox_inches='tight')


def phase_histogram(phase_data, smoothing_window, phase_res):
    """Calculate the phase data and bin it (i.e. create histogram)."""

    assert type(phase_data) == numpy.ndarray

    bin_edge_start = phase_data.min() - (phase_res / 2.)
    bin_edge_end = phase_data.max() + phase_res + (phase_res / 2.)
    bin_centers = numpy.arange(phase_data.min(), phase_data.max() + phase_res, phase_res)
    hist, bin_edges = numpy.histogram(phase_data, bins=numpy.arange(bin_edge_start, bin_edge_end, phase_res))
    smooth_hist = running_mean(hist, smoothing_window)

    return hist, smooth_hist, bin_centers


def plot_histogram(ax, hist, smooth_hist, bin_centers, no_hist=False, label=None):
    """Plot the phase histogram."""

    if not no_hist:
        ax.bar(bin_centers, hist, color='0.7')
    ax.plot(bin_centers, smooth_hist, label=label) 


def main(inargs):
    """Run program."""

    # Read the data and apply filters
    df = pandas.read_csv(inargs.infile)
    filtered_df = df.loc[df['event_duration'] >= inargs.min_duration]

    # Create the desired plot
    phase_freq = 'wave%i_phase' %(inargs.freq)
    if inargs.type == 'phase_distribution':
        plot_phase_distribution(filtered_df, phase_freq, inargs.phase_res, 
                                inargs.window, inargs.ofile,
                                seasonal=inargs.seasonal, epochs=inargs.epochs)
    elif inargs.type == 'event_summary':
        plot_event_summary(filtered_df, phase_freq, inargs.ofile)

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
    parser.add_argument("--epochs", action="store_true", default=False,
                        help="switch for plotting epoch lines on phase distribution plot [default: False]")

    args = parser.parse_args()            
    main(args)
