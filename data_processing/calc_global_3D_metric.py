"""
Filename:     calc_global_3D_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate global metric from 3D (lat, lon, lev) data

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.analysis.cartography
from iris.experimental.equalise_cubes import equalise_attributes

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
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def read_volume(volume_file, level_constraint):
    """Read the optional volume file."""

    if volume_file:
        volume_cube = iris.load_cube(volume_file, level_constraint)
    else:
        volume_cube = None

    return volume_cube


def set_attributes(inargs, data_cube, volume_cube):
    """Set the attributes for the output cube."""
    
    atts = data_cube.attributes

    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0] 
 
    if volume_cube:                  
        infile_history[inargs.volume_file] = volume_cube.attributes['history']
    
    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def get_volume_weights(cube, volume_cube):
    """Get volume weights for averaging"""

    assert volume_cube

    volume_weights = uconv.broadcast_array(volume_cube.data, [1, 3], cube.shape)

    return volume_weights


def calc_global_mean(cube, grid_volumes, spatial_dims, atts):
    """Calculate global mean."""

    global_mean = cube.collapsed(spatial_dims, iris.analysis.MEAN, weights=grid_volumes)
    for dim in spatial_dims:
        global_mean.remove_coord(dim)

    global_mean.attributes = atts

    return global_mean


def calc_mean_abs(cube, grid_volumes, spatial_dims, atts):
    """Calculate the global mean absolute value"""

    abs_val = (cube ** 2) ** 0.5
    abs_val.metadata = cube.metadata

    global_mean_abs = abs_val.collapsed(spatial_dims, iris.analysis.MEAN, weights=grid_volumes)
    for dim in spatial_dims:
        global_mean_abs.remove_coord(dim)
    
    global_mean_abs.attributes = atts

    return global_mean_abs 


def smooth_data(cube, smooth_type):
    """Apply temporal smoothing to a data cube."""

    assert smooth_type in ['annual', 'annual_running_mean']

    if smooth_type == 'annual_running_mean':
        cube = cube.rolling_window('time', iris.analysis.MEAN, 12)
    elif smooth_type == 'annual':
        cube = timeseries.convert_to_annual(cube)   

    return cube


def main(inargs):
    """Run the program."""

    if inargs.depth:
        level_constraint = iris.Constraint(depth=inargs.depth)
    else:
        level_constraint = iris.Constraint()

    with iris.FUTURE.context(cell_datetime_objects=True):
        data_cubes = iris.load(inargs.infiles, inargs.var & level_constraint, callback=save_history)
        equalise_attributes(data_cubes)
        iris.util.unify_time_units(data_cubes)
    volume_cube = read_volume(inargs.volume_file, level_constraint)
    atts = set_attributes(inargs, data_cubes[0], volume_cube)

    out_cubes = []
    for cube in data_cubes:
        dim_coord_names = [coord.name() for coord in cube.dim_coords]
        assert dim_coord_names[0] == 'time'
        spatial_dims = dim_coord_names[1:]
        assert len(spatial_dims) == 3

        if inargs.smoothing:
            cube = smooth_data(cube, inargs.smoothing)
            volume_weights = get_volume_weights(cube, volume_cube)

        if inargs.metric == 'mean':
            metric = calc_global_mean(cube, volume_weights, spatial_dims, atts)
        elif inargs.metric == 'mean-abs':
            metric = calc_mean_abs(cube, volume_weights, spatial_dims, atts)

        out_cubes.append(metric)

    out_list = iris.cube.CubeList(out_cubes)     
    out_cube = out_list.concatenate_cube()
    #cube = gio.check_time_units(cube)

    iris.save(out_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate a global metric from 3D (lat, lon, lev)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files (can merge on time)")
    parser.add_argument("var", type=str, help="Input variable name (i.e. the standard_name)")
    parser.add_argument("metric", type=str, choices=('mean', 'mean-abs'), help="Metric to calculate")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--volume_file", type=str, default=None, 
                        help="Input cell volume file")

    parser.add_argument("--smoothing", type=str, choices=('annual', 'annual_running_mean'), default=None, 
                        help="Apply smoothing to data")

    parser.add_argument("--depth", type=float, default=None, 
                        help="Level selection")

    args = parser.parse_args()            

    main(args)
