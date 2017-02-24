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
    import kde
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

history = []

plot_details = {}
plot_details['early'] = 'blue'
plot_details['late'] = 'red' 

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


def plot_distribution(data_cube, spatial_cube, period):
    """Plot the spatial cube."""

    color = plot_details[period]

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

    bins = numpy.arange(27, 41, 0.25)
    plt.hist(data_cube.data.compressed(), weights=broadcast_spatial_data.compressed(),
             bins=bins, normed=True,
             color=color, label=period, alpha=0.2)  # histtype='stepfilled'

    pdf = kde.gaussian_kde(data_cube.data.compressed(), weights=broadcast_spatial_data.compressed())
    x = numpy.arange(27, 41, 0.25)
    y = pdf(x)
    plt.plot(x, y, color=color) #label='weighted kde'
    
    return spatial_type
 

def main(inargs):
    """Run the program."""

    spatial_cube = read_spatial_file(inargs.spatial_file)

    for file_group in inargs.file_group:
        with iris.FUTURE.context(cell_datetime_objects=True):
            data_cubes = iris.load(file_group, inargs.var, callback=save_history)
            equalise_attributes(data_cubes)
            for period in inargs.period:
                time_constraint = gio.get_time_constraint(period)
                data_cube_list = data_cubes.extract(time_constraint)
                data_cube = concat_cubes(data_cube_list)
                spatial_type = plot_distribution(data_cube, spatial_cube, 'late')

    plt.title('Salinity distribution')
    plt.xlabel('Salinity (g/kg)')
    plt.ylabel(spatial_type + ' density')
    plt.legend()
    plt.xlim(27, 41)

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

    parser.add_argument("--file_group", type=str, nargs='*', action='append',
                        help="Input data files")
    parser.add_argument("--spatial_file", type=str, default=None, 
                        help="Input volume file (or area file for surface variable)")
    parser.add_argument("--period", type=str, nargs=2, action='append', metavar=('START_DATE', 'END_DATE'),
                        help="Time bounds for a period")

        
    args = parser.parse_args()             
    main(args)
