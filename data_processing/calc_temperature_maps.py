"""
Filename:     calc_temperature_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the zonal and vertical mean temperature anomaly fields

"""

# Import general Python modules

import sys, os, pdb
import argparse, math
import numpy
import iris
from iris.experimental.regrid import regrid_weighted_curvilinear_to_rectilinear
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

history = []

vertical_layers = {'surface': [0, 50],
                   'shallow': [50, 350],
                   'middle': [350, 700],
                   'deep': [700, 2000]}

basins = {'atlantic': 2, 
          'pacific': 3,
          'indian': 5}


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


def calc_vertical_mean(cube, weights, inargs):
    """Calculate the weighted vertical mean temperature"""

    vertical_mean = cube.collapsed(['depth'], iris.analysis.MEAN, weights=weights)   
    vertical_mean.remove_coord('depth')

    return vertical_mean


def calc_zonal_mean(cube, inargs):
    """Calculate the zonal mean"""

    zonal_mean = cube.collapsed('longitude', iris.analysis.MEAN)
    zonal_mean.remove_coord('longitude')

    return zonal_mean


def check_coord_names(cube, coord_names):
    """Remove specified coordinate name.

    The iris standard names for lat/lon coordinates are:
      latitude, grid_latitude, longitude, grid_longitude

    If a cube uses one for the dimension coordinate and the 
      other for the auxillary coordinate, the 
      regrid_weighted_curvilinear_to_rectilinear method won't work

    """

    if 'grid_latitude' in coord_names:
        cube.coord('grid_latitude').standard_name = None
        coord_names = [coord.name() for coord in cube.dim_coords]
    if 'grid_longitude' in coord_names:
        cube.coord('grid_longitude').standard_name = None
        coord_names = [coord.name() for coord in cube.dim_coords]

    return cube, coord_names


def curvilinear_to_rectilinear(cube):
    """Regrid curvilinear data to a rectilinear grid if necessary."""

    coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]

    if aux_coord_names:

        assert aux_coord_names == ['latitude', 'longitude']

        # Create target grid
        lats = numpy.arange(-90, 91, 1)
        lons = numpy.arange(0, 360, 1)
        target_grid_cube = make_grid(lats, lons)

        # Interate over slices (experimental regridder only works on 2D slices)
        cube, coord_names =  check_coord_names(cube, coord_names)
        slice_dims = coord_names
        slice_dims.remove('time')
        slice_dims.remove('depth')
        cube_list = []
        for i, cube_slice in enumerate(cube.slices(slice_dims)):
            weights = numpy.ones(cube_slice.shape)
            regridded_cube = regrid_weighted_curvilinear_to_rectilinear(cube_slice, weights, target_grid_cube)
            cube_list.append(regridded_cube)

        new_cube = iris.cube.CubeList(cube_list)
        new_cube = new_cube.merge_cube()
        coord_names = [coord.name() for coord in new_cube.dim_coords]

    else:

        new_cube = cube
    
    return new_cube, coord_names


def make_grid(lat_values, lon_values):
    """Make a dummy cube with desired grid."""
       
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=None)
    longitude = iris.coords.DimCoord(lon_values,                    
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=None)

    dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])

    new_cube.coord('longitude').guess_bounds()
    new_cube.coord('latitude').guess_bounds()

    return new_cube


def read_climatology(climatology_file, variable, level_subset):
    """Read the optional climatology data."""

    if climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(climatology_file, variable & level_subset)
    else:
        climatology_cube = None

    return climatology_cube


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def set_attributes(inargs, temperature_cube, climatology_cube):
    """Set the attributes for the output cube."""
    
    atts = temperature_cube.attributes

    lev_coord = temperature_cube.coord('depth')
    bounds_info = gio.vertical_bounds_text(lev_coord.points, inargs.min_depth, inargs.max_depth)
    depth_text = 'OHC integrated over %s' %(bounds_info)
    atts['depth_bounds'] = depth_text

    infile_history = {}
    infile_history[inargs.temperature_files[0]] = history[0]
    if climatology_cube:                  
        infile_history[inargs.climatology_file] = climatology_cube.attributes['history']

    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def calc_vertical_mean(cube, layer, coord_names):
    """Calculate the vertical mean over a given depth range."""

    min_depth, max_depth = vertical_layers[layer]
    level_subset = gio.iris_vertical_constraint(min_depth, max_depth)
    cube_segment = cube.extract(level_subset)

    depth_axis = cube_segment.coord('depth')
    if depth_axis.units == 'm':
        vertical_weights = spatial_weights.calc_vertical_weights_1D(depth_axis, coord_names, cube_segment.shape)
    elif depth_axis.units == 'dbar':
        vertical_weights = spatial_weights.calc_vertical_weights_2D(depth_axis, cube_segment.coord('latitude'), coord_names, cube_segment.shape)

    vertical_mean_cube = calc_vertical_mean(cube_segment, vertical_weights.astype(numpy.float32), inargs)
    vertical_mean_cube.data = vertical_mean_cube.data.astype(numpy.float32)
        
    units = str(cube.units)
    standard_name = 'vertical_mean_%s_%s' %(layer, vertical_mean_cube.standard_name)
    var_name = '%s_vm_%s'   %(vertical_mean_cube.var_name, layer)
    vertical_mean_cube = add_metadata(atts, vertical_mean_cube, standard_name, var_name, units)

    return vertical_mean_cube


def create_basin_file(cube):
    """Create a basin file.

    For similarity with the CMIP5 basin file, in the output:
      Atlantic Ocean = 2
      Pacific Ocean = 3
      Indian Ocean = 5

    """

    atlantic_bounds = [114, 203]
    indian_bounds = [203, 327]

    lat_axis = cube.coord('latitude').points
    lon_axis = uconv.adjust_lon_range(cube.coord('longitude').points, radians=False)

    lat_array = uconv.broadcast_array(lat_axis.points, 2, cube.shape)
    lon_array = uconv.broadcast_array(lon_axis.points, 3, cube.shape)

    basin_array = numpy.ones(cube.shape) * 3
    basin_array = numpy.where((lon_array >= atlantic_bounds[0]) & (lon_array <= atlantic_bounds[1]), 2, basin_array)
    basin_array = numpy.where((lon_array >= indian_bounds[0]) & (lon_array <= indian_bounds[1]), 5, basin_array)

    basin_array = numpy.where((basin_array == 3) & (lon_array >= 98) & (lat_array >= 20), 2, basin_array)
    basin_array = numpy.where((basin_array == 5) & (lon_array >= 301) & (lat_array >= 0), 3, basin_array)

    return basin_array


def calc_zonal_mean(cube, basin_array, basin_name):
    """Calculate the zonal mean for a given ocean basin."""

    #FIXME
    cube.data.mask = mask

    zonal_mean_cube = calc_zonal_mean(temperature_cube, inargs)
    zonal_mean_cube.data = zonal_mean_cube.data.astype(numpy.float32)

    units = str(temperature_cube.units)
    zonal_mean_cube = add_metadata(atts, zonal_mean_cube,
                                   'zonal_mean_'+zonal_mean_cube.standard_name,
                                    zonal_mean_cube.var_name+'_zm',
                                    units)

    return zonal_mean_cube


def main(inargs):
    """Run the program."""

    climatology_cube = read_climatology(inargs.climatology_file, inargs.temperature_var, level_subset)
    temperature_cubes = iris.load(inargs.temperature_files, inargs.temperature_var, callback=save_history)
    equalise_attributes(temperature_cubes)
    atts = set_attributes(inargs, temperature_cubes[0], climatology_cube)

    out_cubes = []
    for temperature_cube in temperature_cubes:

        if climatology_cube:
            temperature_cube = temperature_cube - climatology_cube
        temperature_cube, coord_names = curvilinear_to_rectilinear(temperature_cube)

        assert coord_names == ['time', 'depth', 'latitude', 'longitude']
    
        depth_axis = temperature_cube.coord('depth')
        assert depth_axis.units in ['m', 'dbar'], "Unrecognised depth axis units"

        out_list = iris.cube.CubeList([])

        # Calculate vertical mean maps
        for layer in vertical_layers.keys():
            out_list.append(calc_vertical_mean(temperature_cube, layer, coord_names))

        # Calculate zonal mean maps
        basin_array = create_basin_file(temperature_cube)
        for basin in basins.keys():
            out_list.append(calc_zonal_mean(temperature_cube, basin_array, basin))

        out_cubes.append(out_list.concatenate())

    cube_list = []
    for var_index in (0, 1):
        temp_list = []
        for infile_index in range(0, len(inargs.temperature_files)):
            temp_list.append(out_cubes[infile_index][var_index])
        
        temp_list = iris.cube.CubeList(temp_list)     
        cube_list.append(temp_list.concatenate_cube())
    
    cube_list = iris.cube.CubeList(cube_list)
    assert cube_list[0].data.dtype == numpy.float32
    iris.save(cube_list, inargs.outfile)



    




if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate the zonal and vertical mean temperature anomaly fields'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_files", type=str, nargs='*', help="Input temperature data files")
    parser.add_argument("temperature_var", type=str, help="Input temperature variable name (the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--climatology_file", type=str, default=None, 
                        help="Input temperature climatology file (required if input data not already anomaly)")
        
    args = parser.parse_args()             
    main(args)
