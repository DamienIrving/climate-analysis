"""
Filename:     calc_ocean_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the zonal and vertical mean ocean anomaly fields

"""

# Import general Python modules

import sys, os, pdb
import argparse, math
import numpy
import iris
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
    import spatial_weights
    import grids
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

history = []

vertical_layers = {'surface': [0, 50],
                   'shallow': [50, 350],
                   'middle': [350, 700],
                   'deep': [700, 2000],
                   'argo': [0, 2000]}

basins = {'atlantic': 2, 
          'pacific': 3,
          'indian': 5,
          'globe': 100}


def add_metadata(orig_atts, new_cube, standard_name, var_name, units):
    """Add metadata to the output cube.
    
    Name can be 'vertical_mean' or 'zonal_mean'
    
    """

    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    new_cube.standard_name = standard_name
    new_cube.long_name = standard_name.replace('_', ' ')
    new_cube.var_name = var_name
    new_cube.attributes = orig_atts  

    return new_cube


def calc_vertical_mean(cube, layer, coord_names, atts):
    """Calculate the vertical mean over a given depth range."""

    min_depth, max_depth = vertical_layers[layer]
    level_subset = gio.iris_vertical_constraint(min_depth, max_depth)
    cube_segment = cube.extract(level_subset)

    depth_axis = cube_segment.coord('depth')
    if depth_axis.units == 'm':
        vertical_weights = spatial_weights.calc_vertical_weights_1D(depth_axis, coord_names, cube_segment.shape)
    elif depth_axis.units == 'dbar':
        vertical_weights = spatial_weights.calc_vertical_weights_2D(depth_axis, cube_segment.coord('latitude'), coord_names, cube_segment.shape)

    vertical_mean_cube = cube_segment.collapsed(['depth'], iris.analysis.MEAN, weights=vertical_weights.astype(numpy.float32))   
    vertical_mean_cube.remove_coord('depth')
    vertical_mean_cube.data = vertical_mean_cube.data.astype(numpy.float32)
        
    units = str(cube.units)
    standard_name = 'vertical_mean_%s_%s' %(layer, vertical_mean_cube.standard_name)
    var_name = '%s_vm_%s'   %(vertical_mean_cube.var_name, layer)
    vertical_mean_cube = add_metadata(atts, vertical_mean_cube, standard_name, var_name, units)

    return vertical_mean_cube


def calc_zonal_mean(cube, basin_array, basin_name, atts):
    """Calculate the zonal mean for a given ocean basin."""

    if not basin_name == 'globe':  
        cube.data.mask = numpy.where((cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

    zonal_mean_cube = cube.collapsed('longitude', iris.analysis.MEAN)
    zonal_mean_cube.remove_coord('longitude')
    zonal_mean_cube.data = zonal_mean_cube.data.astype(numpy.float32)

    units = str(cube.units)
    standard_name = 'zonal_mean_%s_%s' %(basin_name, zonal_mean_cube.standard_name)
    var_name = '%s_zm_%s'   %(zonal_mean_cube.var_name, basin_name)
    zonal_mean_cube = add_metadata(atts, zonal_mean_cube, standard_name, var_name, units)

    return zonal_mean_cube


def create_basin_file(cube):
    """Create a basin file.

    For similarity with the CMIP5 basin file, in the output:
      Atlantic Ocean = 2
      Pacific Ocean = 3
      Indian Ocean = 5

    """

    pacific_bounds = [147, 294]
    indian_bounds = [23, 147]

    lat_axis = cube.coord('latitude').points
    lon_axis = uconv.adjust_lon_range(cube.coord('longitude').points, radians=False)

    lat_array = uconv.broadcast_array(lat_axis, 2, cube.shape)
    lon_array = uconv.broadcast_array(lon_axis, 3, cube.shape)

    basin_array = numpy.ones(cube.shape) * 2
    basin_array = numpy.where((lon_array >= pacific_bounds[0]) & (lon_array <= pacific_bounds[1]), 3, basin_array)
    basin_array = numpy.where((lon_array >= indian_bounds[0]) & (lon_array <= indian_bounds[1]), 5, basin_array)

    basin_array = numpy.where((basin_array == 3) & (lon_array >= 279) & (lat_array >= 10), 2, basin_array)
    basin_array = numpy.where((basin_array == 5) & (lon_array >= 121) & (lat_array >= 0), 3, basin_array)

    return basin_array


def read_climatology(climatology_file, variable):
    """Read the optional climatology data."""

    if climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(climatology_file, variable)
    else:
        climatology_cube = None

    return climatology_cube


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def set_attributes(inargs, data_cube, climatology_cube):
    """Set the attributes for the output cube."""
    
    atts = data_cube.attributes

    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0]
    if climatology_cube:                  
        infile_history[inargs.climatology_file] = climatology_cube.attributes['history']

    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def main(inargs):
    """Run the program."""

    climatology_cube = read_climatology(inargs.climatology_file, inargs.var)
    data_cubes = iris.load(inargs.infiles, inargs.var, callback=save_history)
    equalise_attributes(data_cubes)
    atts = set_attributes(inargs, data_cubes[0], climatology_cube)

    out_cubes = []
    for data_cube in data_cubes:

        if climatology_cube:
            data_cube = data_cube - climatology_cube
        data_cube, coord_names = grids.curvilinear_to_rectilinear(data_cube)

        assert coord_names == ['time', 'depth', 'latitude', 'longitude']
        depth_axis = data_cube.coord('depth')
        assert depth_axis.units in ['m', 'dbar'], "Unrecognised depth axis units"

        out_list = iris.cube.CubeList([])

        for layer in vertical_layers.keys():
            out_list.append(calc_vertical_mean(data_cube, layer, coord_names, atts))

        basin_array = create_basin_file(data_cube)
        for basin in basins.keys():
            out_list.append(calc_zonal_mean(data_cube.copy(), basin_array, basin, atts))

        out_cubes.append(out_list.concatenate())

    cube_list = []
    nvars = len(vertical_layers.keys()) + len(basins.keys())
    for var_index in range(0, nvars):
        temp_list = []
        for infile_index in range(0, len(inargs.infiles)):
            temp_list.append(out_cubes[infile_index][var_index])
        
        temp_list = iris.cube.CubeList(temp_list)     
        cube_list.append(temp_list.concatenate_cube())
    
    cube_list = iris.cube.CubeList(cube_list)
    assert cube_list[0].data.dtype == numpy.float32
    iris.save(cube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate the zonal and vertical mean ocean anomaly fields'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files")
    parser.add_argument("var", type=str, help="Input variable name (the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--climatology_file", type=str, default=None, 
                        help="Input climatology file (required if input data not already anomaly)")
        
    args = parser.parse_args()             
    main(args)
