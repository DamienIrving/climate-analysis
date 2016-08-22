"""
Filename:     fix_salinity.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Fix salinity units in model runs where data files are of mixed units

"""

# Import general Python modules

import sys, os, pdb
import argparse, numpy
import iris
import cf_units

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

def salinity_unit_check(cube):
    """Check CMIP5 salinity units.

    Most modeling groups store their salinity data
    in units of g/kg (typically ranging from 5 to 45 g/kg)
    and label that unit "psu" (which iris doesn't 
    recognise and converts to unknown).

    Some random data files in some runs have some stored 
    with units of kg/kg and the unit is labelled 1.

    This function converts to g/kg and unknown.

    Args:
      cube (iris.cube.Cube) 

    """

    if cube.units == '1':
        cube.data = cube.data * 1000
        cube.units = cf_units.Unit('unknown')
    
    data_max = cube.data.max()
    data_min = cube.data.min()
    assert data_max < 55.0
    assert data_min > 2.0 

    return cube


def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile, 'sea_water_salinity')
   
    cube = salinity_unit_check(cube)

    outfile_metadata = {inargs.infile: cube.attributes['history'],}
    cube.attributes['history'] = gio.write_metadata(file_info=outfile_metadata)
    iris.save(cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description='Fix salinity units in model runs where data files are of mixed units'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input salinity data file")
    parser.add_argument("outfile", type=str, help="Output file name")    

    args = parser.parse_args()             

    main(args)
