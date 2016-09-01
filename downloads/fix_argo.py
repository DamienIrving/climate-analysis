"""
Filename:     fix_argo.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Take the Scripps Institution of Oceanography gridded argo temperature or salinity data
              (from http://www.argo.ucsd.edu/Gridded_fields.html) and make the file attributes
              more consistent with CMIP5
"""

# Import general Python modules

import sys, os, pdb
import argparse
import iris
import cf_units
import datetime


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

def main(inargs):
    """Run the program."""

    cubes = iris.load(inargs.infile)
    if inargs.climatology:
        cube = cubes[0]
    else:
        cube = cubes[1]

    # Edit variable attributes
    cube.attributes = {'comment': cube.long_name}
    if inargs.variable == 'temperature':
        cube.var_name = 'to'
        cube.standard_name = 'sea_water_temperature'
        cube.long_name = 'Sea Water Temperature'
        cube.units = 'K'
    elif inargs.variable == 'salinity':
        cube.var_name = 'so'
        cube.standard_name = 'sea_water_salinity'
        cube.long_name = 'Sea Water Salinity'
        cube.units = 'g/kg'

    # Edit latitude attributes
    argo_lat = cube.coord('latitude')
    argo_lat.var_name = 'lat'
    argo_lat.long_name = 'latitude'

    # Edit latitude attributes
    argo_lon = cube.coord('longitude')
    argo_lon.var_name = 'lon'
    argo_lon.long_name = 'longitude'

    # Edit time attributes
    if not inargs.climatology:
        argo_time = cube.coord('TIME')
        new_unit = cf_units.Unit('days since 2004-01-01 00:00:00', calendar='gregorian')  
        argo_time.convert_units(new_unit)

        argo_time.var_name = 'time'
        argo_time.long_name = 'time'

    # Edit depth attributes
    argo_depth = cube.coord('PRESSURE')
    argo_depth.var_name = 'lev'
    argo_depth.long_name = 'ocean depth coordinate'
    argo_depth.standard_name = 'depth'

    # Write output file
    timestamp = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
    old_history = timestamp + ': Scripps Institution of Oceanography gridded argo %s data downloaded from http://www.argo.ucsd.edu/Gridded_fields.html'  %(inargs.variable)
    cube.attributes['history'] = gio.write_metadata(file_info={inargs.infile: old_history})
    iris.save(cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
notes:
    Applies to Scripps Institution of Oceanography gridded argo 
    temperature or salinity data from http://www.argo.ucsd.edu/Gridded_fields.html
"""

    description='Make Argo data file attributes more like CMIP5'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, choices=('temperature', 'salinity'), help="Input variable") 
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--climatology", action="store_true", default=False,
                        help="switch for outputting a climatology file instead")

    args = parser.parse_args()             
    main(args)
