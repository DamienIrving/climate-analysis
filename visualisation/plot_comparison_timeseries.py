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

    #max_abs = numpy.abs(cube.data).max()
    #norm = cube.data / max_abs

    std = numpy.std(cube.data)
    mean = numpy.mean(cube.data)
    norm = (cube.data - mean) / std

    return norm


def running_mean(cube, window):
    """Calculate the running mean."""

    if window > 1:
        runmean = cube.rolling_window('time', iris.analysis.MEAN, window)
    else:
        runmean = cube

    return runmean


def plot_timeseries(pe_cube, sos_cube, tas_cube, window):
    """Plot a timeseries."""

    pe_running_mean = running_mean(pe_cube, window)
    sos_running_mean = running_mean(sos_cube, window)
    tas_running_mean = running_mean(tas_cube, window)

    pe_running_mean.data = normalise_data(pe_running_mean)
    sos_running_mean.data = normalise_data(sos_running_mean)
    tas_running_mean.data = normalise_data(tas_running_mean)

    iplt.plot(pe_running_mean, label='P-E')
    iplt.plot(sos_running_mean, label='salinity')
    iplt.plot(tas_running_mean, label='surface temperature')
    
    plt.legend(loc=4)
    plt.title('running window: ' + str(window))
    plt.ylabel('normalised metric')


def main(inargs):
    """Run the program."""

    pe_cube = iris.load_cube(inargs.pe_file, 'precipitation minus evaporation flux')
    sos_cube = iris.load_cube(inargs.sos_file, 'sea_surface_salinity')
    tas_cube = iris.load_cube(inargs.tas_file, 'air_temperature')

    metadata_dict = {}
    metadata_dict[inargs.pe_file] = pe_cube.attributes['history']
    metadata_dict[inargs.sos_file] = sos_cube.attributes['history']
    metadata_dict[inargs.tas_file] = tas_cube.attributes['history']

    pe_cube.data = pe_cube.data * 86400

    fig = plt.figure(figsize=[15, 15])
    windows = [1, 5, 10, 20, 30, 40]
    for pnum, window in enumerate(windows):
        pnum = pnum + 1
        ax = fig.add_subplot(3, 2, pnum)
        plt.sca(ax)
        plot_timeseries(pe_cube, sos_cube, tas_cube, window)

    fig.suptitle(inargs.experiment) #fontsize=title_size)
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


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
    parser.add_argument("experiment", type=str, help="experiment")
    parser.add_argument("outfile", type=str, help="Output file")
        
    args = parser.parse_args()             
    main(args)
