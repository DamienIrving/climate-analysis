"""
Filename:     plot_hilbert.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Produce a number of plots for testing and 
              understanding the Hilbert Transform
"""

# Import general Python modules #

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import cdms2, cdutil
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
anal_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(anal_dir)

try:
    import netcdf_io as nio
    import general_io as gio
    import calc_fourier_transform as cft
except ImportError:
    raise ImportError('Must run this script from within phd git repo')


# Define functions #

def get_hemisphere(lat):
    """For a given latitude, return N or S"""

    if lat < 0.0:
        return 'S'
    else:
        return 'N' 


def get_lat_target(fname, lat_desired):
    """Identify the latitude closest to the desired"""

    fin = cdms2.open(fname)
    lat_name = next(dim for dim in fin.listdimension() if 'lat' in dim)
    lat_target = nio.find_nearest(fin.getAxis(lat_name)[:], lat_desired)
    fin.close()

    return lat_target


def extract_data(fname, var, lat, dates):
    """Extract the data for the given latitude and dates""" 

    lat_target = get_lat_target(fname, lat)
    data_dict = {}
    metadata_dict = {}

    for date in dates:
        indata = nio.InputData(fname, var, time=(date, date), latitude=lat_target)
        data_dict[date] = indata.data

    metadata_dict[fname] = indata.global_atts['history']

    return data_dict, metadata_dict, lat_target
 

def plot_hilbert(data_dict, date_list,
                 wmin, wmax,
                 nrows, ncols,
                 latitude,
                 outfile='test.png',
                 ybounds=None,
                 figure_size=None):
    """Create the plot"""

    fig = plt.figure(figsize=figure_size)
    if not figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    lat_tag = '%s%s' %(str(abs(latitude)), get_hemisphere(latitude))

    for index in range(0, len(date_list)):
        plotnum = index + 1
        date = date_list[index]
        data = data_dict[date]
        xaxis = data.getLongitude()[:]

        ax = plt.subplot(nrows, ncols, plotnum)
        plt.sca(ax)

        # Fourier transform
        sig_fft, sample_freq = cft.fourier_transform(data, xaxis)

        # Individual Fourier components
        filtered_signal = {}
        for filt in [None, 'positive', 'negative']:
            for wave_min in range(wmin, wmax + 1):
                for wave_max in range(wmin, wmax + 1):
                    filtered_signal[filt, wave_min, wave_max] = cft.inverse_fourier_transform(sig_fft, sample_freq, 
                                                                                              min_freq=wave_min, 
                                                                                              max_freq=wave_max, 
                                                                                              exclude=filt)

        ax.axhline(y=0.0, linestyle='-', color='0.8')
        
        # Plot original signal
        tag = 'meridional wind, %s'  %(lat_tag)
        ax.plot(xaxis, numpy.array(data), color='green', label=tag)

        # Plot reconstructed signal
        tag = 'reconstructed signal (waves %s-%s)'  %(str(wmin), str(wmax))
        ax.plot(xaxis, 2*filtered_signal['positive', wmin, wmax], color='orange', linestyle='--', label=tag)

        # Plot reconstructed envelope
        tag = 'wave envelope'
        ax.plot(xaxis, numpy.abs(2*filtered_signal['positive', wmin, wmax]), color='orange', label=tag)

        # Plot individual wavenumber components
        for wavenum in range(wmin, wmax):
            ax.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], color='0.5', linestyle='--')
        ax.plot(xaxis, 2*filtered_signal['positive', wmax, wmax], color='0.5', linestyle='--', label='Fourier components')

        # Plot details
        ax.set_xlim(0, 360)
        if ybounds:
            ax.set_ylim(ybounds) 

        ax.set_title(date)
        
        ax.set_ylabel('$m s^{-1}$', fontsize='medium')
        ax.set_xlabel('longitude', fontsize='medium')

        font = font_manager.FontProperties(size='small')
        ax.legend(loc=4, prop=font)

    plt.savefig(outfile)


def main(inargs):
    """Plot each timestep."""

    # Extract data #
    
    data_dict, metadata_dict, latitude = extract_data(inargs.infile, inargs.variable, inargs.latitude, inargs.dates)    

    # Creat the plot
    
    wmin, wmax = inargs.wavenumbers
    plot_hilbert(data_dict, inargs.dates,
                 wmin, wmax,
                 inargs.nrows, inargs.ncols,
                 latitude,
                 outfile=inargs.ofile,
                 ybounds=inargs.ybounds,
                 figure_size=inargs.figure_size)

    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info = """ 

example:


author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description = 'Explore the Hilbert transform'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("ofile", type=str, help="name of output file")
    parser.add_argument("nrows", type=int, help="number of rows in the entire grid of plots")
    parser.add_argument("ncols", type=int, help="number of columns in the entire grid of plots")

    parser.add_argument("--latitude", type=float, default=-45, 
                        help="Latitude along which to extract the waves [default = -45]")
    parser.add_argument("--dates", type=str, nargs='*',
                        help="Dates to plot")
    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[1, 9],
                        help="Wavenumbers to include in the Hiblert Transform and on the plot")
    parser.add_argument("--ybounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=None,
                        help="y-axis bounds (there are defaults set for each timescale)")

    parser.add_argument("--figure_size", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
  
    args = parser.parse_args()            

    main(args)
