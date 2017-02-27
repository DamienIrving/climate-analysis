"""
Filename:     plot_timeseries.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots timeseries

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

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

def prep_data(cube, var, inargs):
    """Prepare the data."""

    if 'precipitation' in var:
        assert cube.units == 'kg m-2 s-1'
        cube.data = cube.data * 86400
        cube.units = 'mm/day'
    
    if inargs.anomaly:
        temporal_mean = cube.collapsed('time', iris.analysis.MEAN)
        cube = cube - temporal_mean

    return cube


def plot_cube(cube, inargs, pnum):
    """Plot a single cube."""

    if inargs.labels:
        label = inargs.labels[pnum]
    else:
        label=None

    iplt.plot(cube, label=label)


def main(inargs):
    """Run the program."""
  
    if inargs.labels:
        assert len(inargs.labels) == len(inargs.infiles)

    metadata_dict = {}
    for pnum, infile_info in enumerate(inargs.infiles):
        infile, var = infile_info
        try:
            cube = iris.load_cube(infile, var)
        except iris.exceptions.ConstraintMismatchError:
            var = var.replace('_', ' ')
            cube = iris.load_cube(infile, var)

        metadata_dict[infile] = cube.attributes['history']
        
        cube = prep_data(cube, var, inargs)
        plot_cube(cube, inargs, pnum) 

    plt.legend(loc=2)
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

    parser.add_argument("outfile", type=str, help="Output file")
        
    parser.add_argument("--infiles", action='append', nargs=2, metavar=('FILE', 'VAR'), default=[], type=str, 
                        help="Input file and variable name (give long name with underscores for non-standard variable names)")
    parser.add_argument("--labels", type=str, nargs='*', default=None, 
                        help="Legend labels (some can be the word blank)")
    parser.add_argument("--anomaly", action="store_true", default=False,
                        help="Plot the anomaly timeseries [default=False]")

    args = parser.parse_args()             
    main(args)
