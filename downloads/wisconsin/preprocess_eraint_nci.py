# Import general Python modules

import os, sys, pdb
import argparse
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def main(inargs):
    """Run the program"""

    level_constraint = iris.Constraint(air_pressure=50000)

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube_list = iris.load(inargs.infiles, level_constraint)
        history = cube_list[0].attributes['history']
        equalise_attributes(cube_list)
        iris.util.unify_time_units(cube_list)
        for cube in cube_list:
            del cube.coord('time').attributes['MD5']

        cube = cube_list.concatenate_cube()
        cube = gio.check_time_units(cube)
        cube = iris.util.squeeze(cube)

        iris.coord_categorisation.add_day_of_year(cube, 'time')
        iris.coord_categorisation.add_year(cube, 'time')
        cube = cube.aggregated_by(['day_of_year', 'year'], iris.analysis.MEAN)
        cube.remove_coord('day_of_year')
        cube.remove_coord('year')
       
    cube.attributes['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history})
    iris.save(cube, inargs.outfile, netcdf_format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    description='Pre-process the ERA-Interim data on NCI at /g/data/ub4/'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    args = parser.parse_args()            
    main(args)
