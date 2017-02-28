"""
Filename:     generate_delsole_command.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create the command line entry to run plot_delsole.py

"""

# Import general Python modules

import sys, os, pdb
import argparse
import glob


# Define functions

var_names = {'tas': 'air_temperature',
             'sos': 'sea_surface_salinity',
             'pe': 'precipitation_minus_evaporation_flux',
             'pr': 'precipitation_flux',
             'evspsbl': 'water_evaporation_flux',
             'so': 'sea_water_salinity'}


def variable_details(var):
    """Get the details for any given variable."""

    var_id, region, metric = var.split('-')
    name = var_names[var_id]

    return var_id, region, metric, name


def main(inargs):
    """Run the program."""

    xvar_id, xregion, xmetric, xname = variable_details(inargs.xvar)
    yvar_id, xregion, ymetric, yname = variable_details(inargs.yvar)
    
    command_list = ['python', '/home/599/dbi599/climate-analysis/visualisation/plot_delsole.py', xname, yname, xmetric, ymetric]
    experiment_list = []
    for experiment, physics in inargs.experiment:
        xfiles = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/%si1%s/%s-%s-%s_*.nc'  %(inargs.model, experiment, xvar_id, inargs.run, physics, xvar_id, xregion, xmetric))
        yfiles = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/%si1%s/%s-%s-%s_*.nc'  %(inargs.model, experiment, yvar_id, inargs.run, physics, yvar_id, yregion, ymetric))    
        assert len(xfiles) == len(yfiles)
        for i in range(len(xfiles)):
            command_list.append('--file_pair')
            command_list.append(xfiles[i])
            command_list.append(yfiles[i])

    if inargs.run == 'r*':
        run_label = 'rall'
    else:
        run_label = inargs.run
    outfile = '/g/data/r87/dbi599/figures/delsole/delsole-%s-%s-%s-%s-%s-%s_yr_%s_%s_%s.png'  %(xvar_id, xregion, xmetric, yvar_id, yregion, ymetric, inargs.model, inargs.experiment_shorthand, run_label)
    command_list.insert(2, outfile)
    command = " ".join(command_list)

    if inargs.execute:
        os.system(command)
    print(command) 


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Create the command line entry to run plot_delsole.py'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="Model name")
    parser.add_argument("xvar", type=str, choices=('tas-global-mean', 'pe-global-griddev', 'pe-ocean-griddev'), help="x-axis variable")
    parser.add_argument("yvar", type=str, choices=('pe-global-griddev', 'pe-ocean-griddev', 'pe-land-griddev', 'sos-global-griddev', 'sos-global-bulkdev', 'pr-global-mean', 'evspsbl-global-mean', 'so-global-griddev'), help="y-axis variable")
    parser.add_argument("experiment_shorthand", type=str, help="for outfile name")

    parser.add_argument("--experiment", type=str, action='append', default=[], metavar=('EXPERIMENT', 'PHYSICS'), nargs=2,
                        help="e.g. historicalMisc p4")
    parser.add_argument("--run", type=str, default='r*',
                        help="e.g. Limit to a particular single run (e.g. r1) [default: uses all runs]")
    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch for executing command rather than printing to screen")

    args = parser.parse_args()            
    main(args)
