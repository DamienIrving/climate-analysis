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

experiments = {}
experiments['historical'] = 'black'
experiments['historicalNat'] = '0.5'
experiments['historicalAA'] = 'blue'
experiments['historicalGHG'] = 'red'
experiments['historicalAnt'] = 'purple'
               

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
    
    color = experiments[inargs.experiment]
    var = 'zonal vertical mean globe argo sea water potential temperature'

    common_lats = [('latitude', numpy.arange(-90, 91, 1))]

    cube_list = iris.cube.CubeList([])
    for index, filename in enumerate(inargs.infiles):
        cube = iris.load_cube(filename, var)
        cube = scale_data(cube)
        if index == 0:
            iplt.plot(cube, color=color, alpha=0.3, label='individual models, %s' %(inargs.experiment))
        else:
            iplt.plot(cube, color=color, alpha=0.3)
        new_cube = cube.interpolate(common_lats, iris.analysis.Linear())
        new_cube.add_aux_coord(iris.coords.DimCoord(index, 'realization'))
        fix_lats(new_cube.coord('latitude'))
        cube_list.append(new_cube)
        
    equalise_attributes(cube_list)
    merged_cube = cube_list.merge_cube()
    ensemble_mean = merged_cube.collapsed('realization', iris.analysis.MEAN)
    iplt.plot(ensemble_mean, color=color, linewidth=3.0, label='ensemble mean, %s' %(inargs.experiment))
    
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

    parser.add_argument("infiles", type=str, nargs='*', help="Input global metric files")
    parser.add_argument("experiment", type=str, choices=("historical", "historicalGHG", "historicalAA"),
                        help="Name of the experiment")
    parser.add_argument("outfile", type=str, help="Output file name")



    args = parser.parse_args()            
    main(args)
