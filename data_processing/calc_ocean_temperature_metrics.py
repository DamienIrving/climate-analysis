"""
Filename:     calc_ocean_temperature_metrics.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate integrated temperature metric for various global regions

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
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

history = []

regions = {'globe': [-90, 90],
           'globe60': [-60, 60],
           'tropics': [-20, 20],
           'northern_extratropics': [20, 90],
           'northern_extratropics60': [20, 60],
           'nh60': [0, 60],
           'southern_extratropics': [-90, -20],
           'southern_extratropics60': [-60, -20],
           'sh60': [-60, 0],
           'outside_southern_extratropics': [-20, 90],
           'outside_southern_extratropics60': [-20, 60]
          }


def calc_metrics(inargs, temperature_cube, volume_cube, ref_region=None):
    """Calculate the ocean heat content metrics.

    If a reference region is supplied the metrics are scaled according
      to the volume of that region. 

    """

    TdV = temperature_cube * volume_cube

    if ref_region:
        ref_bounds = regions[ref_region]
        ref_volume_mask = region_mask(volume_cube.copy(), ref_bounds[0], ref_bounds[-1])
        ref_volume = calc_volume(volume_cube.copy(), ref_volume_mask)    

    metric_dict = {}
    for region, bounds in regions.iteritems():
        data_mask = region_mask(TdV, bounds[0], bounds[-1])
        TdV_sum = integrate_temperature(TdV.copy(), data_mask)
        if inargs.metric == 'inttemp':
            metric_dict[region] = TdV_sum / eval('1e+%i' %(inargs.scaling))
        elif inargs.metric == 'ohc':
            metric_dict[region] = (TdV_sum * inargs.density * inargs.specific_heat) / eval('1e+%i' %(inargs.scaling))

        if ref_region:
            volume_mask = region_mask(volume_cube.copy(), bounds[0], bounds[-1])
            volume = calc_volume(volume_cube.copy(), volume_mask)
            volume_ratio = volume / ref_volume
            print region, volume_ratio
            metric_dict[region] = metric_dict[region] / volume_ratio

    return metric_dict


def calc_volume(volume_cube, mask):
    """Calculate the volume."""

    volume_cube.data.mask = mask
    
    return volume_cube.data.sum()


def create_metric_cubelist(metric_name, metric_dict, units, atts, time_coord):
    """Create an ohc metric cube corresponding to a single input file."""

    if metric_name == 'inttemp':
        standard_base = 'integrated_temperature'
        long_base = 'integrated temperature'
    elif metric_name == 'ohc':
        standard_base = 'ocean_heat_content'
        long_base = 'ocean heat content'

    metric_cubelist = []
    for region in regions.keys():
        standard_name = standard_base+'_'+region
        long_name = '%s %s'  %(long_base, region.replace('_', ' '))
        var_name = metric_name+'_'+region
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': units}
        ohc_cube = iris.cube.Cube(metric_dict[region].data,
                                  standard_name=standard_name,
                                  long_name=long_name,
                                  var_name=var_name,
                                  units=units,
                                  attributes=atts,
                                  dim_coords_and_dims=[(time_coord, 0)],
                                  )
        metric_cubelist.append(ohc_cube)        

    metric_cubelist = iris.cube.CubeList(metric_cubelist)
    metric_cubelist = metric_cubelist.concatenate()

    return metric_cubelist


def create_volume_cube(cube):
    """Create a volume cube."""

    dim_coord_names = [coord.name() for coord in cube.dim_coords]
    assert 'latitude' in dim_coord_names
    assert 'longitude' in dim_coord_names
    assert 'depth' in dim_coord_names

    lat_extents = spatial_weights.calc_meridional_weights(cube.coord('latitude'), dim_coord_names, cube.shape)
    lon_extents = spatial_weights.calc_zonal_weights(cube, dim_coord_names)

    depth_coord = cube.coord('depth')
    assert depth_coord.units in ['m', 'dbar'], "Unrecognised depth axis units"
    if depth_coord.units == 'm':
        vert_extents = spatial_weights.calc_vertical_weights_1D(depth_coord, dim_coord_names, cube.shape)
    elif depth_coord.units == 'dbar':
        vert_extents = spatial_weights.calc_vertical_weights_2D(depth_coord, cube.coord('latitude'), dim_coord_names, cube.shape)

    volume_cube = lat_extents * lon_extents * vert_extents
    volume_cube = volume_cube.astype(numpy.float32)

    return volume_cube


def integrate_temperature(TdV_cube, mask):
    """Calculate the heat content for each timestep."""

    TdV_cube.data.mask = mask
    coord_names = [coord.name() for coord in TdV_cube.coords()]
    coord_names.remove('time')
    TdV_sum = TdV_cube.collapsed(coord_names, iris.analysis.SUM)

    return TdV_sum
    

def in_flag(lat_value, south_bound, north_bound):
    """Determine if a point is in the region of interest.
   
    Returns false for points that are included (because they don't need
      to be masked)

    """

    if lat_value < north_bound and lat_value > south_bound:
        return False
    else:
        return True 
        

def read_optional_data(inargs, level_subset):
    """Read the optional input data (volume and climatology)."""

    with iris.FUTURE.context(cell_datetime_objects=True):
        if inargs.volume_file:
            volume_cube = iris.load_cube(inargs.volume_file, 'ocean_volume' & level_subset)
        else:
            volume_cube = None

        if inargs.climatology_file:
            climatology_cube = iris.load_cube(inargs.climatology_file, inargs.temperature_var & level_subset)
            assert climatology_cube.data.dtype == numpy.float32
        else:
            climatology_cube = None

    return volume_cube, climatology_cube


def region_mask(cube, south_bound, north_bound):
    """Create mask for excluding points not in region of interest.

    False corresponds to points that are not masked.

    Args:
      cube (iris.cube.Cube): Data cube
      south_bound (float): Southern boundary of region of interest
      north_bound (float): Northern boundary of region of interest 

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


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.
    (This is required because the history attribute differs between input files 
      and is therefore deleted upon equilising attributes)  
    """ 

    history.append(cube.attributes['history'])


def set_attributes(inargs, temperature_cube, volume_cube, climatology_cube):
    """Set the attributes for the output cube."""
    
    atts = temperature_cube.attributes

    lev_coord = temperature_cube.coord('depth')
    bounds_info = gio.vertical_bounds_text(lev_coord.points, inargs.min_depth, inargs.max_depth)
    depth_text = '%s integrated over %s' %(inargs.metric, bounds_info)
    atts['depth_bounds'] = depth_text

    infile_history = {}
    infile_history[inargs.temperature_files[0]] = history[0]
    if volume_cube:                  
        infile_history[inargs.volume_file] = volume_cube.attributes['history']
    if climatology_cube:                  
        infile_history[inargs.climatology_file] = climatology_cube.attributes['history']

    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def main(inargs):
    """Run the program."""

    level_subset = gio.iris_vertical_constraint(inargs.min_depth, inargs.max_depth)
    volume_cube, climatology_cube = read_optional_data(inargs, level_subset)
    temperature_cubelist = iris.load(inargs.temperature_files, inargs.temperature_var & level_subset, callback=save_history)
    #history.append(temperature_cubelist[0].attributes['history'])
    equalise_attributes(temperature_cubelist)

    if inargs.metric == 'ohc':
        units = '10^%d J' %(inargs.scaling)
    elif inargs.metric == 'inttemp':
        units = '10^%d K m3' %(inargs.scaling)

    atts = set_attributes(inargs, temperature_cubelist[0], volume_cube, climatology_cube)

    out_cubes = []
    for temperature_cube in temperature_cubelist:

        if climatology_cube:
            temperature_cube = temperature_cube - climatology_cube

        if not volume_cube:
            volume_cube = create_volume_cube(temperature_cube)

        metric_dict = calc_metrics(inargs, temperature_cube, volume_cube, ref_region=inargs.ref_region)   
        metric_cubelist = create_metric_cubelist(inargs.metric, metric_dict, units, atts, temperature_cube.coord('time'))
            
        out_cubes.append(metric_cubelist)

    cube_list = []
    for region_index in range(0, len(regions.keys())):
        temp_list = []
        for infile_index in range(0, len(inargs.temperature_files)):
            temp_list.append(out_cubes[infile_index][region_index])
        
        temp_list = iris.cube.CubeList(temp_list)     
        cube_list.append(temp_list.concatenate_cube())
    
    cube_list = iris.cube.CubeList(cube_list)
    assert cube_list[0].data.dtype == numpy.float32
    iris.save(cube_list, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    The default density and specific heat of seawater are from:
    Hobbs et al (2016). Journal of Climate, 29(5), 1639-1653. doi:10.1175/JCLI-D-15-0477.1

"""

    description='Calculate integrated temperature metrics for a region of interest'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("temperature_files", type=str, nargs='*', help="Input temperature data files")
    parser.add_argument("temperature_var", type=str, help="Input temperature variable name (i.e. the standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--metric", type=str, choices=('inttemp', 'ohc'), default='ohc', 
                        help="Metric to calculate - integrated temperature or ocean heat content")

    region_choices = regions.keys()
    region_choices.append(None)
    parser.add_argument("--ref_region", type=str, choices=regions.keys(), default=None, 
                        help="Scale metrics to the volume of this region")

    parser.add_argument("--volume_file", type=str, default=None, 
                        help="Input volume data file")
    parser.add_argument("--climatology_file", type=str, default=None, 
                        help="Input temperature climatology file (for calculating the anomaly)")

    parser.add_argument("--min_depth", type=float, default=None,
                        help="Only include data below this vertical level")
    parser.add_argument("--max_depth", type=float, default=None,
                        help="Only include data above this vertical level")
    
    parser.add_argument("--density", type=float, default=1023,
                        help="Density of seawater (in kg.m-3). Default of 1023 kg.m-3 from Hobbs2016.")
    parser.add_argument("--specific_heat", type=float, default=4000,
                        help="Specific heat of seawater (in J / kg.K). Default of 4000 J/kg.K from Hobbs2016")
    
    parser.add_argument("--scaling", type=int, default=22,
                        help="Factor by which to scale metrics (default value of 19 gives units of 10^22 J or K m3)")
    
    args = parser.parse_args()            

    main(args)
