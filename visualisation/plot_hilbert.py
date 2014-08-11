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

def plot_hilbert(original_signal, filtered_signal, 
                 amp_spectrum, sample_freq,
                 env_mermax,
                 xaxis,
                 ybounds,  
                 wmin, wmax,
                 lat_single_tag, lat_range_tag,
                 outfile, title=None):
    """Plot the Hilbert transform and key components of it"""

    fig = plt.figure()
    
    axes1 = fig.add_axes([0.1, 0.1, 0.8, 0.8]) # [left, bottom, width, height]
    axes2 = fig.add_axes([0.11, 0.11, 0.18, 0.115]) # inset axes
    
    # Outer plot

    #original signal, single lat
    tag = 'original signal, %s' %(lat_single_tag)
    axes1.plot(xaxis, numpy.array(original_signal), color='green', label=tag)

    #individual wavenumber components, for single lat
    for wavenum in range(1, 10):
        axes1.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], 
                   color='0.5', linestyle='--')
    
    #full reconstructed signal, single lat
    tag = 'wave %s-%s signal, %s'  %(str(wmin), str(wmax), lat_single_tag)
    axes1.plot(xaxis, 2*filtered_signal['positive', wmin, wmax], color='orange', linestyle='--', label=tag)
    
    #full reconstructed envelope, single lat
    tag = 'wave %s-%s envelope, %s'  %(str(wmin), str(wmax), lat_single_tag)
    axes1.plot(xaxis, numpy.abs(2*filtered_signal['positive', wmin, wmax]), color='orange', label=tag)
    
    #meridional maximum reconstructed envelope, over full lat range
    tag = 'mermax envelope, %s'  %(lat_range_tag)
    axes1.plot(xaxis, numpy.array(env_mermax), color='red', label=tag)

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


def set_ybounds(timescale, timestep, user_bounds):
    """Define the y-axis bounds.
    
    If user_bounds is None (i.e. the user didn't supply the bounds),
    then the decision is based on the timescale and timestep.
    
    timescale  -->   e.g. 30day-runmean
    timestep   -->   e.g. daily, monthly

    """

    ybounds_tscale_dict={'01day-runmean': [-50, 50],
                         '05day-runmean': [-40, 40],
                         '30day-runmean': [-20, 20],
                         '90day-runmean': [-15, 15]}
    ybounds_tstep_dict = {'daily': ybounds_tscale_dict['01day-runmean'],
                          'monthly': ybounds_tscale_dict['30day-runmean']}

    if user_bounds:
        ybounds = user_bounds
    elif timescale in ybounds_tscale_dict.keys():
        ybounds = ybounds_tscale_dict[timescale]
    elif timestep in ybounds_tstep_dict.keys():
        ybounds = ybounds_tstep_dict[timestep]
    else:
        ybounds = None

    return ybounds


def get_hemisphere(lat):
    """For a given latitude, return N or S"""

    if lat < 0.0:
        return 'S'
    else:
        return 'N' 


def main(inargs):
    """Plot each timestep."""
    
    indata = nio.InputData(inargs.infile, inargs.variable,
                           **nio.dict_filter(vars(inargs), ['time', 'latitude']))
    
    lat_target = (inargs.latitude[0] + inargs.latitude[1]) / 2.0
    lat_selection = nio.find_nearest(indata.data.getLatitude()[:], lat_target)
    xaxis = indata.data.getLongitude()[:]
    wmin, wmax = inargs.wavenumbers
    for date in indata.data.getTime().asComponentTime()[::inargs.stride]:
        date_bounds, date_abbrev = nio.get_cdms2_tbounds(date, inargs.timestep)
        data_selection = indata.data(time=(date_bounds[0], date_bounds[1]), squeeze=1)
        data_selection_lat = data_selection(latitude=lat_selection, squeeze=1)        
        
        # Title (i.e. date and latitude info)
        lat_single_tag = '%s%s' %(str(abs(lat_selection)), get_hemisphere(lat_selection))       
        lat_range_tag = '%s%s-%s%s' %(str(abs(inargs.latitude[0])), get_hemisphere(inargs.latitude[0]), 
                                      str(abs(inargs.latitude[1])), get_hemisphere(inargs.latitude[1])) 

        # y-axis bounds
        ybounds = set_ybounds(inargs.timescale, inargs.timestep, inargs.ybounds)
	
        # Outfile
        outfile_name = gio.set_outfile_date(inargs.ofile, date)

        # Fourier transform, single lat
        sig_fft, sample_freq = cft.fourier_transform(data_selection_lat, xaxis)

        # Individual Fourier components, single lat
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

        # Meridional maximum envelope
        lat_index = data_selection.getOrder().index('y')
        lon_index = data_selection.getOrder().index('x')
        exclusion = 'negative'
        env = numpy.apply_along_axis(cft.filter_signal, lon_index, data_selection, xaxis, wmin, wmax, exclusion)
        env = 2 * numpy.abs(env)
        env_mermax = numpy.amax(env, axis=lat_index)
      
        # Plot
        plot_hilbert(data_selection_lat, filtered_signal, 
                     amp_spectrum, sample_freq, 
                     env_mermax,
                     xaxis, 
                     ybounds,
                     wmin, wmax, 
                     lat_single_tag, lat_range_tag,
                     outfile_name, title=date_abbrev)
        metadata = [[indata.fname, indata.id, indata.global_atts['history']],]
        gio.write_metadata(outfile_name, file_info=metadata)    


if __name__ == '__main__':

    extra_info = """ 

example:
    /usr/local/uvcdat/1.3.0/bin/cdat plot_hilbert.py 
    va_Merra_250hPa_30day-runmean_r360x181.nc va daily 
    hilbert-va_Merra_250hPa_30day-runmean_r360x181-50S_2002-06-30.png 
    --latitude -70 -40
    --timescale 30day-runmean
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
    parser.add_argument("timestep", type=str, help="distance between timesteps (e.g. daily, monthly)")
    parser.add_argument("ofile", type=str, 
                        help="name of output file (include the date of one of the timesteps in YYYY-MM-DD format - it will be replaced in place)")

    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range over which to extract waves [default = entire]")    
    parser.add_argument("--timescale", type=str, default=None, 
                        help="timescale of the input data (e.g. 05day-runmean) - use this when timescale differs from timestep")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")
    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[2, 9],
                        help="Wavenumber range [default = (2, 9)]. The upper and lower values are included (i.e. default selection includes 2 and 9).")
    parser.add_argument("--ybounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=None,
                        help="y-axis bounds (there are defaults set for each timescale)")
    parser.add_argument("--stride", type=int, default=1,
                        help="Stride for dates to plot (e.g. 3 would plot every third timestep)")
  
    args = parser.parse_args()            

    main(args)
