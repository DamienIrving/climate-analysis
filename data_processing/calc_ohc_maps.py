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

def get_weights(coord_list, level_bounds, data_shape):
    """Get weights for vertical sum (i.e. integration)"""

    depth_index = coord_list.index('depth')
    level_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], depth_index, level_bounds)

    #guess_bounds can produce negative bound at surface
    if level_bounds[0][0] < 0.0:
        level_diffs[0] = level_diffs[0] + level_bounds[0][0]

    dim = 0
    while dim < depth_index:
        level_diffs = level_diffs[numpy.newaxis, ...]
        level_diffs = numpy.repeat(level_diffs, data_shape[dim], axis=0)
        dim = dim + 1
    
    dim = depth_index + 1
    while dim < len(data_shape):    
        level_diffs = level_diffs[..., numpy.newaxis]
        level_diffs = numpy.repeat(level_diffs, data_shape[dim], axis=-1)
        dim = dim + 1

    return level_diffs


def main(inargs):
    """Run the program."""
    
    # Read the data
    
    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(inargs.infile, inargs.var & level_subset)

    coord_names = [coord.name() for coord in cube.coords()]
    assert 'depth' in coord_names

    # Calculate anomaly
    if inargs.climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(inargs.climatology_file, inargs.var & level_subset)
        cube = cube - climatology_cube

    # Create weights
    if cube.coord('depth').bounds == None:
        cube.coord('depth').guess_bounds()

    lev_bounds = cube.coord('depth').bounds
    lev_diffs = get_weights(coord_names, lev_bounds, cube.shape)

    # Calculate heat content     
    integral = cube.collapsed('depth', iris.analysis.SUM, weights=lev_diffs)
    ohc_per_m2 = (integral * inargs.density * inargs.specific_heat) / (10**inargs.scaling)

    # Add the metadata
    standard_name = 'ocean_heat_content'
    units = '10^%d J m-2' %(inargs.scaling)
    iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}

    ohc_per_m2.standard_name = standard_name
    ohc_per_m2.long_name = 'ocean heat content'
    ohc_per_m2.var_name = 'ohc'
    ohc_per_m2.units = units
    ohc_per_m2.attributes = cube.attributes

    depth_text = 'OHC integrated over %s' %(gio.vertical_bounds_text(cube.coord('depth').points, inargs.min_depth, inargs.max_depth))
    ohc_per_m2.attributes['depth_bounds'] = depth_text

    infile_history = {inargs.infile: cube.attributes['history']}
    ohc_per_m2.attributes['history'] = gio.write_metadata(file_info=infile_history)

    # Write the output file
    iris.save(ohc_per_m2, inargs.outfile)


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
