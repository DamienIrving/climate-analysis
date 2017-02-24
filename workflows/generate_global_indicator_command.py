"""
Filename:     generate_global_indicator_command.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Create the command line entry to run plot_global_indicator.py

"""

# Import general Python modules

import sys, os, pdb
import argparse
import glob

# Define functions

def get_outfile(infile):
    """Generate outfile name from r1 infile name """

    outfile = infile.replace('r1', 'ensmean-')
    assert infile != outfile

    return outfile


def get_mkdir_command(filename):
    """Get directory from path+filename."""

    newdir = filename.split('/')
    newdir.pop(-1)
    newdir = "/".join(newdir)
    mkdir_command = 'mkdir -p ' + newdir

    return mkdir_command


def get_runs_file_list(model, experiment, physics, metric):
    """Get a list of files."""

    variable = metric.split('-')[0]
    file_pattern = '/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/r*i1%s/%s_*.nc'  %(model, experiment, variable, physics, metric)
    file_list = glob.glob(file_pattern)
    file_list.sort()

    return file_list


def get_ensemble_file(model, experiment, physics, metric):
    """Get the ensemble file name."""

    variable = metric.split('-')[0]
    file_pattern = '/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/ensmean-i1%s/%s_*.nc'  %(model, experiment, variable, physics, metric)
    file_list = glob.glob(file_pattern)
    
    assert len(file_list) == 1
    
    return file_list[0]
    

def calc_ensmean(infiles, execute):
    """Calculate the ensemble mean."""

    outfile = get_outfile(infiles[0])
    infiles.insert(0, 'cdo ensmean')
    infiles.append(outfile)

    command = " ".join(infiles)
    mkdir_command = get_mkdir_command(outfile)
    if execute:
        os.system(mkdir_command)
        os.system(command)
    print(mkdir_command)
    print(command)

    return outfile


def main(inargs):
    """Run the program."""

    command_list = ['python', '/home/599/dbi599/climate-analysis/visualisation/plot_global_indicators.py']
    experiments = [('historical', 'p1'), ('historicalGHG', 'p1'), ('historicalNat', 'p1')]
    if inargs.aa_physics:
        experiments.append(('historicalMisc', 'p' + inargs.aa_physics))
    if inargs.ant_physics:
        experiments.append(('historicalMisc', 'p' + inargs.ant_physics))

    for experiment, physics in experiments:
        if inargs.ensmean:
            tas_infiles = get_runs_file_list(inargs.model, experiment, physics, 'tas-global-mean')
            pe_infiles = get_runs_file_list(inargs.model, experiment, physics, 'pe-global-griddev')
            sos_infiles = get_runs_file_list(inargs.model, experiment, physics, 'sos-global-bulkdev')
            
            assert tas_infiles 
            assert len(tas_infiles) == len(pe_infiles) == len(sos_infiles)

            tas_outfile = calc_ensmean(tas_infiles, inargs.execute)
            pe_outfile = calc_ensmean(pe_infiles, inargs.execute)
            sos_outfile = calc_ensmean(sos_infiles, inargs.execute)
        else:
            tas_outfile = get_ensemble_file(inargs.model, experiment, physics, 'tas-global-mean')
            pe_outfile = get_ensemble_file(inargs.model, experiment, physics, 'pe-global-griddev')
            sos_outfile = get_ensemble_file(inargs.model, experiment, physics, 'sos-global-bulkdev')

        command_list.append(tas_outfile)
        command_list.append(pe_outfile)
        command_list.append(sos_outfile)

    outfile = '/g/data/r87/dbi599/figures/global_indicators/global-indcators_yr_%s_historicalAll_ensmean-i1_all.png'  %(inargs.model)
    command_list.append(outfile)
    command_list.append('--pe_type mean-griddev')
    if inargs.aa_physics:
        command_list.append('--aa_physics ' + inargs.aa_physics)
    if inargs.ant_physics:
        command_list.append('--ant_physics ' + inargs.ant_physics)
    command = " ".join(command_list)
    mkdir_command = get_mkdir_command(outfile)
    if inargs.execute:
        os.system(command)
    print(command) 


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Create the command line entry to run plot_global_indicators.py'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("model", type=str, help="Model name")

    parser.add_argument("--aa_physics", type=str, default=None,
                        help="Physics version for the anthropogenic aerosol only experiment (e.g. 4) [default=None]")
    parser.add_argument("--ant_physics", type=str, default=None,
                        help="Physics version for the anthropogenic only experiment (e.g. 4) [default=None]")

    parser.add_argument("--ensmean", action="store_true", default=False,
                        help="Calculate the ensemble mean first")

    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch for executing command rather than printing to screen")

    args = parser.parse_args()            
    main(args)
