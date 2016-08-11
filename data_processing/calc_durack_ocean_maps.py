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


def main(inargs):
    """Run the program."""

    variables = ['potential_temperature', 'practical_salinity']

    # Read data

    change_cubes = {}
    climatology_cubes = {}
    for variable in variables:
        change_cube[variable] = iris.load_cube(inargs.infile, 'change_over_time_in_sea_water_'+variable)
        change_cube[variable] = iris.util.squeeze(change_cube[variable])

        climatology_cube[variable] = iris.load_cube(inargs.infile, 'sea_water_'+variable)
        climatology_cube[variable] = iris.util.squeeze(climatology_cube[variable])

    basin_array = calc_ocean_maps.create_basin_array(change_cube[variable])
    coord_names = [coord.name() for coord in change_cube[variable].dim_coords]
    atts = change_cube[variable].attributes

    # Calculate maps

    #FIXME: Account for units of per 50 years

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
            change_cube_vm = calc_ocean_maps.calc_vertical_mean(change_cube, layer, coord_names, atts, standard_name, var_name)
            change_cube_vm.data = change_cube_vm.data / 50.
            change_cube_vm.units = ?? #FIXME
            change_cube_list.append(change_cube_vm)

            # FIXME Put the above 4 lines in a function

            climatology_cube_list.append(calc_ocean_maps.calc_vertical_mean(climatology_cube.copy(), layer, coord_names, atts, standard_name, var_name))    

        for basin in calc_ocean_maps.basins.keys():
            change_cube_list.append(calc_ocean_maps.calc_zonal_mean(change_cube.copy(), basin_array, basin, atts, standard_name, var_name))
            climatology_cube_list.append(calc_ocean_maps.calc_zonal_mean(climatology_cube.copy(), basin_array, basin, atts, standard_name, var_name))

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
