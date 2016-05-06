"""
Filename:     calc_heat_content.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate heat content

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
from iris.experimental.regrid import regrid_weighted_curvilinear_to_rectilinear
from iris.analysis.cartography import cosine_latitude_weights

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

def add_metadata(orig_cube, new_cube, dims, inargs):
    """Add metadata to the output cube.
    
    dims = '3D' or '2D'
    
    """

    standard_name = 'ocean_heat_content_%s'  %(dims)
    units = '10^%d J m-2' %(inargs.scaling)
    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    out_cube.standard_name = standard_name
    out_cube.long_name = 'ocean heat content %s'  %(dims)
    out_cube.var_name = 'ohc_%s'  %(dims)
    out_cube.units = units
    out_cube.attributes = orig_cube.attributes

    depth_text = 'OHC integrated over %s' %(gio.vertical_bounds_text(in_cube.coord('depth').points, inargs.min_depth, inargs.max_depth))
    new_cube.attributes['depth_bounds'] = depth_text

    infile_history = {inargs.infile: orig_cube.attributes['history']}
    new_cube.attributes['history'] = gio.write_metadata(file_info=infile_history)

    return new_cube


def broadcast_weights(weights, axis_index, data_shape):
    """Broadcast the one dimesional weights array to same shape as data."""

    dim = 0
    while dim < axis_index:
        weights = weights[numpy.newaxis, ...]
        weights = numpy.repeat(weights, data_shape[dim], axis=0)
        dim = dim + 1
    
    dim = axis_index + 1
    while dim < len(data_shape):    
        weights = weights[..., numpy.newaxis]
        weights = numpy.repeat(weights, data_shape[dim], axis=-1)
        dim = dim + 1

    return weights


def calc_ohc_2D(cube, weights, inargs):
    """Calculate the 2D OHC field (time, latitude)"""

    integral = cube.collapsed(['depth', 'longitude'], iris.analysis.SUM, weights=weights)
    ohc_per_m = (integral * inargs.density * inargs.specific_heat) / (10**inargs.scaling)

    return ohc_per_m


def calc_ohc_3D(cube, weights, inargs):
    """Calculate the 3D OHC field (time, latitude, longitude)"""

    integral = cube.collapsed('depth', iris.analysis.SUM, weights=weights)
    ohc_per_m2 = (integral * inargs.density * inargs.specific_heat) / (10**inargs.scaling)

    return ohc_per_m2


def calc_vertical_weights(depth_axis, coord_list, data_shape):
    """Calculate vertical weights. 

    Defined as the distance (m) between levels.

    """

    # Calculate weights
    if not depth_axis.has_bounds():
        depth_axis.guess_bounds()
    level_bounds = depth_axis.bounds

    level_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, level_bounds)

    #guess_bounds can produce negative bound at surface
    if level_bounds[0][0] < 0.0:
        level_diffs[0] = level_diffs[0] + level_bounds[0][0]

    # Broadcast to size of data
    depth_index = coord_list.index('depth')
    level_diffs = broadcast_weights(level_diffs, depth_index, data_shape)

    return level_diffs


def calc_zonal_weights(cube, coord_list):
    """Calculate zonal weights.

    Defined as the zonal distance (m) spanned by each grid box. 

    The length of a degree of longitude is a function of 
      latitude. The formula for the length of one degree of 
      longitude is (pi/180) a cos(lat), where a is the radius of 
      the earth.

    """

    lon_axis = cube.coord('longitude')
    lon_index = coord_list.index('depth')

    coslat = cosine_latitude_weights(cube)
    radius = iris.analysis.cartography.DEFAULT_SPHERICAL_EARTH_RADIUS
    lon_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lon_axis.bounds)
    lon_diffs = broadcast_weights(lon_diffs, lon_index, cube.shape)

    lon_extents = (math.pi / 180.) * radius * coslat * lon_diffs

    return lon_extents


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
        cube_list = []
        slice_dims = coord_names
        slice_dims.remove('time')
        slice_dims.remove('depth')
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


def get_anomaly_data(inargs):
    """Read the input data and calculate anomaly if necessary."""

    # Read the data
    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(inargs.infile, inargs.var & level_subset)

    # Calculate anomaly
    if inargs.climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(inargs.climatology_file, inargs.var & level_subset)
        cube = cube - climatology_cube

    return cube


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


def main(inargs):
    """Run the program."""
    
    cube = get_anomaly_data(inargs)
    cube, coord_names = curvilinear_to_rectilinear(cube)

    assert coord_names == ['time', 'depth', 'latitude', 'longitude']

    # Calculate heat content
    vertical_weights = calc_vertical_weights(cube.coord('depth'), coord_names, cube.shape)
    zonal_weights = calc_zonal_weights(cube, coord_names)

    ohc_per_m2 = calc_ohc_3D(cube, vertical_weights, inargs)
    ohc_per_m = calc_ohc_2D(cube, vertical_weights * zonal_weights, inargs)
   
    # Write the output file
    ohc_per_m2 = add_metadata(cube, ohc_per_m2, '3D', inargs)
    ohc_per_m = add_metadata(cube, ohc_per_m, '2D', inargs)

    cube_list = iris.cube.CubeList(ohc_per_m2, ohc_per_m)
    out_cube = cube_list.concatenate()
    iris.save(out_cube, inargs.outfile)


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

    parser.add_argument("infile", type=str, help="Input temperature data file")
    parser.add_argument("var", type=str, help="Input temperature variable name (the standard_name)")
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

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
