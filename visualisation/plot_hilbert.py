"""
Filename:     plot_hilbert.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Produce a number of plots for testing and 
              understanding the Hilbert Transform
"""

# Import general Python modules #

import sys, os
import argparse
import numpy
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import cdms2
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pdb

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

def plot_hilbert(original_signal, filtered_signal, 
                 amp_spectrum, sample_freq,
                 xaxis,
                 ybounds,  
                 wmin, wmax,
                 outfile, title=None):
    """Plot the Hilbert transform and key components of it"""

    fig = plt.figure()
    
    axes1 = fig.add_axes([0.1, 0.1, 0.8, 0.8]) # [left, bottom, width, height]
    axes2 = fig.add_axes([0.11, 0.11, 0.18, 0.115]) # inset axes
    
    # Outer plot
    for wavenum in range(1, 10):
        axes1.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], 
                   color='0.5', linestyle='--')

    axes1.plot(xaxis, 2*filtered_signal['positive', wmin, wmax], color='red', linestyle='--', label='w'+str(wmin)+'-'+str(wmax)+' signal')
    axes1.plot(xaxis, numpy.abs(2*filtered_signal['positive', wmin, wmax]), color='red', label='w'+str(wmin)+'-'+str(wmax)+' envelope')
    axes1.plot(xaxis, numpy.array(original_signal), color='green', label='original signal')

    axes1.set_ylim(ybounds)
    if title:
        axes1.set_title(title)
    font = font_manager.FontProperties(size='small')
    axes1.legend(loc=4, prop=font)
    
    # Inner plot    
    freqs = sample_freq[1:10]
    axes2.plot(sample_freq[1:10], amp_spectrum[1:10], '-o')
    axes2.get_xaxis().set_visible(False)
    axes2.get_yaxis().set_visible(False)
    #axes2.set_xlabel('Frequency [cycles / domain]')
    #axes2.set_ylabel('amplitude')
    
    plt.savefig(outfile)
    plt.clf()


def main(inargs):
    """Plot each timestep."""
    
    indata = nio.InputData(inargs.infile, inargs.variable,
                             **nio.dict_filter(vars(inargs), ['time', 'latitude']))
    xaxis = indata.data.getLongitude()[:]
    wmin, wmax = inargs.wavenumbers
    for date in indata.data.getTime().asComponentTime():
        date_bounds, date_abbrev = nio.get_cdms2_tbounds(date, inargs.timestep)
        data_selection = indata.data(time=(date_bounds[0], date_bounds[1]), squeeze=1)
        
        # Title (i.e. date and latitude info)
        hemisphere = 'S' if inargs.latitude < 0.0 else 'N'
        title = '%s %s%s' %(date_abbrev, str(int(abs(inargs.latitude))), hemisphere)       

        # y-axis bounds
        ybounds_dict={'01day-runmean': [-50, 50],
                      '05day-runmean': [-40, 40],
                      '30day-runmean': [-20, 20],
                      '90day-runmean': [-10, 10]}
        if inargs.ybounds:
            ybounds = inargs.ybounds
        elif inargs.timescale in ybounds_dict.keys():
            ybounds = ybounds_dict[inargs.timescale]
        else:
            ybounds = None
	
        # Outfile
        outfile_name = gio.set_outfile_date(inargs.ofile, date)

        # Hilbert transform
        sig_fft, sample_freq = cft.fourier_transform(data_selection, xaxis)

        # Individual Fourier components
        filtered_signal = {}
        for filt in [None, 'positive', 'negative']:
            for wave_min in range(1, 10):
                for wave_max in range(1, 10):
                    filtered_signal[filt, wave_min, wave_max] = cft.inverse_fourier_transform(sig_fft, sample_freq, 
                                                                                              min_freq=wave_min, 
                                                                                              max_freq=wave_max, 
                                                                                              exclude=filt)

        # Amplitude spectra
        amp_spectrum = cft.spectrum(sig_fft, output='amplitude')
        freqs = sample_freq[1:wave_max+1]
    
        # Plot
        plot_hilbert(data_selection, filtered_signal, 
                     amp_spectrum, sample_freq, 
                     xaxis, 
                     ybounds,
                     wmin, wmax, 
                     outfile_name, title=title)
        metadata = [[indata.fname, indata.id, indata.global_atts['history']],]
        gio.write_metadata(outfile_name, file_info=metadata)    


if __name__ == '__main__':

    extra_info = """ 

example:
    /usr/local/uvcdat/1.3.0/bin/cdat plot_hilbert.py 
    va_Merra_250hPa_30day-runmean_r360x181.nc va 
    -50 30day-runmean daily 
    hilbert-va_Merra_250hPa_30day-runmean_r360x181-50S_2002-06-30.png 
    --time 2002-06-01 2002-06-30 none

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
    parser.add_argument("latitude", type=float, help="Single latitude over which to extract the wave")
    parser.add_argument("timescale", type=str, help="timescale of the input data (e.g. 05day-runmean)")
    parser.add_argument("timestep", type=str, help="distance between timesteps (e.g. daily, monthly)")
    parser.add_argument("ofile", type=str, 
                        help="name of output file (include the date of one of the timesteps in YYYY-MM-DD format - it will be replaced in place)")
    
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")
    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[2, 9],
                        help="Wavenumber range [default = (2, 9)]. The upper and lower values are included (i.e. default selection includes 2 and 9).")
    parser.add_argument("--ybounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=None,
                        help="y-axis bounds (there are defaults set for each timescale)")
  
    args = parser.parse_args()            

    main(args)
