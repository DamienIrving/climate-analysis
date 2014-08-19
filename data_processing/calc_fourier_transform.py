"""
Filename:     calc_fourier_transform.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
from scipy import fftpack
from scipy import signal
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

try:
    import netcdf_io as nio
    import coordinate_rotation as crot
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #


def apply_lon_filter(data, lon_bounds):
    """Set all values outside of the specified longitude range [lon_bounds[0], lon_bounds[1]] to zero."""
    
    # Convert to common bounds (0, 360) #
 
    lon_min = crot.adjust_lon_range(lon_bounds[0], radians=False, start=0.0)
    lon_max = crot.adjust_lon_range(lon_bounds[1], radians=False, start=0.0)
    lon_axis = crot.adjust_lon_range(data.getLongitude()[:], radians=False, start=0.0)

    # Make required values zero #
    
    ntimes, nlats, nlons = data.shape
    lon_axis_tiled = numpy.tile(lon_axis, (ntimes, nlats, 1))
    
    new_data = numpy.where(lon_axis_tiled < lon_min, 0.0, data)
    
    return numpy.where(lon_axis_tiled > lon_max, 0.0, new_data)


def spectrum(signal_fft, output='amplitude'):
    """Calculate the amplitude or power (amplitude squared 
    spectrum for a given Fourier Transform
    
    The sample frequencies usually include both the positive
    and negative frequencies (which are identical for real functions
    and maybe other times as well), so when plotting the amplitude
    you could just double the positive value??? 
    
    """
    
    assert output in ['amplitude', 'power']
    
    if output == 'amplitude':
        result = numpy.abs(signal_fft)
    elif output == 'power':
        result = numpy.abs(signal_fft)**2
    
    return result
    

def filter_signal(signal, indep_var, min_freq, max_freq, exclusion):
    """Filter a signal by performing a Fourier Tranform and then
    an inverse Fourier Transform for a selected range of frequencies"""
    
    sig_fft, sample_freq = fourier_transform(signal, indep_var)
    filtered_signal = inverse_fourier_transform(sig_fft, sample_freq, min_freq=min_freq, max_freq=max_freq, exclude=exclusion)
    
    return filtered_signal


def fourier_transform(signal, indep_var):
    """Calculate the Fourier Transform.
    
    Input arguments:
        indep_var  ->  Independent variable (i.e. 1 dimensional time axis or longitude axis)
    
    Output:
        sig_fft    ->  Coefficients obtained from the Fourier Transform
        freqs      ->  Wave frequency associated with each coefficient
        power      ->  Power associated with each frequency (i.e. abs(sig_fft))
    
    """
    
    spacing = indep_var[1] - indep_var[0]
    sig_fft = fftpack.fft(signal)
    sample_freq = fftpack.fftfreq(len(indep_var), d=spacing) * len(indep_var) * spacing  # i.e. in units of cycles per length of domain
    sample_freq = numpy.resize(sample_freq, sig_fft.shape)
    
    return sig_fft, sample_freq


def inverse_fourier_transform(coefficients, sample_freq, min_freq=None, max_freq=None, exclude='negative'):
    """Inverse Fourier Transform.
    
    Input arguments:
        max_freq, min_freq   ->  Can filter to only include a certain
                                 frequency range. 
                                 (Note that this filtering keeps both the positive
                                 and negative half of the spectrum)
        exclude              ->  Can exclude either the 'positive' or 
                                 'negative' half of the Fourier spectrum.
                                 (A Hilbert transform, for example, excludes the 
                                 negative part of the spectrum)
                                 
    """
    
    assert exclude in ['positive', 'negative', None]
    
    coefs = deepcopy(coefficients)  # Deep copy to prevent side effects
                                    # (shallow copy not sufficient for complex
                    # things like numpy arrays)
    
    if exclude == 'positive':
        coefs[sample_freq > 0] = 0
    elif exclude == 'negative':
        coefs[sample_freq < 0] = 0
    
    if (max_freq == min_freq) and max_freq:
        coefs[numpy.abs(sample_freq) != max_freq] = 0
    
    if max_freq:
        coefs[numpy.abs(sample_freq) > max_freq] = 0
    
    if min_freq:
        coefs[numpy.abs(sample_freq) < min_freq] = 0
    
    result = fftpack.ifft(coefs)
    
    return result


def first_localmax_index(data):
    localmax_indexes = signal.argrelextrema(data, numpy.greater)
    
    return localmax_indexes[0][0]


def get_coefficients(data, lon_axis, min_freq, max_freq):
    """Return the magnitude and phase coefficient for each frequency in the range [min_freq, max_freq].

    Output:
      - A list: [mag_min_freq, phase_min_freq, ... mag_max_freq, phase_max_freq]
      - The phase is represented by the location of the first local maxima along the longitude axis
    
    """

    outdata_list = [] 
    exclusion = None
    for freq in range(min_freq, max_freq + 1):
        filtered_signal = numpy.apply_along_axis(filter_signal, -1, 
                                                 data, lon_axis, 
                                                 min_freq, max_freq, 
                                                 exclusion)
        localmax_vals = numpy.max(filtered_signal, axis=-1)
        localmax_indexes = numpy.apply_along_axis(first_localmax_index, -1, filtered_signal)
        localmax_lons = map(lambda x: lon_axis[x], localmax_indexes)
        
        outdata_list.append(localmax_vals)
        outdata_list.append(localmax_lons)

    return outdata_list


def get_coefficient_atts(orig_data, min_freq, max_freq):
    """Get the attributes for the coefficient output file

    Output:
      - A list: [mag-atts_min-freq, phase-atts_min-freq, ... mag-atts_max-freq, mag-phase_max-freq] 

    """
    
    method = 'filtered'
    outvar_atts_list = []
    outvar_axes_list = []
    for freq in range(min_freq, max_freq + 1):
        filter_text = get_filter_text(method, freq, freq)
        mag_atts = {'id': 'wave'+str(freq)+'_amp',
                    'standard_name': 'Amplitude of '+method+' '+orig_data.long_name,
                    'long_name': 'Amplitude of '+method+' '+orig_data.long_name,
                    'units': orig_data.units,
                    'history': filter_text}
        outvar_atts_list.append(mag_atts)
        outvar_axes_list.append(orig_data.getAxisList()[:-1])
        
        phase_atts = {'id': 'wave'+str(freq)+'_phase',
                      'standard_name': 'First local maxima of '+method+' '+orig_data.long_name,
                      'long_name': 'First local maxima of '+method+' '+orig_data.long_name,
                      'units': orig_data.getLongitude().units,
                      'history': filter_text}
        outvar_atts_list.append(phase_atts)    
        outvar_axes_list.append(orig_data.getAxisList()[:-1])

    return outvar_atts_list, outvar_axes_list


def hilbert_transform(data, lon_axis, min_freq, max_freq, out_type=None):
    """Perform the Hilbert transform.

    There is the option of placing the output array in a list of length 1
    (this is useful in some cases)

    """
    
    exclusion = 'negative'
    outdata = numpy.apply_along_axis(filter_signal, -1, 
                                     data, lon_axis, 
                                     min_freq, max_freq, 
                                     exclusion)
    outdata = 2 * numpy.abs(outdata)

    if out_type == list:
        return [outdata,]
    else:
        return outdata


def get_hilbert_atts(orig_data, min_freq, max_freq):
    """Get the attributes for the output Hilbert transform file"""
   
    method = 'Hilbert transformed'
    filter_text = get_filter_text(method, min_freq, max_freq)
    var_atts = {'id': orig_data.id,
                'standard_name': method+' '+orig_data.long_name,
                'long_name': method+' '+orig_data.long_name,
                'units': orig_data.units,
                'history': filter_text}

    outvar_atts_list = [var_atts,]
    outvar_axes_list = [orig_data.getAxisList(),]

    return outvar_atts_list, outvar_axes_list


def get_filter_text(method, min_freq, max_freq):
    """Get the history attribute text according to the analysis
    method and frequency range"""

    if min_freq and max_freq:
        filter_text = '%s with frequency range: %s to %s' %(method, min_freq, max_freq)
    else:
        filter_text = '%s with all frequencies retained' %(method)

    return filter_text


def main(inargs):
    """Run the program."""
    
    # Read input data #
    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'latitude']))
    
    assert indata.data.getOrder()[-1] == 'x', \
    'This script is setup to perform the fourier transform along the longitude axis'
    
    # Apply longitude filter (i.e. set unwanted longitudes to zero) #
    data_masked = apply_lon_mask(indata.data, inargs.longitude) if inargs.longitude else indata.data
    
    # Perform task #
    min_freq, max_freq = inargs.filter
    if inargs.outtype == 'coefficients':
        outdata_list = get_coefficients(data_masked, indata.data.getLongitude()[:], min_freq, max_freq)
        outvar_atts_list, outvar_axes_list = get_coefficient_atts(indata.data, min_freq, max_freq)
    elif inargs.outtype == 'hilbert':
        outdata_list = hilbert_transform(data_masked, indata.data.getLongitude()[:], min_freq, max_freq, out_type=list)
        outvar_atts_list, outvar_axes_list = get_hilbert_atts(indata.data, min_freq, max_freq)

    # Write output file #
    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     indata.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
    /usr/local/uvcdat/1.5.1/bin/cdat calc_fourier_transform.py 
    va_Merra_250hPa_30day-runmean-Jun2002_r360x181.nc va test.nc 
    --filter 2 9 --outtype hilbert
author:
    Damien Irving, d.irving@student.unimelb.edu.au
notes:
    Note that the Hilbert transform excludes the negative half 
    of the frequency spectrum and doubles the final amplitude. This does not
    give the same result as if you simply retain the negative half.
references:
    http://docs.scipy.org/doc/numpy/reference/routines.fft.html
    http://gribblelab.org/scicomp/09_Signals_sampling_filtering.html
    
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
                        help="Longitude range over which to perform Fourier Transform (all other values are set to zero) [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    # Output options
    parser.add_argument("--filter", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=None,
                        help="Range of frequecies to retain in filtering [e.g. 3,3 would retain the wave that repeats 3 times over the domain")
    parser.add_argument("--outtype", type=str, default='hilbert', choices=('hilbert', 'coefficients'),
                        help="The output can be a hilbert transform or the magnitude and phase coefficients for each frequency")

  
    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
