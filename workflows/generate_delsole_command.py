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
             'evspsbl': 'water_evaporation_flux'}


def variable_details(var):
    """Get the details for any given variable."""

    var_id, metric = var.split('-')
    name = var_names[var_id]

    return var_id, metric, name


def main(inargs):
    """Run the program."""

    xvar_id, xmetric, xname = variable_details(inargs.xvar)
    yvar_id, ymetric, yname = variable_details(inargs.yvar)
    
    command_list = ['python', '/home/599/dbi599/climate-analysis/visualisation/plot_delsole.py']
    experiment_list = []
    for experiment, physics in inargs.experiment:
        xfiles = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/r*i1%s/%s-global-%s_*.nc'  %(inargs.model, experiment, xvar_id, physics, xvar_id, xmetric))
        yfiles = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/r*i1%s/%s-global-%s_*.nc'  %(inargs.model, experiment, yvar_id, physics, yvar_id, ymetric))    
        assert len(xfiles) == len(yfiles)
        for i in range(len(xfiles)):
            command_list.append('--file_group')
            command_list.append(xfiles[i])
            command_list.append(xname)
            command_list.append(yfiles[i])
            command_list.append(yname)

    outfile = '/g/data/r87/dbi599/figures/delsole/delsole-%s-%s-%s-%s_yr_%s_%s_rall.png'  %(xvar_id, xmetric, yvar_id, ymetric, inargs.model, inargs.experiment_shorthand)
    command_list.insert(2, outfile)
    if 'pe-amp' in [inargs.xvar, inargs.yvar]:
        command_list.append('--pe_metric amp')
    elif 'pe-abs' in [inargs.xvar, inargs.yvar]:
        command_list.append('--pe_metric abs')
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
    parser.add_argument("xvar", type=str, choices=('tas-mean', 'pe-abs', 'pe-amp'), help="x-axis variable")
    parser.add_argument("yvar", type=str, choices=('pe-abs', 'pe-amp', 'sos-amp', 'pr-mean', 'evspsbl-mean'), help="y-axis variable")
    parser.add_argument("experiment_shorthand", type=str, help="for outfile name")

    parser.add_argument("--experiment", type=str, action='append', default=[], metavar=('EXPERIMENT', 'PHYSICS'), nargs=2,
                        help="e.g. historicalMisc p4")
    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch for executing command rather than printing to screen")

    args = parser.parse_args()            
    main(args)
