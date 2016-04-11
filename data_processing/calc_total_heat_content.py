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


def region_mask(data_mask, latitudes, north_bound, south_bound, invert=False):
    """Create mask for excluding points not in region of interest.

    False corresponds to points that are not masked.

    Args:
      data_mask: The mask corresponding to the original data
      latitude: Latitude axis
      invert: If true, invert the latitude bounds matching so that
        points outside the region are included 
    """

    if invert:
        test_north = latitudes < north_bound
        test_south = latitudes > south_bound
    else:
        test_north = latitudes > north_bound
        test_south = latitudes < south_bound

    combo = data_mask + test_north[numpy.newaxis, numpy.newaxis, ...] + test_south[numpy.newaxis, numpy.newaxis, ...]
    mask = numpy.where(combo == 0, 0, 1)

    return mask    


def heat_content(TdV_data, mask, density, cp):
    """Calculate the heat content for each timestep."""

    TdV_data.mask = mask    # do I need to create a copy here to avoid function leakage??
    TdV_sum = TdV_data.sum(axis=(1,2,3))

    return TdV_sum * density * cp  


def main(inargs):
    """Run the program."""
    
    # Read the data
    
    level_subset = vertical_constraint(inargs.min_depth, inargs.max_depth)
    with iris.FUTURE.context(cell_datetime_objects=True):
        temperature_cube = iris.load_cube(inargs.temperature_file, inargs.temperature_var & level_subset)
        volume_cube = iris.load_cube(inargs.volume_file, inargs.volume_var)

    coord_names = [coord.name() for coord in temperature_cube.coords()]
    assert coord_names[0] == 'time', "First axis must be time"

    time_coord = temperature_cube.coord('time') 
    lat_coord = temperature_cube.coord('latitude').points

    TdV = temperature_cube.data * volume_cube.data[numpy.newaxis, ...]
    in_region = region_mask(TdV.mask, lat_coord, inargs.lat_bounds[0], inargs.lat_bounds[1])
    out_region = region_mask(TdV.mask, lat_coord, inargs.lat_bounds[0], inargs.lat_bounds[1], invert=True)

    in_ohc = heat_content(TdV, in_region, inargs.density, inargs.specific_heat)
    out_ohc = heat_content(TdV, out_region, inargs.density, inargs.specific_heat)

    pdb.set_trace()

      
    # Write the output file
    #out_cube = iris.cube.Cube(integral,
    #                      standard_name='ocean_heat_content',
    #                      long_name='ocean heat content',
    #                      var_name='ohc',
    #                      units='J m-2',
    #                      attributes=cube.attributes,
    #                      dim_coords_and_dims=[(coords[0], 0), (coords[2], 1), (coords[3], 2)],
    #                      aux_coords_and_dims=[(aux_coords[0], [1, 2]), (aux_coords[1], [1, 2])],
    #                     )
#    notes_text = 'OHC integrated over %s' %(domain_text(lev_coord.points, 
#                                                        inargs.min_depth,
#                                                        inargs.max_depth))
#    dset_out['ohc'].attrs =   {'standard_name': 'ocean_heat_content',
#                               'long_name': 'ocean_heat_content',
#                               'units': '10^%d J m-2' %(inargs.scaling),
#                               'missing_value': ohc_per_m2.fill_value,
#                               'notes': notes_text} 

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
    
    parser.add_argument("--scaling", type=int, default=12,
                        help="Factor by which to scale heat content (default value of 9 gives units of 10^9 J m-2)")
    
    args = parser.parse_args()            

    main(args)
