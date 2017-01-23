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
from collections import OrderedDict

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

experiments = OrderedDict()
experiments['historical'] = 'black'
experiments['historicalNat'] = '0.5'
experiments['historicalAA'] = 'blue'
experiments['historicalGHG'] = 'red'
experiments['historicalAnt'] = 'purple'
experiments['linear combination: AA, GHG'] = 'purple'
               
metadata_dict = {}


def get_common_time_period(cube_dict, long_name):
    """Select cubes of a common time period"""

    aa_cube = cube_dict[long_name, 'historicalAA']
    ghg_cube = cube_dict[long_name, 'historicalGHG']

    aa_time = aa_cube.coord('time').points
    ghg_time = ghg_cube.coord('time').points

    common_times = set(aa_time).intersection(ghg_time)
    start_common = min(common_times)
    end_common = max(common_times)

    start_aa = aa_time.tolist().index(start_common)
    end_aa = aa_time.tolist().index(end_common)
    start_ghg = ghg_time.tolist().index(start_common)
    end_ghg = ghg_time.tolist().index(end_common)

    aa_cube = aa_cube.copy()[start_aa : end_aa + 1]
    ghg_cube = ghg_cube.copy()[start_ghg : end_ghg + 1]

    return aa_cube, ghg_cube 


def fake_ant(cube_dict, long_name):
    """Create a fake historicalAnt timeseries by adding the AA and GHG anomalies."""

    try:
        aa_cube, ghg_cube = get_common_time_period(cube_dict, long_name)
        cube_dict[(long_name, 'linear combination: AA, GHG')] = iris.analysis.maths.add(aa_cube, ghg_cube, in_place=True)
    except KeyError:
        pass

    return cube_dict


def get_linestyle(experiment):
    """Select linestyle depending on experiment."""

    if experiment == 'linear combination: AA, GHG':
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
    cube_dict = fake_ant(cube_dict, 'Near-Surface Air Temperature')
    for experiment, color in experiments.iteritems():
        try:
            cube = cube_dict['Near-Surface Air Temperature', experiment]
            iplt.plot(cube, color=color, label=experiment, linestyle=get_linestyle(experiment))
        except KeyError:
            pass
    plt.title('Global mean temperature')
    plt.xlabel('Year')
    plt.ylabel('anomaly relative to first decade (%s)' %(str(cube.units)))
    plt.legend(fontsize='small', loc=2)


def sos_plot(ax, cube_dict, so=False):
    """Plot the salinity amplification timeseries.

    so: Sea water salinity (so) used for salinity data instead of 
      sea surface salinity (sos)  

    """
    
    plt.sca(ax)
    if so:
        var = 'Sea Water Salinity'
    else:
        var = 'Sea Surface Salinity'

    cube_dict = fake_ant(cube_dict, var)
    for experiment, color in experiments.iteritems():
        try:
            cube = cube_dict[var, experiment]
            iplt.plot(cube, color=color, label=experiment, linestyle=get_linestyle(experiment))
        except KeyError:
            pass

    plt.title('Salinity amplification')
    plt.xlabel('Year')
    plt.ylabel('anomaly relative to first decade')
    plt.legend(fontsize='small', loc=2)


def pe_plot(ax, cube_dict, data_type):
    """Plot the precipiation minus evaproation timeseries."""
    
    plt.sca(ax)
    cube_dict = fake_ant(cube_dict, 'precipitation minus evaporation flux')
    for experiment, color in experiments.iteritems():
        try:
            cube = cube_dict['precipitation minus evaporation flux', experiment] * 86400
            iplt.plot(cube, color=color, label=experiment, linestyle=get_linestyle(experiment))
        except KeyError:
            pass

    if data_type == 'amplification':
        plt.title('P-E amplification')
    elif data_type == 'mean-abs':
        plt.title('Global mean $|P-E|$')
    plt.xlabel('Year')
    plt.ylabel('anomaly relative to first decade (mm/day)')
    plt.legend(fontsize='small', loc=2)


def main(inargs):
    """Run the program."""

    cube_list = iris.load(inargs.infiles, callback=save_history)
    iris.util.unify_time_units(cube_list)

    cube_dict = {}
    for cube in cube_list:
        long_name = cube.long_name
        variables = ['Near-Surface Air Temperature', 'Sea Surface Salinity',
                     'Sea Water Salinity', 'precipitation minus evaporation flux']
        assert long_name in variables

        experiment = cube.attributes['experiment_id']
        if experiment == 'historicalMisc':
            physics = cube.attributes['physics_version']
            assert str(physics) in [inargs.aa_physics, inargs.ant_physics], '%s is not an acceptable physics version' %(physics)
            if str(physics) == inargs.aa_physics:
                experiment = 'historicalAA'
            elif str(physics) == inargs.ant_physics:
                experiment = 'historicalAnt'
        assert experiment in experiments.keys(), '%s is not an acceptable experiment name' %(experiment)
        
        key = (long_name, experiment)
        assert key not in cube_dict.keys(), '%s, %s not in cube dict' %(long_name, experiment)
        cube_dict[key] = cube

    for key, cube in cube_dict.iteritems():
        baseline = cube[0:10].data.mean()
        cube_dict[key] = cube - baseline

    fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(20, 5))
    tas_plot(axes[0], cube_dict) 
    sos_plot(axes[1], cube_dict, so=inargs.so)
    pe_plot(axes[2], cube_dict, inargs.pe_type)
        
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

    description='Plot global mean surface temperature, salinity amplifcation and global mean P-E absolute value'
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
    parser.add_argument("--pe_type", type=str, choices=("amplification", "mean-abs"), default="amplification",
                        help="specify which P-E metric is being plotted [default: False]")

    args = parser.parse_args()            
    main(args)
