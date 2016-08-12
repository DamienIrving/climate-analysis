"""
Filename:     spatial_weights.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Functions for calculating spatial weights

"""

# Import general Python modules

import sys, os, pdb
import argparse, math
import numpy
import iris
from iris.analysis.cartography import cosine_latitude_weights
import gsw

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
script_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(script_dir)
try:
    import general_io as gio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def calc_vertical_weights_1D(depth_coord, coord_names, data_shape):
    """Calculate vertical weights for a 1D depth axis with units = m.

    Args:
      depth_coord (iris.coords.DimCoord): One-dimensional depth coordinate
      coord_names (list): Names of each data coordinate
      data_shape (tuple): Shape of data

    Returns:
      iris.cube: Array of weights with shape matching data_shape
  
    """

    assert depth_coord.units == 'm'

    # Calculate weights
    if not depth_coord.has_bounds():
        depth_coord.guess_bounds()
    level_bounds = depth_coord.bounds
    level_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, level_bounds)

    #guess_bounds can produce negative bound at surface
    if level_bounds[0][0] < 0.0:
        level_diffs[0] = level_diffs[0] + level_bounds[0][0]

    # Broadcast to size of data
    depth_index = coord_names.index('depth')
    level_diffs = uconv.broadcast_array(level_diffs, depth_index, data_shape)

    return level_diffs


def calc_vertical_weights_2D(pressure_coord, latitude_coord, coord_names, data_shape):
    """Calculate vertical weights for a 2D depth axis (i.e. pressure, latitude)

    Args:
      pressure_coord (iris.coords.DimCoord): One-dimensional pressure coordinate
      latitude_coord (iris.coords.DimCoord): One-dimensional latitude coordinate
      coord_names (list): Names of each data coordinate
      data_shape (tuple): Shape of data

    Returns:
      iris.cube: Array of weights with shape matching data_shape

    """
    
    if coord_names == ['time', 'depth', 'latitude', 'longitude']:
        ntime, nlev, nlat, nlon = data_shape
    elif coord_names == ['depth', 'latitude', 'longitude']:
        nlev, nlat, nlon = data_shape
        ntime = None

    depth_diffs = numpy.zeros([nlev, nlat])
    for lat_index in range(0, nlat):
        height_vals = gsw.z_from_p(pressure_coord.points, latitude_coord.points[lat_index])
        depth_vals = gsw.depth_from_z(height_vals)
        depth_bounds = guess_depth_bounds(depth_vals)
        depth_diffs[:, lat_index] = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, depth_bounds)

    # Braodcast
    if ntime:
        depth_diffs = depth_diffs[numpy.newaxis, ...]
        depth_diffs = numpy.repeat(depth_diffs, ntime, axis=0)

    depth_diffs = depth_diffs[..., numpy.newaxis]
    depth_diffs = numpy.repeat(depth_diffs, nlon, axis=-1)

    return depth_diffs


def calc_meridional_weights(lat_coord, coord_names, data_shape):
    """Calculate meridional weights.

    Defined as the zonal distance (m) spanned by each grid box. 

    The length of a degree of latitude is (pi/180)*a, 
      where a is the radius of the earth.

    Args:
      lat_coord (iris.coords.DimCoord): One-dimensional latitude coordinate
      coord_names (list): Names of each data coordinate
      data_shape (tuple): Shape of data

    Returns:
      iris.cube: Array of weights with shape matching data_shape

    """

    lat_index = coord_names.index('latitude')

    if not lat_coord.has_bounds():
        lat_coord.guess_bounds()

    lat_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lat_coord.bounds)
    lat_diffs = uconv.broadcast_array(lat_diffs, lat_index, data_shape)
    lat_extents = (math.pi / 180.) * iris.analysis.cartography.DEFAULT_SPHERICAL_EARTH_RADIUS * lat_diffs

    return lat_extents


def calc_zonal_weights(cube, coord_names):
    """Calculate zonal weights.

    Defined as the zonal distance (m) spanned by each grid box. 

    The length of a degree of longitude is a function of 
      latitude. The formula for the length of one degree of 
      longitude is (pi/180) a cos(lat), where a is the radius of 
      the earth.

    Args:
      cube (iris.cube.Cube): Data cube
      coord_names (list): Names of each data coordinate

    Returns:
      iris.cube: Array of weights with shape matching data_shape

    """

    lon_coord = cube.coord('longitude')
    lon_index = coord_names.index('longitude')

    if not lon_coord.has_bounds():
        lon_coord.guess_bounds()

    coslat = cosine_latitude_weights(cube)
    radius = iris.analysis.cartography.DEFAULT_SPHERICAL_EARTH_RADIUS

    lon_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lon_coord.bounds)
    lon_diffs = uconv.broadcast_array(lon_diffs, lon_index, cube.shape)
    lon_extents = (math.pi / 180.) * radius * coslat * lon_diffs

    return lon_extents


def guess_depth_bounds(points, bound_position=0.5):
    """The guess_bounds method copied from iris.
    
    This implementation is specifically for the depth axis 

    """

    diffs = numpy.diff(points)
    diffs = numpy.insert(diffs, 0, diffs[0])
    diffs = numpy.append(diffs, diffs[-1])

    min_bounds = points - diffs[:-1] * bound_position
    max_bounds = points + diffs[1:] * (1 - bound_position)

    bounds = numpy.array([min_bounds, max_bounds]).transpose()
    if bounds[0, 0] < 0.0:
        bounds[0, 0] = 0

    return bounds


