"""
Filename:     calc_heat_content.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate total heat content

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris

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

def domain_text(level_axis, user_top, user_bottom):
    """Text describing the vertical bounds over which the integration was performed."""
    
    if user_top and user_bottom:
        level_text = '%f down to %f' %(user_top, user_bottom)
    elif user_bottom:
        level_text = 'input data surface (%f) down to %f' %(level_axis[0], user_bottom)
    elif user_top:
        level_text = '%f down to input data bottom (%f)' %(user_top, level_axis[-1])
    else:
        level_text = 'full depth of input data (%f down to %f)' %(level_axis[0], level_axis[-1])
    
    return level_text
        

def vertical_constraint(min_depth, max_depth):
    """Define vertical constraint for cube data loading."""
    
    if min_depth and max_depth:
        level_subset = lambda cell: min_depth <= cell <= max_depth
        level_constraint = iris.Constraint(depth=level_subset)
    elif max_depth:
        level_subset = lambda cell: cell <= max_depth
        level_constraint = iris.Constraint(depth=level_subset)
    elif min_depth:
        level_subset = lambda cell: cell >= min_depth    
        level_constraint = iris.Constraint(depth=level_subset)
    else:
        level_constraint = iris.Constraint()
    
    return level_constraint


def in_flag(lat_value, south_bound, north_bound):
    """Determine if a point is in the region of interest.
   
    Returns false for points that are included (because they don't need
      to be masked)

    """

    if lat_value < north_bound and lat_value > south_bound:
        return False
    else:
        return True 
        

def region_mask(data_mask, latitudes, south_bound, north_bound, invert=False):
    """Create mask for excluding points not in region of interest.

    False corresponds to points that are not masked.

    Args:
      data_mask: The mask corresponding to the original data
      latitudes: Latitude axis
      south_bound: Southern boundary of region of interest
      north_bound: Northern boundary of region of interest 
      invert: If true, invert the latitude bounds matching so that
        points outside the region are included 

    """

    vin_flag = numpy.vectorize(in_flag)
    in_region = vin_flag(latitudes, south_bound, north_bound)
    if invert:
        in_region = numpy.logical_not(in_region)

    if len(latitudes.shape) == 1:
        in_region = in_region[numpy.newaxis, numpy.newaxis, numpy.newaxis, ...]
    elif len(latitudes.shape) == 2:
        in_region = in_region[numpy.newaxis, numpy.newaxis, ...]
    else:
        raise ValueError('Latitude dimension must be 1D or 2D')

    mask = data_mask + in_region

    return mask    


def heat_content(TdV_data, mask, density, cp, scale_factor):
    """Calculate the heat content for each timestep."""

    TdV_data.mask = mask
    TdV_sum = TdV_data.sum(axis=(1,2,3))

    result = (TdV_sum * density * cp) / eval('1e+%i' %(scale_factor))

    return result


def main(inargs):
    """Run the program."""
    
    # Read the data
    
    level_subset = vertical_constraint(inargs.min_depth, inargs.max_depth)
    with iris.FUTURE.context(cell_datetime_objects=True):
        temperature_cube = iris.load_cube(inargs.temperature_file, inargs.temperature_var & level_subset)
        volume_cube = iris.load_cube(inargs.volume_file, inargs.volume_var & level_subset)

    coord_names = [coord.name() for coord in temperature_cube.coords()]
    assert coord_names[0] == 'time', "First axis must be time"
    assert len(temperature_cube.data.shape) == 4, "Script expects 4D input data"

    time_coord = temperature_cube.coord('time') 
    lev_coord = temperature_cube.coord('depth')
    lat_coord = temperature_cube.coord('latitude')

    # Calculate the heat content

    TdV = temperature_cube.data * volume_cube.data[numpy.newaxis, ...]

    south_lat, north_lat = inargs.lat_bounds
    in_region = region_mask(TdV.mask, lat_coord.points, south_lat, north_lat)
    out_region = region_mask(TdV.mask, lat_coord.points, south_lat, north_lat, invert=True)

    ohc_in = heat_content(TdV.copy(), in_region, inargs.density, inargs.specific_heat, inargs.scaling)
    ohc_out = heat_content(TdV.copy(), out_region, inargs.density, inargs.specific_heat, inargs.scaling) 

    # Get all the metadata

    units = '10^%d J m-2' %(inargs.scaling)

    depth_text = 'OHC integrated over %s' %(domain_text(lev_coord.points, inargs.min_depth, inargs.max_depth))
    temperature_cube.attributes['depth_bounds'] = depth_text

    region_text = 'Region of interest: south lat = %f to north lat = %f' %(south_lat, north_lat) 
    temperature_cube.attributes['region_of_interest'] = region_text

    infile_history = {inargs.temperature_file: temperature_cube.attributes['history'],
                      inargs.volume_file: volume_cube.attributes['history']}
    temperature_cube.attributes['history'] = gio.write_metadata(file_info=infile_history)

    # Write the output file

    iris.std_names.STD_NAMES['ocean_heat_content_in'] = {'canonical_units': units}
    ohc_in_cube = iris.cube.Cube(ohc_in,
                                 standard_name='ocean_heat_content_in',
                                 long_name='ocean heat content within region of interest',
                                 var_name='ohc_in',
                                 units=units,
                                 attributes=temperature_cube.attributes,
                                 dim_coords_and_dims=[(time_coord, 0)],
                                 )

    iris.std_names.STD_NAMES['ocean_heat_content_out'] = {'canonical_units': units}
    ohc_out_cube = iris.cube.Cube(ohc_out,
                                  standard_name='ocean_heat_content_out',
                                  long_name='ocean heat content outside region of interest',
                                  var_name='ohc_out',
                                  units=units,
                                  attributes=temperature_cube.attributes,
                                  dim_coords_and_dims=[(time_coord, 0)],
                                  )

    cube_list = iris.cube.CubeList([ohc_in_cube, ohc_out_cube])
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

    description='Calculate the total ocean heat content for a region of interest'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_file", type=str, help="Input temperature data file")
    parser.add_argument("temperature_var", type=str, help="Input temperature variable name (i.e. the standard_name)")
    parser.add_argument("volume_file", type=str, help="Input volume data file")
    parser.add_argument("volume_var", type=str, help="Input volume variable name (i.e. the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--min_depth", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")

    parser.add_argument("--lat_bounds", type=float, nargs=2, metavar=('SOUTH_LAT', 'NORTH_LAT'), default=(-90, 0),
                        help="Latitude bounds of region of interest")
    
    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")
    
    parser.add_argument("--scaling", type=int, default=22,
                        help="Factor by which to scale heat content (default value of 22 gives units of 10^22 J m-2)")
    
    args = parser.parse_args()            

    main(args)
