"""
Filename:     calc_durack_ocean_maps.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the zonal and vertical mean ocean anomaly fields
              from the Durack and Wijffels (2010) data files

"""

# Import general Python modules

import sys, os, pdb
import argparse, math
import numpy
import iris
iris.FUTURE.netcdf_no_unlimited = True

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
    import calc_ocean_maps
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


def fix_cube(cube, data_type):
    """Fixes for initial loading of cube"""

    cube = iris.util.squeeze(cube)

    cube.coord('sea_water_pressure').units = 'dbar'
    cube.coord('sea_water_pressure').standard_name = 'depth'

    assert data_type in ['trend', 'climatology']
    if data_type == 'trend':
        cube.data = cube.data / 50.
        cube.units = 'K/yr'

    return cube


def main(inargs):
    """Run the program."""

    variables = ['potential_temperature', 'practical_salinity']

    # Read data
    change_cube = {}
    climatology_cube = {}
    for variable in variables:
        change_cube[variable] = iris.load_cube(inargs.infile, 'change_over_time_in_sea_water_'+variable)
        change_cube[variable] = fix_cube(change_cube[variable], 'trend')

        climatology_cube[variable] = iris.load_cube(inargs.infile, 'sea_water_'+variable)
        climatology_cube[variable] = fix_cube(climatology_cube[variable], 'climatology')

    basin_array_default = calc_ocean_maps.create_basin_array(change_cube[variable])
    coord_names = [coord.name() for coord in change_cube[variable].dim_coords]
    atts = change_cube[variable].attributes
    atts['history'] = gio.write_metadata(file_info={inargs.infile: atts['history']})
    atts['model_id'] = 'Durack and Wijffels'

    # Calculate maps
    for variable in variables:
        if variable == 'potential_temperature':
            standard_name = 'sea_water_potential_temperature'
            var_name = 'thetao'
        elif variable == 'practical_salinity':
            standard_name = 'sea_water_salinity'
            var_name = 'so'

        change_cube_list = iris.cube.CubeList([])
        climatology_cube_list = iris.cube.CubeList([])
        for layer in calc_ocean_maps.vertical_layers.keys():
            change_cube_vm = calc_ocean_maps.calc_vertical_mean(change_cube[variable].copy(), layer, coord_names, atts, standard_name, var_name)
            change_cube_list.append(change_cube_vm)

            climatology_cube_vm = calc_ocean_maps.calc_vertical_mean(climatology_cube[variable].copy(), layer, coord_names, atts, standard_name, var_name)
            climatology_cube_list.append(climatology_cube_vm)   

            if layer in ['surface', 'argo']:
                for basin in calc_ocean_maps.basins.keys():
                    basin_array = calc_ocean_maps.create_basin_array(change_cube_vm)
                    depth_cube = None
                    change_cube_list.append(calc_ocean_maps.calc_zonal_vertical_mean(change_cube_vm.copy(), depth_cube, basin_array, basin, layer, atts, standard_name, var_name))

        for basin in calc_ocean_maps.basins.keys():
            change_cube_zm = calc_ocean_maps.calc_zonal_mean(change_cube[variable].copy(), basin_array_default, basin, atts, standard_name, var_name)
            change_cube_list.append(change_cube_zm)

            climatology_cube_zm = calc_ocean_maps.calc_zonal_mean(climatology_cube[variable].copy(), basin_array_default, basin, atts, standard_name, var_name)
            climatology_cube_list.append(climatology_cube_zm)

        iris.save(change_cube_list, eval('inargs.change_outfile_'+var_name))
        iris.save(climatology_cube_list, eval('inargs.climatology_outfile_'+var_name))


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate the zonal and vertical mean ocean anomaly fields from Durack and Wijffels (2010) data files'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input data file")
    parser.add_argument("change_outfile_thetao", type=str, help="Output file name for potential temperature change data")
    parser.add_argument("climatology_outfile_thetao", type=str, help="Output file name for potential temperature climatology data")
    parser.add_argument("change_outfile_so", type=str, help="Output file name for salinity change data")
    parser.add_argument("climatology_outfile_so", type=str, help="Output file name for salinity climatology data")
        
    args = parser.parse_args()             
    main(args)
