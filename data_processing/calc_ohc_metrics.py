"""
Filename:     calc_ohc_metrics.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the total heat content for various global regions

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.coord_categorisation
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

regions = {'southern_extratropics': [-90, -20],
          'tropics': [-20, 20],
          'northern_extratropics': [20, 90],
          'outside_southern_extratropics': [-20, 90],
          'globe': [-90, 90],
          'globe60': [-60, 60]
          }

def in_flag(lat_value, south_bound, north_bound):
    """Determine if a point is in the region of interest.
   
    Returns false for points that are included (because they don't need
      to be masked)

    """

    if lat_value < north_bound and lat_value > south_bound:
        return False
    else:
        return True 
        

def region_mask(cube, south_bound, north_bound):
    """Create mask for excluding points not in region of interest.

    False corresponds to points that are not masked.

    Args:
      data_mask: The mask corresponding to the original data
      latitudes: Latitude axis
      south_bound: Southern boundary of region of interest
      north_bound: Northern boundary of region of interest 

    """

    data_mask = cube.data.mask
    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    aux_coord_names = [coord.name() for coord in cube.aux_coords]
    
    lat_coord = cube.coord('latitude')
    
    vin_flag = numpy.vectorize(in_flag)
    in_region = vin_flag(lat_coord.points, south_bound, north_bound)

    if 'latitude' in dim_coord_names:
        lat_index = dim_coord_names.index('latitude')
        in_region = uconv.broadcast_array(in_region, lat_index, cube.shape)
    elif 'latitude' in aux_coord_names:
        assert 'time' in dim_coord_names[0:2], "Last two axes must be spatial coordinates"
        assert 'depth' in dim_coord_names[0:2], "Last two axes must be spatial coordinates"
        while in_region.ndim < data_mask.ndim:
            in_region = in_region[numpy.newaxis, ...]

    mask = data_mask + in_region

    return mask    


def heat_content(TdV_cube, mask, density, cp, scale_factor):
    """Calculate the heat content for each timestep."""

    TdV_cube.data.mask = mask
    coord_names = [coord.name() for coord in TdV_cube.coords()]
    coord_names.remove('time')
    TdV_sum = TdV_cube.collapsed(coord_names, iris.analysis.SUM)

    result = (TdV_sum * density * cp) / eval('1e+%i' %(scale_factor))

    return result


def read_data(inargs):
    """Read the input data.
    
    Will calculate the temperature anomaly if necessary.
    
    """

    # Read the data
    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    with iris.FUTURE.context(cell_datetime_objects=True):
        temperature_cube = iris.load_cube(inargs.temperature_file, inargs.temperature_var & level_subset)
        volume_cube = iris.load_cube(inargs.volume_file, inargs.volume_var & level_subset)

    # Calculate anomaly
    if inargs.climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(inargs.climatology_file, inargs.var & level_subset)
        temperature_cube = temperature_cube - climatology_cube

    return temperature_cube, volume_cube


def calc_metrics(temperature_cube, volume_cube):
    """Calculate the ocean heat content metrics"""

    TdV = temperature_cube * volume_cube
               
    ohc_dict = {}
    for region, bounds in regions.iteritems():
        mask = region_mask(TdV, bounds[0], bounds[-1])
        ohc_dict[region] = heat_content(TdV.copy(), mask, inargs.density, inargs.specific_heat, inargs.scaling)

    return ohc_dict


def get_attributes(inargs, temperature_cube, volume_cube):
    """Get the attributes for the output cubes."""
    
    lev_coord = temperature_cube.coord('depth')
    bounds_info = gio.vertical_bounds_text(lev_coord.points, inargs.min_depth, inargs.max_depth)
    depth_text = 'OHC integrated over %s' %(bounds_info)
    temperature_cube.attributes['depth_bounds'] = depth_text

    infile_history = {inargs.temperature_file: temperature_cube.attributes['history'],
                      inargs.volume_file: volume_cube.attributes['history']}
    temperature_cube.attributes['history'] = gio.write_metadata(file_info=infile_history)

    return temperature_cube.attributes


def main(inargs):
    """Run the program."""
    
    temperature_cube, volume_cube = read_data(inargs)
    ohc_dict = calc_metrics(temperature_cube, volume_cube)
    
    # Get all the metadata
    units = '10^%d J m-2' %(inargs.scaling)
    atts = get_attributes(inargs, temperature_cube)
    
    # Write the output file
    out_cubes = []
    for region in regions.keys():
        standard_name = 'ocean_heat_content_'+region
        long_name = 'ocean heat content over %s'  %(region.replace('_', ' '))
        var_name = 'ohc_'+region
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}
        ohc_cube = iris.cube.Cube(ohc_dict[region].data,
                                  standard_name=standard_name,
                                  long_name=long_name,
                                  var_name=var_name,
                                  units=units,
                                  attributes=atts,
                                  dim_coords_and_dims=[(cube.coord('time'), 0)],
                                  )
        out_cubes.append(ohc_cube)        

    cube_list = iris.cube.CubeList(out_cubes)
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
    
    parser.add_argument("--scaling", type=int, default=22,
                        help="Factor by which to scale heat content (default value of 22 gives units of 10^22 J m-2)")
    
    args = parser.parse_args()            

    main(args)
