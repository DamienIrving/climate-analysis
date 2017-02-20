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

var_names = {'tas': 'air_temperature',
             'sos': 'sea_surface_salinity',
             'pe': 'precipitation_minus_evaporation_flux',
             'pr': 'precipitation_flux',
             'evspsbl': 'water_evaporation_flux'}


def get_outfile(infile):
    """Generate outfile name from r1 infile name """

    outfile = infile.replace('r1', 'ensmean-')
    assert infile != outfile

    return outfile


def get_file_list(model, experiment, physics, metric):
    """Get a list of files."""

    variable = metric.split('-')
    file_list = glob.glob('/g/data/r87/dbi599/drstree/CMIP5/GCM/*/%s/%s/yr/*/%s/r*i1%s/%s_*.nc'  %(inargs.model, experiment, variable, physics, metric))
    file_list.sort()

    return file_list


def calc_ensmean(infiles, execute):
    """Calculate the ensemble mean."""

    outfile = get_outfile(infiles[0])
    infiles.insert(0, 'cdo ensmean')
    infiles.append(outfile)
    command = " ".join(infiles)

    if execute:
        os.system(command)
    print(command)

    return outfile


def main(inargs):
    """Run the program."""
    
    command_list = ['python', '/home/599/dbi599/climate-analysis/visualisation/plot_global_indicators.py']
    experiments = [('historical', 'p1'), ('historicalGHG', 'p1'), ('historicalNat', 'p1')]
    if inargs.aa_physics:
        experiments.append(('historicalMisc', inargs.aa_physics))
    if inargs.ant_physics:
        experiments.append(('historicalMisc', inargs.ant_physics))

    if inargs.ensmean:
        for experiment, physics in experiments:
            tas_infiles = get_file_list(inargs.model, experiment, physics, 'tas-global-mean')
            pe_infiles = get_file_list(inargs.model, experiment, physics, 'pe-global-abs')
            sos_infiles = get_file_list(inargs.model, experiment, physics, 'sos-global-amp')
            
            assert tas_files 
            assert len(tas_files) == len(pe_files) == len(sos_files)

            tas_outfile = calc_ensmean(tas_infiles, inargs.execute)
            pe_outfile = calc_ensmean(pe_infiles, inargs.execute)
            sos_outfile = calc_ensmean(sos_infiles, inargs.execute)
            
            command_list.append(tas_outfile)
            command_list.append(pe_outfile)
            command_list.append(sos_outfile)

    else:

 










    outfile = '/g/data/r87/dbi599/figures/delsole/delsole-%s-%s-%s-%s_yr_%s_%s_rall.png'
    command_list.insert(2, outfile)
    if 'pe-amp' in [inargs.xvar, inargs.yvar]:
        command_list.append('--pe_metric amp')
    elif 'pe-abs' in [inargs.xvar, inargs.yvar]:
        command_list.append('--pe_metric abs')
    command = " ".join(command_list)

    if inargs.execute:
        os.system(command)
    print(command) 




python plot_global_indicators.py /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalGHG/yr/ocean/sos/ensmean-i1p1/sos-global-amp_Oyr_CanESM2_historicalGHG_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalMisc/yr/ocean/sos/ensmean-i1p4/sos-global-amp_Oyr_CanESM2_historicalMisc_ensmean-i1p4_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalNat/yr/ocean/sos/ensmean-i1p1/sos-global-amp_Oyr_CanESM2_historicalNat_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historical/yr/ocean/sos/ensmean-i1p1/sos-global-amp_Oyr_CanESM2_historical_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalGHG/yr/atmos/evspsbl/ensmean-i1p1/evspsbl-global-mean_Ayr_CanESM2_historicalGHG_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalGHG/yr/atmos/pr/ensmean-i1p1/pr-global-mean_Ayr_CanESM2_historicalGHG_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalGHG/yr/atmos/tas/ensmean-i1p1/tas-global-mean_Ayr_CanESM2_historicalGHG_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalMisc/yr/atmos/evspsbl/ensmean-i1p4/evspsbl-global-mean_Ayr_CanESM2_historicalMisc_ensmean-i1p4_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalMisc/yr/atmos/pr/ensmean-i1p4/pr-global-mean_Ayr_CanESM2_historicalMisc_ensmean-i1p4_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalMisc/yr/atmos/tas/ensmean-i1p4/tas-global-mean_Ayr_CanESM2_historicalMisc_ensmean-i1p4_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalNat/yr/atmos/evspsbl/ensmean-i1p1/evspsbl-global-mean_Ayr_CanESM2_historicalNat_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalNat/yr/atmos/pr/ensmean-i1p1/pr-global-mean_Ayr_CanESM2_historicalNat_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historicalNat/yr/atmos/tas/ensmean-i1p1/tas-global-mean_Ayr_CanESM2_historicalNat_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historical/yr/atmos/evspsbl/ensmean-i1p1/evspsbl-global-mean_Ayr_CanESM2_historical_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historical/yr/atmos/pr/ensmean-i1p1/pr-global-mean_Ayr_CanESM2_historical_ensmean-i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/CCCMA/CanESM2/historical/yr/atmos/tas/ensmean-i1p1/tas-global-mean_Ayr_CanESM2_historical_ensmean-i1p1_all.nc /g/data/r87/dbi599/figures/global_indicators/global-indcators_yr_CanESM2_historicalAll_ensmean-i1_all.png --aa_physics 4




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
                        help="Physics version for the anthropogenic aerosol only experiment (e.g. p4) [default=None]")
    parser.add_argument("--ant_physics", type=str, default=None,
                        help="Physics version for the anthropogenic only experiment (e.g. p4) [default=None]")
    parser.add_argument("--ensmean", action="store_true", default=False,
                        help="Calculate the ensemble mean first")

    parser.add_argument("--execute", action="store_true", default=False,
                        help="Switch for executing command rather than printing to screen")

    args = parser.parse_args()            
    main(args)
