"""
Filename: plot_scatter.py
Author: Damien Irving, d.irving@student.unimelb.edu.au
Description: Create a scatterplot

"""

# Import general Python modules

import os, sys, pdb

import numpy
import pandas, xray
from scipy.signal import argrelextrema
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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

def get_datetimes(darray, date_file):
    """Generate a list of datetimes common to darray and date_file."""

    if date_file:
        time_dim = map(str, darray['time'].values)
        date_list, date_metadata = gio.read_dates(date_file)
    
        match_dates, miss_dates = uconv.match_dates(date_list, time_dim)
        match_dates = map(numpy.datetime64, match_dates)

    else:
        match_dates = darray['time'].values
        date_metadata = None

    return match_dates, date_metadata


def find_phase(data, lon_axis):
    """Find the location of the first local minima within the search domain."""

    local_min_indexes = argrelextrema(data, numpy.less)
    local_min_lons = lon_axis[local_min_indexes]

    first_lon = next(lon for lon in local_min_lons if lon > 115)

    return first_lon


def main(inargs):
    """Run program."""

    # Read the data
    dset_in = xray.open_dataset(inargs.ift_file)
    gio.check_xrayDataset(dset_in, inargs.ift_var)
    darray = dset_in[inargs.ift_var]

    # Filter data so just the date_list dates remain
    dt_list, dt_list_metadata = get_datetimes(darray, inargs.date_file)
    darray_selection = darray.sel(time=dt_list)

    pdb.set_trace()

    # Get the phase info
    #find_phase(darray_selection)


    

    #gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:

author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot the phase information'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required data
    parser.add_argument("ift_file", type=str, help="Input file for the x-axis")
    parser.add_argument("ift_var", type=str, help="Variable name in x-axis input file")
    parser.add_argument("date_file", type=str, help="Input file for the x-axis")
    parser.add_argument("ofile", type=str, help="Output file name")
    

    args = parser.parse_args()            
    main(args)
