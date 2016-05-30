"""
Filename:     plot_ocean_temperature_metric_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot timeseries of various ocean temperature metrics
              for a single model/experiment/run

"""

# Import general Python modules

import sys, os, pdb
import argparse

import matplotlib.pyplot as plt
import seaborn
import numpy

import iris
import iris.quickplot as qplt
from iris.util import rolling_window


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

def plot_timeseries(globe_cube, sthext_cube, notsthext_cube, 
                    model, experiment, run, tex_units):
    """Create the timeseries plot."""

    qplt.plot(globe_cube.coord('time'), globe_cube, label='global')
    qplt.plot(sthext_cube.coord('time'), sthext_cube, label='southern extratropics')
    qplt.plot(notsthext_cube.coord('time'), notsthext_cube, label='outside southern extratropics')

    plt.legend(loc='best')
    plt.title('%s, %s, %s' %(model, experiment, run))
    plt.ylabel('Ocean heat content (%s)' %(tex_units))
    plt.xlabel('Year')


def main(inargs):
    """Run the program."""
    
    model, experiment, run = gio.get_cmip5_file_details(inargs.infile)

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    data_dict = {}
    with iris.FUTURE.context(cell_datetime_objects=True):
        data_dict['globe'] = iris.load_cube(inargs.infile, 'ocean heat content globe' & time_constraint)
        data_dict['sthext'] = iris.load_cube(inargs.infile, 'ocean heat content southern extratropics' & time_constraint)
        data_dict['notsthext'] = iris.load_cube(inargs.infile, 'ocean heat content outside southern extratropics' & time_constraint)

    # Calculate the annual mean timeseries
    for key, value in data_dict.iteritems():
        data_dict[key] = value.rolling_window('time', iris.analysis.MEAN, 12)
    tex_units, exponent = uconv.units_info(str(value.units))

    # Plot
    fig = plt.figure() #figsize=[15, 7])
    
    plot_timeseries(data_dict['globe'], 
                    data_dict['sthext'], 
                    data_dict['notsthext'],
                    model, experiment, run, tex_units)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    infile_history = data_dict['globe'].attributes['history']
    gio.write_metadata(inargs.outfile, file_info={inargs.outfile:infile_history})


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Plot timeseries of various ocean temperature metrics'
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
