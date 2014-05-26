"""
Filename:     calc_fourier_transform.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules

import sys, os
import argparse
import numpy
from scipy import fftpack
import matplotlib.pyplot as plt
from copy import deepcopy

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
vis_dir = os.path.join(repo_dir, 'visualisation')
sys.path.append(vis_dir)

try:
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #


def filter_signal(signal, indep_var, min_freq, max_freq):
    """Filter a signal by performing a Fourier Tranform and then
    an inverse Fourier Transform for a selected range of frequencies"""
    
    sig_fft, sample_freq, freqs, power = fourier_transform(signal, indep_var)
    filtered_signal = inverse_fourier_transform(sig_fft, sample_freq, min_freq=min_freq, max_freq=max_freq)
    
    return filtered_signal


def fourier_transform(signal, indep_var):
    """Calculate the Fourier Transform.
    
    Input arguments:
        indep_var  ->  Independent variable (i.e. time axis or longitude axis)
    
    Output:
        sig_fft    ->  Coefficients obtained from the Fourier Transform
        freqs      ->  Wave frequency associated with each coefficient
        power      ->  Power associated withe each frequency (i.e. abs(sig_fft))
    
    """
    
    spacing = indep_var[1] - indep_var[0]
    sample_freq = fftpack.fftfreq(signal.size, d=spacing) * signal.size * spacing  # i.e. in units of cycles per length of domain
    sig_fft = fftpack.fft(signal)
    pidxs = numpy.where(sample_freq > 0)
    freqs, power = sample_freq[pidxs], numpy.abs(sig_fft)[pidxs]
    
    return sig_fft, sample_freq, freqs, power


def inverse_fourier_transform(coefficients, sample_freq, min_freq=None, max_freq=None, exclude=None):
    """Inverse Fourier Transform.
    
    Input arguments:
        max_freq, min_freq   ->  Can filter to only include a certain
                                 frequency range. 
	exclude              ->  Can exclude either the 'positive' or 
	                         'negative' half of the Fourier spectrum  
                                 
    """
    
    assert exclude in ['positive', 'negative', None]
    
    coefs = deepcopy(coefficients)  # Deep copy to prevent side effects
                                    # (shallow copy not sufficient for complex
				    # things like numpy arrays)
    
    if exclude == 'positive':
        coefs[sample_freq > 0] = 0
    elif exclude == 'negative':
        coefs[sample_freq < 0] = 0
    
    if max_freq == min_freq and max_freq:
        coefs[numpy.abs(sample_freq) != max_freq] = 0
    
    if max_freq:
        coefs[numpy.abs(sample_freq) > max_freq] = 0
    
    if min_freq:
        coefs[numpy.abs(sample_freq) < min_freq] = 0
    
    result = fftpack.ifft(coefs)
    
    return result


def plot_spectrum(freqs, power, window=20):
    """Plot power spectrum.
    
    Input arguments:
        Window  -> There is an inset winow for the first 0:window frequencies
    
    """
    
    plt.figure()  
    
    # Outer plot
    plt.plot(freqs, power)
    plt.xlabel('Frequency [cycles / domain]')
    plt.ylabel('power')
    
    # Inner plot
    axes = plt.axes([0.3, 0.3, 0.5, 0.5])
    plt.title('Peak frequency')
    plt.plot(freqs[:window], power[:window])
    plt.setp(axes, yticks=[])
    plt.show()


def main(inargs):
    """Run the program."""
    
    # Read input data #
    
    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'latitude']))
    
    assert indata.data.getOrder() == 'tyx', \
    'This script only works if the input data has a time, latitude and longitude axis'
     
    # Perform the filtering #
    
    if inargs.filter:
        min_freq, max_freq = inargs.filter
	filter_text = 'Fourier transform filtering with frequency range: %s to %s' %(min_freq, max_freq)
    else:
        min_freq = max_freq = None
	filter_text = 'Fourier transform filtering with all frequencies retained'
    
    outdata = numpy.apply_along_axis(filter_signal, 2, indata.data, indata.data.getLongitude()[:], min_freq, max_freq)
    
    # Write output file #

    var_atts = {'id': indata.data.id,
                'standard_name': 'Frequency filtered '+indata.data.long_name,
                'long_name': 'Frequency filtered '+indata.data.long_name,
                'units': indata.data.units,
                'history': filter_text}

    outdata_list = [outdata,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [indata.data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     indata.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Perform Fourier Transform along lines of constant latitude'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
			
    # Input data options
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range over which to perform Fourier Transform [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'), default=None,
                        help="Longitude range over which to perform Fourier Transform [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    # Output options
    parser.add_argument("--filter", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=None,
                        help="Range of frequecies to retain in filtering [e.g. 3,3 would retain the wave that repeats 3 times over the domain")
    parser.add_argument("--spectrum", action="store_true", default=False, 
                        help="Switch for plotting the spectrum [default: False]")

  
    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
