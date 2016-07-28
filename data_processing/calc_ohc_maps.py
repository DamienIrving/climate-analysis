"""
Filename:     calc_ohc_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate heat content

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

def add_metadata(orig_atts, new_cube, dims, inargs):
    """Add metadata to the output cube.
    
    dims = '3D' or '2D'
    
    """

    standard_name = 'ocean_heat_content_%s'  %(dims)
    units = '10^%d J m-2' %(inargs.scaling)
    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    new_cube.standard_name = standard_name
    new_cube.long_name = 'ocean heat content %s'  %(dims)
    new_cube.var_name = 'ohc_%s'  %(dims)
    new_cube.units = units
    new_cube.attributes = orig_atts  

    return new_cube


def calc_ohc_2D(cube, weights, inargs):
    """Calculate the 2D OHC field (time, latitude)"""

    integral = cube.collapsed(['depth', 'longitude'], iris.analysis.SUM, weights=weights)
    ohc_per_m = (integral * inargs.density * inargs.specific_heat) / (10**inargs.scaling)

    ohc_per_m.remove_coord('depth')
    ohc_per_m.remove_coord('longitude')

    return ohc_per_m


def calc_ohc_3D(cube, weights, inargs):
    """Calculate the 3D OHC field (time, latitude, longitude)"""

    integral = cube.collapsed('depth', iris.analysis.SUM, weights=weights)
    ohc_per_m2 = (integral * inargs.density * inargs.specific_heat) / (10**inargs.scaling)

    ohc_per_m2.remove_coord('depth')

    return ohc_per_m2


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


def main(inargs):
    """Run the program."""

    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    climatology_cube = read_climatology(inargs.climatology_file, inargs.temperature_var, level_subset)
    temperature_cubes = iris.load(inargs.temperature_files, inargs.temperature_var & level_subset, callback=save_history)
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

        # Calculate heat content
        if depth_axis.units == 'm':
            vertical_weights = spatial_weights.calc_vertical_weights_1D(depth_axis, coord_names, temperature_cube.shape)
        elif depth_axis.units == 'dbar':
            vertical_weights = spatial_weights.calc_vertical_weights_2D(depth_axis, temperature_cube.coord('latitude'), coord_names, temperature_cube.shape)

        zonal_weights = spatial_weights.calc_zonal_weights(temperature_cube, coord_names)

        ohc_per_m2 = calc_ohc_3D(temperature_cube, vertical_weights.astype(numpy.float32), inargs)
        ohc_per_m = calc_ohc_2D(temperature_cube, vertical_weights * zonal_weights, inargs)

        # Create the cube
        ohc_per_m2.data = ohc_per_m2.data.astype(numpy.float32)
        ohc_per_m.data = ohc_per_m.data.astype(numpy.float32)

        ohc_per_m2 = add_metadata(atts, ohc_per_m2, '3D', inargs)
        ohc_per_m = add_metadata(atts, ohc_per_m, '2D', inargs)

        ohc_list = iris.cube.CubeList([ohc_per_m2, ohc_per_m])
        out_cubes.append(ohc_list.concatenate())

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
notes:
    The default density and specific heat of seawater are from:
    Hobbs et al (2016). Journal of Climate, 29(5), 1639-1653. doi:10.1175/JCLI-D-15-0477.1

"""

    description='Calculate ocean heat content for a region of interest'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_files", type=str, nargs='*', help="Input temperature data files")
    parser.add_argument("temperature_var", type=str, help="Input temperature variable name (the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--climatology_file", type=str, default=None, 
                        help="Input temperature climatology file (required if input data not already anomaly)")
    
    parser.add_argument("--min_depth", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")

    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")
    
    parser.add_argument("--scaling", type=int, default=12,
                        help="Factor by which to scale heat content (default value of 9 gives units of 10^9 J m-2)")
    
    args = parser.parse_args()             
    main(args)
