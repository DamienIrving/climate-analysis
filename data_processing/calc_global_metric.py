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


def read_optional(optional_file):
    """Read an optional file (e.g. area, basin) file."""

    if optional_file:
        cube = iris.load_cube(optional_file)
    else:
        cube = None

    return cube


def set_attributes(inargs, data_cube, area_cube, sftlf_cube):
    """Set the attributes for the output cube."""
    
    atts = data_cube.attributes

    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0] 
 
    if area_cube:                  
        infile_history[inargs.area_file] = area_cube.attributes['history']
    if sftlf_cube:                  
        infile_history[inargs.sftlf_file[0]] = sftlf_cube.attributes['history']
    
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


def calc_bulk_deviation(cube, grid_areas, atts):
    """Calculate bulk deviation metric.

    Usually used for sea surface salinity
      (e.g. Figure 3.21 of the IPCC AR5 report)

    Definition: difference between the average positive
      and average negative spatial anomaly.

    """

    fldmean = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
    cube_spatial_anom = cube - fldmean        

    ave_pos_anom = calc_mean_anomaly(cube_spatial_anom.copy(), 'positive', grid_areas)
    ave_neg_anom = calc_mean_anomaly(cube_spatial_anom.copy(), 'negative', grid_areas)

    metric = ave_pos_anom - ave_neg_anom 
    metric.metadata = cube.metadata

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


def calc_global_mean(cube, grid_areas, atts, remove_atts=True):
    """Calculate global mean."""

    global_mean = cube.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)

    if remove_atts:
        global_mean.remove_coord('longitude')
        global_mean.remove_coord('latitude')

    global_mean.attributes = atts

    return global_mean


def calc_grid_deviation(cube, var, grid_areas, atts):
    """Calculate the global mean |x - x_spatial_mean|.
  
    Doesn't calculate the spatial mean for P-E 
    (already centered on zero)

    """

    metadata = cube.metadata

    if var != 'precipitation_minus_evaporation_flux':
        global_mean = calc_global_mean(cube, grid_areas, atts, remove_atts=False)
        cube = cube - global_mean        

    abs_val = (cube ** 2) ** 0.5
    abs_val.metadata = metadata

    global_mean_abs = abs_val.collapsed(['longitude', 'latitude'], iris.analysis.MEAN, weights=grid_areas)
    global_mean_abs.remove_coord('longitude')
    global_mean_abs.remove_coord('latitude')

    global_mean_abs.attributes = atts

    return global_mean_abs 


def smooth_data(cube, smooth_type):
    """Apply temporal smoothing to a data cube."""

    assert smooth_type in ['annual', 'annual_running_mean']

    if smooth_type == 'annual_running_mean':
        cube = cube.rolling_window('time', iris.analysis.MEAN, 12)
    elif smooth_type == 'annual':
        cube = timeseries.convert_to_annual(cube)   

    return cube


def area_info(atts, area_cube, mask, selected_region):
    """Determine the area of the ocean and land."""

    



def create_mask(land_fraction_cube, selected_region, area_cube, atts):
    """Create a mask."""

    assert selected_region in ['ocean', 'land']
    if selected_region == 'ocean':
        mask = numpy.where(land_fraction_cube.data < 50, False, True)
    elif selected_region == 'land':
        mask = numpy.where(land_fraction_cube.data > 50, False, True)
    
    if area_cube:
        atts = area_info(atts, area_cube, mask, selected_region)

    return mask, atts


def main(inargs):
    """Run the program."""

    if inargs.depth:
        level_constraint = iris.Constraint(depth=inargs.depth)
    else:
        level_constraint = iris.Constraint()
    
    if inargs.var == 'precipitation_minus_evaporation_flux':
        iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': "kg m-2 s-1"}

    cube = iris.load(inargs.infiles, inargs.var & level_constraint, callback=save_history)
    equalise_attributes(cube)
    iris.util.unify_time_units(cube)
    cube = cube.concatenate_cube()
    cube = gio.check_time_units(cube)

    area_cube = read_optional(inargs.area_file)
    if inargs.sftlf_file:
        sftlf_file, selected_region = inargs.sftlf_file
        sftlf_cube = read_optional(sftlf_file)
        mask, atts = create_mask(sftlf_cube, selected_region, area_cube, atts)
        cube.data = numpy.ma.asarray(cube.data)
        cube.data.mask = mask
        
    atts = set_attributes(inargs, cube, area_cube, sftlf_cube)
    pdb.set_trace()

    if inargs.smoothing:
        cube = smooth_data(cube, inargs.smoothing)
    area_weights = get_area_weights(cube, area_cube)

    if inargs.metric == 'bulk-deviation':
        metric = calc_bulk_deviation(cube, area_weights, atts)
    elif inargs.metric == 'mean':
        metric = calc_global_mean(cube, area_weights, atts)
    elif inargs.metric == 'grid-deviation':
        metric = calc_grid_deviation(cube, inargs.var, area_weights, atts)

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
    parser.add_argument("metric", type=str, choices=('mean', 'bulk-deviation', 'grid-deviation'), help="Metric to calculate")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--area_file", type=str, default=None, 
                        help="Input cell area file")
    parser.add_argument("--sftlf_file", type=str, nargs=2, metavar=('FILE', 'SELECTION'), default=None, 
                        help="Land surface fraction file used to generate mask (SELECTION = land or ocean)")

    parser.add_argument("--smoothing", type=str, choices=('annual', 'annual_running_mean'), default=None, 
                        help="Apply smoothing to data")

    parser.add_argument("--depth", type=float, default=None, 
                        help="Level selection")

    args = parser.parse_args()            

    main(args)
