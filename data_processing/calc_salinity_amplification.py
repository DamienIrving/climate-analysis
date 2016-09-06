"""
Filename:     calc_ohc_metrics.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate integrated temperature metric for various global regions

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.analysis.cartography
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

history = []

def read_area(area_file):
    """Read the optional area file."""

    if area_file:
        area_cube = iris.load_cube(area_file)
    else:
        area_cube = None

    return area_cube


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def set_attributes(inargs, data_cube, area_cube):
    """Set the attributes for the output cube."""
    
    atts = data_cube.attributes

    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0]
 
    if area_cube:                  
        infile_history[inargs.area_file] = area_cube.attributes['history']
    
    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def calc_mean_anomaly(cube, sign, grid_areas):
    """Calculate the mean of all the positive or negative anomalies."""

    if sign == 'positive':
        new_mask = numpy.where((cube.data.mask == False) & (cube.data > 0.0), False, True)
    elif sign == 'negative':
        new_mask = numpy.where((cube.data.mask == False) & (cube.data < 0.0), False, True)

    cube.data.mask = new_mask
    cube = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
    cube.remove_coord('longitude')
    cube.remove_coord('latitude')
    
    return cube


def calc_amplification_metric(cube, grid_areas, atts):
    """Calculate salinity amplification metric.

    Definition: difference between the average positive
      and average negative spatial anomaly.

    Reference: Figure 3.21 of the IPCC AR5 report

    """

    fldmean = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
    cube_spatial_anom = cube - fldmean        

    ave_pos_anom = calc_mean_anomaly(cube_spatial_anom.copy(), 'positive', grid_areas)
    ave_neg_anom = calc_mean_anomaly(cube_spatial_anom.copy(), 'negative', grid_areas)

    metric = ave_pos_anom - ave_neg_anom 

    iris.std_names.STD_NAMES['sa'] = {'canonical_units': 'g/kg'}
    metric.var_name = 'sa'
    metric.standard_name = 'sea_surface_salinity'
    metric.long_name = 'Sea Surface Salinity'
    metric.units = 'g/kg'
    metric.attributes = atts

    return metric


def get_area_weights(cube, area_cube):
    """Get area weights for averaging"""

    if area_cube:
        area_weights = uconv.broadcast_array(area_cube.data, [1, 2], cube.shape)
    else:
        if not cube.coord('latitude').has_bounds():
            cube.coord('latitude').guess_bounds()
        if not cube.coord('longitude').has_bounds():
            cube.coord('longitude').guess_bounds()
        area_weights = iris.analysis.cartography.area_weights(cube)

    return area_weights


def main(inargs):
    """Run the program."""

    in_cubes = iris.load(inargs.infiles, inargs.var, callback=save_history)
    equalise_attributes(in_cubes)
    cube = in_cubes.concatenate_cube()

    area_cube = read_area(inargs.area_file) 

    atts = set_attributes(inargs, in_cubes[0], area_cube)

    cube = cube.rolling_window('time', iris.analysis.MEAN, 12)

    area_weights = get_area_weights(cube, area_cube)
    metric = calc_amplification_metric(cube, area_weights, atts)

    iris.save(metric, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate a salinity amplification metric'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input salinity data files")
    parser.add_argument("var", type=str, help="Input salinity variable name (i.e. the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--area_file", type=str, default=None, 
                        help="Input cell area file")

    args = parser.parse_args()            

    main(args)