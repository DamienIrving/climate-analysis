"""
Filename:     plot_ohc_metric_timeseries.py
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

def plot_timeseries(cube_dict, user_regions, title, tex_units, ref_region=None):
    """Create the timeseries plot."""

    region_dict = {'globe': ('globe', 'black', '--'),
                   'globe60': ('globe (60S - 60N)', 'black', '-'),
                   'tropics': ('tropics (20S to 20N)', 'purple', '-'),
                   'ne': ('northern extratropics (north of 20N)', 'red', '--'),
                   'ne60': ('northern extratropics (20N - 60N)', 'red', '-'),
                   'nh60': ('northern hemisphere (to 60N)', 'red', '-.'),
                   'se': ('southern extratropics (south of 20S)', 'blue', '--'),
                   'se60': ('southern extratropics (60S - 20S)', 'blue', '-'),
                   'sh60': ('southern hemisphere (to 60S)', 'blue', '-.'),
                   'ose': ('outside southern extratropics (north of 20S)', '#cc0066', '-.'),
                   'ose60': ('outside southern extratropics (20S - 60N)', '#cc0066', '--')}

    for region in user_regions:
        name, color, style = region_dict[region]
        cube = cube_dict[name]
        qplt.plot(cube.coord('time'), cube, label=name, color=color, linestyle=style)

    plt.legend(loc='best')
    plt.title(title)
    if ref_region:
        ylabel = '%s equivalent ocean heat content (%s)' %(region_dict[ref_region][0], tex_units)
    else:
        ylabel = 'ocean heat content (%s)' %(tex_units)
    plt.ylabel(ylabel)
    plt.xlabel('year')


def set_title(data_dict, inargs, plotnum):
    """Set the title for the plot"""

    if inargs.argo:
        title = 'Argo'
    else:
        model, experiment, run = gio.get_cmip5_file_details(data_dict['globe'])
        if inargs.experiment:
            experiment = inargs.experiment[plotnum].replace('_',' ')
        if inargs.run:
            run = inargs.run[plotnum]
                  
        title = '%s, %s, %s' %(model, experiment, run)

    return title


def check_inputs(inargs):
    """Check the validity of the input arguments."""

    assert len(inargs.infiles) <= inargs.nrows * inargs.ncols
    if inargs.experiment:
        assert len(inargs.infiles) == len(inargs.experiment)
    if inargs.run:
        assert len(inargs.infiles) == len(inargs.run)


def main(inargs):
    """Run the program."""

    check_inputs(inargs)

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    metadata_dict = {}
    fig = plt.figure(figsize=inargs.figsize)
    if not inargs.figsize:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    for plotnum, infile in enumerate(inargs.infiles):

        if not os.path.isfile(infile):
            continue

        data_dict = {}
        with iris.FUTURE.context(cell_datetime_objects=True):
            data_dict['globe'] = iris.load_cube(infile, 'ocean heat content globe' & time_constraint)
            data_dict['globe (60S - 60N)'] = iris.load_cube(infile, 'ocean heat content globe60' & time_constraint)
            data_dict['southern extratropics (south of 20S)'] = iris.load_cube(infile, 'ocean heat content southern extratropics' & time_constraint)
            data_dict['northern extratropics (north of 20N)'] = iris.load_cube(infile, 'ocean heat content northern extratropics' & time_constraint)
            data_dict['southern extratropics (60S - 20S)'] = iris.load_cube(infile, 'ocean heat content southern extratropics60' & time_constraint)
            data_dict['northern extratropics (20N - 60N)'] = iris.load_cube(infile, 'ocean heat content northern extratropics60' & time_constraint)
            data_dict['outside southern extratropics (north of 20S)'] = iris.load_cube(infile, 'ocean heat content outside southern extratropics' & time_constraint)
            data_dict['outside southern extratropics (20S - 60N)'] = iris.load_cube(infile, 'ocean heat content outside southern extratropics60' & time_constraint)
            data_dict['southern hemisphere (to 60S)'] = iris.load_cube(infile, 'ocean heat content sh60' & time_constraint)
            data_dict['northern hemisphere (to 60N)'] = iris.load_cube(infile, 'ocean heat content nh60' & time_constraint)
            data_dict['tropics (20S to 20N)'] = iris.load_cube(infile, 'ocean heat content tropics' & time_constraint)
        metadata_dict[infile] = data_dict['globe'].attributes['history']

        # Calculate the annual mean timeseries
        for key, value in data_dict.iteritems():
            data_dict[key] = value.rolling_window('time', iris.analysis.MEAN, 12)
        tex_units, exponent = uconv.units_info(str(value.units))

        # Generate plot
        title = set_title(data_dict, inargs, plotnum)
        ax = plt.subplot(inargs.nrows, inargs.ncols, plotnum + 1)
        plt.sca(ax)
        plot_timeseries(data_dict, inargs.regions, title, tex_units, ref_region=inargs.ref_region)
        
    # Write output
    plt.tight_layout(pad=0.4, w_pad=2.0, h_pad=2.0)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


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

    parser.add_argument("infiles", type=str, nargs='*', help="Input temperature metric files (write blank for empty plots on grid)")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--ref_region", type=str, default=None, 
                        help="Metrics are scaled to the volume of this region")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--regions", type=str, nargs='*', default=('globe60', 'ne60', 'tropics', 'se60', 'ose60'), 
                        help="regions to plot")

    parser.add_argument("--nrows", type=int, default=1, 
                        help="number of rows in the entire grid of plots")
    parser.add_argument("--ncols", type=int, default=1,
                        help="number of columns in the entire grid of plots")
    parser.add_argument("--figsize", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
    parser.add_argument("--experiment", type=str, nargs='*', default=None,
                        help="overwrite the default experiment in the plot header (write blank for empty plots on grid)")
    parser.add_argument("--run", type=str, nargs='*', default=None,
                        help="overwrite the default run in the plot header (write blank for empty plots on grid)")


    parser.add_argument("--argo", action="store_true", default=False,
                        help="switch for indicated an Argo rather than CMIP5 input file [default: False]")


    args = parser.parse_args()            
    main(args)
