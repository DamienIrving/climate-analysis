"""
Filename:     plot_comparison_timeseries.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot a number of timeseries for comparison

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

history = []


def write_met_file(inargs, spatial_cube, outfile):
    """Write the output metadata file."""
    
    infile_history = {}
    infile_history[inargs.infiles[0]] = history[0]

    if spatial_cube:                  
        infile_history[inargs.spatial_file] = spatial_cube.attributes['history']

    gio.write_metadata(outfile, file_info=infile_history)


def normalise_data(cube):
    """Normalise the data."""

    mean = cube.data.mean()
    std = cube.data.std()
    norm = (cube.data - mean) / std

    return norm


def plot_timeseries(pe_cube, sos_cube, tas_cube, window):
    """Plot a timeseries."""

    iplt.plot(pe_cube.rolling_window('time', iris.analysis.MEAN, window), label='P-E')
    iplt.plot(sos_cube.rolling_window('time', iris.analysis.MEAN, window), label='salinity')
    iplt.plot(sos_cube.rolling_window('time', iris.analysis.MEAN, window), label='surface temperature')
    

def main(inargs):
    """Run the program."""

    pe_cube = iris.load_cube(pe_file, 'precipitation minus evaporation flux')
    sos_cube = iris.load_cube(sos_file, 'sea_surface_salinity')
    tas_cube = iris.load_cube(sos_file, 'air_temperature')

    pe_cube.data = pe_cube.data * 86400
    
    pe_cube.data = normalise_data(pe_cube)
    sos_cube.data = normalise_data(sos_cube)
    tas_cube.data = normalise_data(tas_cube)

    fig = plt.figure() #figsize=
    windows = [1, 5, 10, 20]
    for pnum, window in enumerate(windows) :
        ax = fig.add_subplot(4, 1, pnum)
        plt.sca(ax)
        plot_timeseries(pe_cube, sos_cube, tas_cube, window)

    plt.legend(loc=2)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    #write_met_file(inargs, spatial_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 

author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Plot the volumetric (or area-metric) distribution'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("pe_file", type=str, help="P-E file")
    parser.add_argument("sos_file", type=str, help="surface salinity file")
    parser.add_argument("tas_file", type=str, help="surface air temperature file")
    parser.add_argument("outfile", type=str, help="Output file")
        
    args = parser.parse_args()             
    main(args)
