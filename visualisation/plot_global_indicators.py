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
    """Run the program."""

    # Read and group data
    timeseries_data = {}
    for filename in inargs.infiles:
        cube = iris.load_cube(filename)

        standard_name = cube.standard_name
        experiment = cube.attributes['experiment']
        if experiment == 'historicalMisc':
            physics = cube.attributes['physics_version']
            experiment = 'historicalAA' # or historicalAnt
               
        key = (standard_name, experiment)
        if key in timeseries_data.keys():
            timeseries_data(key).append(cube)
        else:
            timeseries_data(key) = [cube,]
     
    # take ensemble mean of each group (hopefully without losing time axis metadata??)
    # create 3 subplots       
         
    plt.savefig(inargs.outfile, bbox_inches='tight')

    metadata_dict = get_metadata(inargs, cube, climatology) 
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
example:
/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/historical/yr/atmos/tas/r1i1p1/tas-global-mean_Ayr_IPSL-CM5A-LR_historical_r1i1p1_185001-200512.nc  
/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/historical/yr/atmos/evspsbl/r1i1p1/evspsbl-global-mean_Ayr_IPSL-CM5A-LR_historical_r1i1p1_185001-200512.nc
/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/historical/yr/atmos/pr/r1i1p1/pr-global-mean_Ayr_IPSL-CM5A-LR_historical_r1i1p1_185001-200512.nc
/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/historical/yr/ocean/sos/r1i1p1/sos-global-amp_Oyr_IPSL-CM5A-LR_historical_r1i1p1_185001-200512.nc

"""

    description='Plot global mean surface temperature, salinity amplifcation and P-E'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input global metric files")
    parser.add_argument("outfile", type=str, help="Output file name")

    ## Options to designate the Ant vs AA historicalMisc run

    args = parser.parse_args()            
    main(args)
