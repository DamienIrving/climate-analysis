"""
Filename:     plot_ohc_trend.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the spatial trend in ocean heat content

"""

# Import general Python modules

import sys, os, pdb
import argparse

import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn
import numpy

import iris
import iris.quickplot as qplt
from iris.util import rolling_window
from iris.analysis import Aggregator
from scipy import stats


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

def plot_timeseries(globe_cube, sthext_cube, notsthext_cube, model, experiment, run, gs):
    """Blah."""

    ax = plt.subplot(gs[0])
    plt.sca(ax)

    qplt.plot(globe_cube.coord('time'), globe_cube, label='global')
    qplt.plot(sthext_cube.coord('time'), sthext_cube, label='southern extratropics')
    qplt.plot(notsthext_cube.coord('time'), notsthext_cube, label='not southern extratropics')

    plt.legend(loc='best')
    plt.title('Ocean heat content, %s, %s, %s' %(model, experiment, run))
    plt.ylabel('Ocean heat content (%s)' %(globe_cube.units))


def plot_trend_distribution(trend_data, gs):
    """ """

    ax = plt.subplot(gs[1])
    plt.sca(ax)

    seaborn.distplot(trend_data)


def calc_slope(y, x):
    """Calculate the slope from linear regression."""
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
    
    return slope


def linear_trend(data, axis, window_size):
    """Calculate the linear trend for specified running window."""

    window_array = rolling_window(data, window=window_size, axis=axis)

    x_axis = numpy.arange(0, window_size)    
    trend = numpy.apply_along_axis(calc_slope, -1, window_array, x_axis)
    
    return trend
    

def calc_diff_trends(sthext_cube, notsthext_cube, window=12):
    """Calculate trends in difference between southern extratropics and rest of globe.

    A window of 12 years matches the length of the Argo record.

    """

    diff = sthext_cube - notsthext_cube
    trends = linear_trend(diff.data, 0, window)

    return trends


def get_file_details(filename):
    """Extract details from filename."""

    name = filename.split('/')[-1]
    components = name.split('_')
    model, experiment, run = components[2:5]

    return model, experiment, run


def main(inargs):
    """Run the program."""
    
    model, experiment, run = get_file_details(inargs.infile)

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    data_dict = {}
    with iris.FUTURE.context(cell_datetime_objects=True):
        data_dict[(model, experiment, run, 'globe')] = iris.load_cube(inargs.infile, 'ocean heat content globe' & time_constraint)
        data_dict[(model, experiment, run, 'sthext')] = iris.load_cube(inargs.infile, 'ocean heat content southern extratropics' & time_constraint)
        data_dict[(model, experiment, run, 'notsthext')] = iris.load_cube(inargs.infile, 'ocean heat content outside southern extratropics' & time_constraint)

    # Calculate the annual mean timeseries
    for key, value in data_dict.iteritems():
        data_dict[key] = value.rolling_window('time', iris.analysis.MEAN, 12)

    # Calculate trends in 
    diff_trends = calc_diff_trends(data_dict[(model, experiment, run, 'sthext')], data_dict[(model, experiment, run, 'notsthext')])

    # Plot
    fig = plt.figure(figsize=[15, 3])
    gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1]) 

    plot_timeseries(data_dict[(model, experiment, run, 'globe')], 
                    data_dict[(model, experiment, run, 'sthext')], 
                    data_dict[(model, experiment, run, 'notsthext')],
                    model, experiment, run, gs)
    plot_trend_distribution(diff_trends, gs)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    infile_history = data_dict[(model, experiment, run, 'globe')].attributes['history']
    gio.write_metadata(inargs.outfile, file_info={inargs.outfile:infile_history})


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Plot the spatial trend in ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input ocean heat content file")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            
    main(args)
