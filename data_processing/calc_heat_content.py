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

def simple_integration(vert_vector, level_steps):
    """Perform vertical integration for a single lat/lon/time point."""
    
    areas = vert_vector * level_steps
    
    return areas.sum()


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
        

def vertical_constraint(top_level, bottom_level):
    """Define vertical constraint for cube data loading."""
    
    if top_level and bottom_level:
        level_subset = lambda cell: bottom_level <= cell <= top_level
        level_constraint = iris.Constraint(depth=level_subset)
    elif bottom_level:
        level_subset = lambda cell: cell >= bottom_level
        level_constraint = iris.Constraint(depth=level_subset)
    elif top_level:
        level_subset = lambda cell: cell <= top_level    
        level_constraint = iris.Constraint(depth=level_subset)
    else:
        level_constraint = iris.Constraint()
    
    return level_constraint


def main(inargs):
    """Run the program."""
    
    # Read the data
    
    level_subset = vertical_constraint(inargs.top_level, inargs.bottom_level)
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(inargs.infile, inargs.long_var & level_subset)

    coord_names = [coord.name() for coord in cube.coords]
    assert coord_names == ['time', 'depth', 'latitude', 'longitude']

    time_coord = cube.coord('time')
    lat_coord = cube.coord('latitude')
    lon_coord = cube.coord('longitude')
    lev_coord = cube.coord('depth')

    lev_bounds = cube.coord('depth').bounds
    #if no bounds: cube.coord('latitude').guess_bounds()
    lev_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lev_bounds)
      
    # Integrate vertically      
    integral = numpy.ma.apply_along_axis(simple_integration, 1, cube.data, lev_diffs)
    ohc_per_m2 = (integral * inargs.density * inargs.specific_heat) / (10^inargs.scaling)
      
    # Write the output file
    d = {}
    d['time'] = ('time', time_coord.points)
    d['latitude'] = ('latitude', lat_coord.points)
    d['longitude'] = ('longitude', lon_coord.points)
    d['ohc'] = (['time', 'latitude', 'longitude'], ohc_per_m2.data)

    dset_out = xray.Dataset(d)
    notes_text = 'OHC integrated over %s' %(domain_text(lev_coord.points, 
                                                        inargs.top_level,
                                                        inargs.bottom_level))
    dset_out['ohc'].attrs =   {'standard_name': 'ocean_heat_content',
                               'long_name': 'ocean_heat_content',
                               'units': '10^%d J m-2' %(inargs.scaling),
                               'notes': notes_text} 
    gio.set_dim_atts(dset_out, str(time_coord.units))

    outfile_metadata = {inargs.infile: cube.attributes['history']}

    gio.set_global_atts(dset_out, cube.attributes, outfile_metadata)
    dset_out.to_netcdf(inargs.outfile,) #format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    The default density and specific heat of seawater are from:
    Hobbs et al (2016). Journal of Climate, 29(5), 1639–1653. doi:10.1175/JCLI-D-15-0477.1

"""

    description='Calculate ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("long_var", type=str, help="Input file variable (the standard or long name)")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--top_level", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--bottom_level", type=float, default=None,
                        help="Only include data above this vertical level")
    
    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")
    
    parser.add_argument("--scaling", type=int, default=9,
                        help="Factor by which to scale heat content (default value of 9 gives units of 10^9 J m-2)")
    
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
