"""
Filename:     calc_pe.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate precipitation minus evaporation

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

def main(inargs):
    """Run the program."""
  
    precip_cube = iris.load_cube(inargs.precip_file, inargs.precip_var)
    evap_cube = iris.load_cube(inargs.evap_file, inargs.evap_var)
    pe_cube = precip_cube - evap_cube

    pe_cube.metadata = precip_cube.metadata
    iris.std_names.STD_NAMES['precipitation_minus_evaporation_flux'] = {'canonical_units': pe_cube.units}
    pe_cube.standard_name = 'precipitation_minus_evaporation_flux'
    pe_cube.long_name = 'precipitation minus evaporation flux'
    pe_cube.var_name = 'pe'
    metadata_dict = {inargs.precip_file: precip_cube.attributes['history'], 
                     inargs.evap_file: evap_cube.attributes['history']}
    pe_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

    assert pe_cube.data.dtype == numpy.float32
    iris.save(pe_cube, inargs.pe_file, netcdf_format='NETCDF3_CLASSIC')
        

if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the precipitation minus evaporation'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("precip_file", type=str, help="Precipitation file")
    parser.add_argument("precip_var", type=str, help="Precipitation standard_name")
    parser.add_argument("evap_file", type=str, help="Evaporation file")
    parser.add_argument("evap_var", type=str, help="Evaporation standard_name")
    parser.add_argument("pe_file", type=str, help="Output p-e file")

    args = parser.parse_args()            

    main(args)
