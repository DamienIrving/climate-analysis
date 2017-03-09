"""
Filename:     plot_ocean_distribution.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the volumetric (or area-metric) distribution

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.equalise_cubes import equalise_attributes
import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn

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

history = []
colors = {'historicalGHG': 'red',
          'historicalAA': 'blue'}
 

def read_spatial_file(spatial_file):
    """Read a spatial file (i.e. area or volume file)."""

    if spatial_file:
        cube = iris.load_cube(spatial_file)
    else:
        cube = None

    return cube


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between Input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def write_met_file(inargs, spatial_cube, outfile):
    """Write the output metadata file."""
    
    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0]

    if spatial_cube:                  
        infile_history[inargs.spatial_file] = spatial_cube.attributes['history']

    gio.write_metadata(outfile, file_info=infile_history)


def concat_cubes(cube_list):
    """Concatenate an iris cube list."""

    iris.util.unify_time_units(cube_list)
    cube = cube_list.concatenate_cube()
    cube = gio.check_time_units(cube)

    return cube


def calc_histogram(data_cube, spatial_cube):
    """Calculate the histogram."""

    dim_coord_names = [coord.name() for coord in data_cube.dim_coords]
    assert dim_coord_names[0] == 'time'
    spatial_dims = dim_coord_names[1:]
  
    assert len(spatial_dims) in [2, 3]
    if len(spatial_dims) == 2:
        axis_index = [1, 2]
        spatial_type = 'area'
    elif len(spatial_dims) == 3:
        axis_index = [1, 3]
        spatial_type = 'volume'

    broadcast_spatial_data = uconv.broadcast_array(spatial_cube.data, axis_index, data_cube.shape)

    bin_edges = numpy.arange(25, 45, 0.2)
    hist, bin_edges = numpy.histogram(data_cube.data.compressed(), bins=bin_edges, normed=True, weights=broadcast_spatial_data.compressed())

    return hist, bin_edges


def create_upper_plot(ax, hist_dict, left_edges, experiment):
    """Create an upper panel plot (shows AA and GHG distributions)"""

    ax.bar(left_edges, hist_dict[(experiment, 'early')],
           width=0.2, color='blue', label='early', alpha=0.3)

    ax.bar(left_edges, hist_dict[(experiment, 'late')],
           width=0.2, color='red', label='late', alpha=0.3)

    #ax.title = experiment
 

def create_lower_plot(ax, hist_dict, left_edges, experiment):
    """Create a lower panel plot (shows AA and GHG difference)""" 

    ax.bar(left_edges, hist_dict[(experiment, 'diff')],
           width=0.2, color='black', label='late - early', alpha=0.3)


def main(inargs):
    """Run the program."""

    data_files = {'historicalGHG': inargs.ghg_files,
                  'historicalAA': inargs.aa_files} 
    spatial_files = {'historicalGHG': inargs.ghg_spatial_file,
                     'historicalAA': inargs.aa_spatial_file}
    time_periods = {'early': inargs.early_period,
                    'late': inargs.late_period}

    hist = {}
    for experiment in ['historicalGHG', 'historicalAA']:
        spatial_cube = read_spatial_file(spatial_files[experiment])
        with iris.FUTURE.context(cell_datetime_objects=True):
            data_cubes = iris.load(data_files[experiment], inargs.var, callback=save_history)
            equalise_attributes(data_cubes)
            for period_name, period_dates in time_periods.iteritems():
                time_constraint = gio.get_time_constraint(period_dates)
                data_cube_list = data_cubes.extract(time_constraint)
                data_cube = concat_cubes(data_cube_list)
                hist[(experiment, period_name)], bin_edges = calc_histogram(data_cube, spatial_cube)
        hist[(experiment, 'diff')] = hist[(experiment, 'late')] - hist[(experiment, 'early')]

    
    fig = plt.figure(figsize=[15, 10])
    gs = gridspec.GridSpec(2, 2, height_ratios=[4,1])

    ax0 = plt.subplot(gs[0])
    #plt.sca(ax0)
    create_upper_plot(ax0, hist, bin_edges[0:-1], 'historicalAA')

    ax1 = plt.subplot(gs[1])
    create_upper_plot(ax1, hist, bin_edges[0:-1], 'historicalGHG')

    ax2 = plt.subplot(gs[2])
    create_lower_plot(ax2, hist, bin_edges[0:-1], 'historicalAA')

    ax3 = plt.subplot(gs[3])
    create_lower_plot(ax3, hist, bin_edges[0:-1], 'historicalGHG')

#    plt.title('Salinity distribution')
#    plt.xlabel('Salinity (g/kg)')
#    plt.ylabel(spatial_type + ' density')
#    plt.legend()
#    plt.xlim(27, 41)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    #write_met_file(inargs, spatial_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Plot the volumetric (or area-metric) distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("var", type=str, help="Input variable name (the standard_name)")

    parser.add_argument("--aa_files", type=str, nargs='*',
                        help="Input historicalAA data files")
    parser.add_argument("--ghg_files", type=str, nargs='*',
                        help="Input historicalGHG data files")
    parser.add_argument("--aa_spatial_file", type=str, default=None, 
                        help="Input historicalAA volume file (or area file for surface variable)")
    parser.add_argument("--ghg_spatial_file", type=str, default=None, 
                        help="Input historicalGHG volume file (or area file for surface variable)")

    parser.add_argument("--early_period", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1850-01-01', '1869-12-31'),
                        help="Time bounds for the early period")
    parser.add_argument("--late_period", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=('1986-01-01', '2005-12-31'),
                        help="Time bounds for the late period")

    args = parser.parse_args()             
    main(args)
