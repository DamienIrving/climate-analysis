"""
Filename:     plot_global_indicators.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot global mean surface temperature, salinity amplifcation and P-E

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
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

experiments = {'historical': 'black',
               'historicalAA': 'blue',
               'historicalGHG': 'red',
               'historicalAnt': 'purple',
               'historicalNat': '0.5'}
variables = ['air_temperature', 'sea_surface_salinity',
             'precipitation_flux', 'water_evaporation_flux'] 


metadata_dict = {}

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.""" 

    metadata_dict[filename] = cube.attributes['history']


def tas_plot(ax, cube_dict):
    """Plot the global mean temperature timeseries."""
    
    plt.sca(ax)
    for experiment, color in experiments.iteritems():
        try:
            cube = cube_dict['air_temperature', experiment]
            iplt.plot(cube, color=color, label=experiment)
        except KeyError:
            pass
    plt.title('Global mean temperature')
    plt.xlabel('Year')
    plt.ylabel(str(cube.units))
    plt.legend(fontsize='small', loc=2)


def sos_plot(ax, cube_dict):
    """Plot the salinity amplification timeseries."""
    
    plt.sca(ax)
    for experiment, color in experiments.iteritems():
        try:
            iplt.plot(cube_dict['sea_surface_salinity', experiment], color=color, label=experiment)
        except KeyError:
            pass

    plt.title('Salinity amplification')
    plt.xlabel('Year')
    plt.legend(fontsize='small', loc=2)


def pe_plot(ax, cube_dict):
    """Plot the precipiation minus evaproation timeseries."""
    
    plt.sca(ax)
    for experiment, color in experiments.iteritems():
        try:
            pe_cube = cube_dict['precipitation_flux', experiment] + cube_dict['water_evaporation_flux', experiment]
            iplt.plot(pe_cube * 86400, color=color, label=experiment)
        except KeyError:
            pass
    plt.title('P-E')
    plt.xlabel('Year')
    plt.ylabel('mm/day')
    plt.legend(fontsize='small', loc=2)


def main(inargs):
    """Run the program."""

    cube_list = iris.load(inargs.infiles, callback=save_history)
    iris.util.unify_time_units(cube_list)

    cube_dict = {}
    for cube in cube_list:
        standard_name = cube.standard_name
        assert standard_name in variables

        experiment = cube.attributes['experiment_id']
        if experiment == 'historicalMisc':
            physics = cube.attributes['physics_version']
            assert str(physics) in [inargs.aa_physics, inargs.ant_physics], '%s is not an acceptable physics version' %(physics)
            if str(physics) == inargs.aa_physics:
                experiment = 'historicalAA'
            elif str(physics) == inargs.ant_physics:
                experiment = 'historicalAnt'
        assert experiment in experiments.keys(), '%s is not an acceptable experiment name' %(experiment)
        
        key = (standard_name, experiment)
        assert key not in cube_dict.keys()
        cube_dict[key] = cube

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))
    tas_plot(axes[0], cube_dict) 
    sos_plot(axes[1], cube_dict)
    pe_plot(axes[2], cube_dict)
        
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

"""

    description='Plot global mean surface temperature, salinity amplifcation and P-E'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input global metric files")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--aa_physics", type=str, default=None,
                        help="Physics version for the anthropogenic aerosol only experiment [default=None]")
    parser.add_argument("--ant_physics", type=str, default=None,
                        help="Physics version for the anthropogenic only experiment [default=None]")

    args = parser.parse_args()            
    main(args)
