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
               'historicalAAGHGmean': 'purple',
               'historicalNat': '0.5'}

metadata_dict = {}


def fake_ant(cube_dict, standard_name):
    """Create a fake historicalAnt timeseries using AA and GHG average."""

    try:
        aa_cube = cube_dict[standard_name, 'historicalAA']
        ghg_cube = cube_dict[standard_name, 'historicalGHG']
        cube_dict[(standard_name, 'historicalAAGHGmean')] = iris.analysis.maths.add(aa_cube.copy(), ghg_cube, in_place=True) / 2.0
    except KeyError:
        pass

    return cube_dict


def get_linestyle(experiment):
    """Select linestyle depending on experiment."""

    if experiment == 'historicalAAGHGmean':
        linestyle = 'dotted'
    else:
        linestyle = '-'

    return linestyle


def save_history(cube, field, filename):
    """Save the history attribute when reading the data.""" 

    metadata_dict[filename] = cube.attributes['history']


def tas_plot(ax, cube_dict):
    """Plot the global mean temperature timeseries."""
    
    plt.sca(ax)
    cube_dict = fake_ant(cube_dict, 'air_temperature')
    for experiment, color in experiments.iteritems():
        try:
            cube = cube_dict['air_temperature', experiment]
            iplt.plot(cube, color=color, label=experiment, linestyle=get_linestyle(experiment))
        except KeyError:
            pass
    plt.title('Global mean temperature')
    plt.xlabel('Year')
    plt.ylabel(str(cube.units))
    plt.legend(fontsize='small', loc=2)


def sos_plot(ax, cube_dict, so=False):
    """Plot the salinity amplification timeseries.

    so: Sea water salinity (so) used for salinity data instead of 
      sea surface salinity (sos)  

    """
    
    plt.sca(ax)
    if so:
        var = 'sea_water_salinity'
    else:
        var = 'sea_surface_salinity'

    cube_dict = fake_ant(cube_dict, var)
    for experiment, color in experiments.iteritems():
        try:
            iplt.plot(cube_dict[var, experiment], color=color, label=experiment, linestyle=get_linestyle(experiment))
        except KeyError:
            pass

    plt.title('Salinity amplification')
    plt.xlabel('Year')
    plt.legend(fontsize='small', loc=2)


def pe_plot(ax, cube_dict):
    """Plot the precipiation minus evaproation timeseries."""
    
    plt.sca(ax)
    cube_dict = fake_ant(cube_dict, 'precipitation_flux')
    cube_dict = fake_ant(cube_dict, 'water_evaporation_flux')
    for experiment, color in experiments.iteritems():
        try:
            p_cube = cube_dict['precipitation_flux', experiment]
            e_cube = cube_dict['water_evaporation_flux', experiment]
            pe_cube = iris.analysis.maths.add(p_cube.copy(), e_cube, in_place=True) * 86400
            iplt.plot(pe_cube, color=color, label=experiment, linestyle=get_linestyle(experiment))
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
        variables = ['air_temperature', 'sea_surface_salinity',
                     'sea_water_salinity', 'precipitation_flux',
                     'water_evaporation_flux']
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
        assert key not in cube_dict.keys(), '%s, %s not in cube dict' %(standard_name, experiment)
        cube_dict[key] = cube

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))
    tas_plot(axes[0], cube_dict) 
    sos_plot(axes[1], cube_dict, so=inargs.so)
    pe_plot(axes[2], cube_dict)
        
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com

note:
  In a couple of places this script uses 'in_place' cube arithmetic.
  This is because if I did the default arithmetic (in_place=False) I
  would inconsistently generate a segmentation fault upon trying to plot
  the resulting cube. 
   
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

    parser.add_argument("--so", action="store_true", default=False,
                        help="so rather than sos used for salinity [default: False]")

    args = parser.parse_args()            
    main(args)
