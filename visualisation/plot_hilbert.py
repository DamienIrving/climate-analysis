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

    axes1.plot(xaxis, 2*filtered_signal['positive', wmin, wmax], 
               color='red', linestyle='--', 
	       label='w'+str(wmin)+'-'+str(wmax)+' signal')
    axes1.plot(xaxis, numpy.abs(2*filtered_signal['positive', wmin, wmax]), 
               color='red', 
	       label='w'+str(wmin)+'-'+str(wmax)+' envelope')
    axes1.plot(xaxis, numpy.array(original_signal), 
               color='green', 
	       label='original signal')

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
    """Run the program."""

    wmin, wmax = inargs.wavenumbers
    for i in range(0, inargs.ndates):
        
	# Date
        start = datetime.strptime(inargs.start_date, '%Y-%m-%d')
        dt = start + relativedelta(days=i)
        date = dt.strftime('%Y-%m-%d')
        
	# Data
	lat = inargs.latitude
	indata = nio.InputData(inargs.infile, inargs.variable,
                               latitude=(lat - 0.1, lat + 0.1), 
			       time=(date, date))
	xaxis = indata.data.getLongitude()[:]

        # Title (i.e. date and latitude info)
        hemisphere = 'S' if inargs.latitude < 0.0 else 'N'
        tag = '%s %s%s' %(date, str(int(abs(inargs.latitude))), hemisphere)       

        # Outfile
	outfile_name = gio.set_outfile_date(inargs.ofile, date)

        # Hilbert transform
        sig_fft, sample_freq = cft.fourier_transform(indata.data, xaxis)

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
        plot_hilbert(indata.data, filtered_signal, 
	             amp_spectrum, sample_freq, 
		     xaxis, 
		     wmin, wmax, 
		     outfile_name, title=None)
        metadata = [[indata.fname, indata.id, indata.global_atts['history']],]
        gio.write_metadata(outfile_name, file_info=metadata)    


if __name__ == '__main__':

    extra_info = """ 

example:
    /usr/local/uvcdat/1.4.0/bin/cdat plot_hilbert.py 
    ~/Downloads/Data/va_Merra_250hPa_30day-runmean-2002_r360x181.nc va -50 2002-04-17

notes:
   Interesting dates are 2002-01-15 (extent=180), 2002-01-23 (extent=150), 2002-02-13 (extent=100), 
   2002-04-24 (extent=350), 2002-05-12 (extent=360), 2002-06-19 (extent=240)                     

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
    parser.add_argument("latitude", type=float, help="Latitude over which to extract the wave")
    parser.add_argument("start_date", type=str, help="Start date for which to extract the wave")
    parser.add_argument("ofile", type=str, 
                        help="name of output file (include the date of one of the timesteps in YYYY-MM-DD format - it will be replaced in place)")
    
    parser.add_argument("--ndates", type=int, default=1, 
                        help="Number of dates (starting from start_date) to plot")    
    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[2, 9],
                        help="Wavenumber range [default = (2, 9)]. The upper and lower values are included (i.e. default selection includes 2 and 9).")
  
    args = parser.parse_args()            

    main(args)
