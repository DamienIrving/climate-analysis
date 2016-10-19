"""
Filename:     fix_salinity_units.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Fix the salinity units in a given data file

"""

# Import general Python modules

import sys, os, pdb
import argparse
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


# Define functions and classes

def main(inargs):
    """Run the program."""

    cube = iris.load_cube(inargs.infile)
    cube = gio.salinity_unit_check(cube)

    cube.attributes['history'] = gio.write_metadata(file_info={inargs.infile: cube.attributes['history']})

    iris.save(cube, inargs.outfile, netcdf_format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    description="""Fix the salinity units in a given data file"""
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")
                
    args = parser.parse_args()            

    main(args)
