"""
Filename:     plot_integrated_ocean_trend_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
from iris.experimental.equalise_cubes import equalise_attributes
import seaborn

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

experiment_colors = {}
experiment_colors['historical'] = 'black'
experiment_colors['historicalNat'] = '0.5'
experiment_colors['historicalAA'] = 'blue'
experiment_colors['historicalGHG'] = 'red'
experiment_colors['historicalAnt'] = 'purple'
               
experiment_cubes = {}
experiment_cubes['historical'] = iris.cube.CubeList([])
experiment_cubes['historicalNat'] = iris.cube.CubeList([])
experiment_cubes['historicalAA'] = iris.cube.CubeList([])
experiment_cubes['historicalGHG'] = iris.cube.CubeList([])
experiment_cubes['historicalAnt'] = iris.cube.CubeList([])

def fix_lats(lat_coord):
    """Edit the latitude axis so that they can be merged."""

    lat_coord.long_name = 'latitude'
    lat_coord.standard_name = 'latitude'
    lat_coord.var_name = 'lat'        
    try:
        lat_coord.coord_system = None    # iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    except iris.exceptions.CoordinateNotFoundError:
        pass


def scale_data(cube):
    """Scale a cube."""

    metadata = cube.metadata
    cube = cube * 10**3
    cube.metadata = metadata

    return cube


def main(inargs):
    """Run the program."""
    
    var = 'zonal vertical mean globe argo sea water potential temperature'

    common_lats = [('latitude', numpy.arange(-90, 91, 1))]

    index = 0
    current_experiments = []
    for filename, experiment in inargs.infile:
        assert experiment in experiment_colors.keys()
        cube = iris.load_cube(filename, var)
        cube = scale_data(cube)

        color = experiment_colors[experiment]
        if not experiment in current_experiments:
            iplt.plot(cube, color=color, alpha=0.3, label='individual models, %s' %(experiment))
            current_experiments.append(experiment)
        else:
            iplt.plot(cube, color=color, alpha=0.3)

        new_cube = cube.interpolate(common_lats, iris.analysis.Linear())
        new_cube.add_aux_coord(iris.coords.DimCoord(index, 'realization'))
        fix_lats(new_cube.coord('latitude'))
        experiment_cubes[experiment].append(new_cube)
        index = index + 1
    
    for experiment in current_experiments:
        cube_list = experiment_cubes[experiment]
        equalise_attributes(cube_list)
        merged_cube = cube_list.merge_cube()
        ensemble_mean = merged_cube.collapsed('realization', iris.analysis.MEAN)

        color = experiment_colors[experiment]
        iplt.plot(ensemble_mean, color=color, linewidth=3.0, label='ensemble mean, %s' %(experiment))
    
    plt.xlim(-70, 70)
    plt.legend(loc=8)
    plt.ylabel('1950-2000 trend ($10^{-3} \enspace K \enspace yr^{-1}$)')
    plt.xlabel('latitude')
    plt.title('Zonal mean, vertical mean sea water potential temperature')

    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={filename: cube.attributes['history']})


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

note:
   
"""

    description=''
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("--infile", type=str, action='append', default=[], nargs=2,
                        metavar=('FILENAME', 'EXPERIMENT'), help="Input file")
    
    args = parser.parse_args()            
    main(args)
