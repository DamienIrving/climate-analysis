"""
Filename:     calc_global_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate global metric

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
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def read_area(area_file):
    """Read the optional area file."""

    if area_file:
        area_cube = iris.load_cube(area_file)
    else:
        area_cube = None

    return area_cube


def set_attributes(inargs, data_cube, area_cube, clim_cube):
    """Set the attributes for the output cube."""
    
    atts = data_cube.attributes

    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0] 
    infile_history[inargs.climatology] = clim_cube.attributes['history'] 

    if area_cube:                  
        infile_history[inargs.area_file] = area_cube.attributes['history']
    
    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def calc_mean_anomaly(data_cube, clim_cube, sign, grid_areas):
    """Calculate the mean of all the positive or negative anomalies."""

    if sign == 'positive':
        new_mask = numpy.where((data_cube.data.mask == False) & (clim_cube.data > 0.0), False, True)
    elif sign == 'negative':
        new_mask = numpy.where((data_cube.data.mask == False) & (clim_cube.data < 0.0), False, True)

    data_cube.data.mask = new_mask
    data_cube = data_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
    data_cube.remove_coord('longitude')
    data_cube.remove_coord('latitude')
    
    return data_cube


def calc_amplification_metric(data_cube, clim_cube, grid_areas, atts):
    """Calculate amplification metric.

    Definition: difference between the average positive
      and average negative spatial anomaly.

    """

    assert data_cube.standard_name in ['sea_surface_salinity', 'sea_water_salinity']

    clim_fldmean = clim_cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
    clim_spatial_anom = clim_cube - clim_fldmean  # I'll need to braodcast this       

    ave_pos_anom = calc_mean_anomaly(data_cube.copy(), clim_spatial_anom.copy(), 'positive', grid_areas)
    ave_neg_anom = calc_mean_anomaly(data_cube.copy(), clim_spatial_anom.copy(), 'negative', grid_areas)

    metric = ave_pos_anom - ave_neg_anom 

    metric.var_name = data_cube.var_name
    metric.standard_name = data_cube.standard_name
    metric.long_name = data_cube.long_name
    metric.units = data_cube.units
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


def smooth_data(cube, smooth_type):
    """Apply temporal smoothing to a data cube."""

    assert smooth_type in ['annual', 'annual_running_mean']

    if smooth_type == 'annual_running_mean':
        cube = cube.rolling_window('time', iris.analysis.MEAN, 12)
    elif smooth_type == 'annual':
        cube = timeseries.convert_to_annual(cube)   

    return cube


def main(inargs):
    """Run the program."""

    if inargs.depth:
        level_constraint = iris.Constraint(depth=inargs.depth)
    else:
        level_constraint = iris.Constraint()

    cube = iris.load(inargs.infiles, inargs.var & level_constraint, callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    area_cube = read_area(inargs.area_file) 
    clim_cube = iris.load_cube(climatology_file, inargs.var & level_constraint)

    atts = set_attributes(inargs, cube, area_cube, clim_cube)

    if inargs.smoothing:
        cube = smooth_data(cube, inargs.smoothing)
    area_weights = get_area_weights(cube, area_cube)

    metric = calc_amplification_metric(cube, area_weights, atts)
    
    iris.save(metric, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate a global metric'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input data files (can merge on time)")
    parser.add_argument("var", type=str, help="Input variable name (i.e. the standard_name)")
    parser.add_argument("climatology", type=str, help="Climatology file")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--area_file", type=str, default=None, 
                        help="Input cell area file")

    parser.add_argument("--smoothing", type=str, choices=('annual', 'annual_running_mean'), default=None, 
                        help="Apply smoothing to data")

    parser.add_argument("--depth", type=float, default=None, 
                        help="Level selection")

    args = parser.parse_args()            

    main(args)
