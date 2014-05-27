"""
Filename:     plot_hilbert.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Produce a number of plots for testing and understanding 
              the Hilbert Transform

"""

# Import general Python modules #

import sys, os
import argparse
import numpy
import matplotlib.pyplot as plt
import cdms2
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
vis_dir = os.path.join(repo_dir, 'visualisation')
sys.path.append(vis_dir)

try:
    import netcdf_io as nio
    import calc_fourier_transform as cft
    import calc_envelope as cenv
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions # 

def simple_signal():
    """Define a sample signal"""
    
    numpy.random.seed(1234)

    time_step = 1.
    period = 120.

    time_vec = numpy.arange(0, 360, time_step)
#    signal = numpy.cos(((2 * numpy.pi) / period) * time_vec) + 0.5 * numpy.random.randn(time_vec.size)
#    signal = numpy.cos(((2 * numpy.pi) / 360.) * time_vec) + numpy.sin(((2 * numpy.pi) / 180.) * time_vec) + \
#             numpy.sin(((2 * numpy.pi) / 120.) * time_vec) - numpy.cos(((2 * numpy.pi) / 90.) * time_vec) 
#             + 0.5 * numpy.random.randn(time_vec.size)
    signal = numpy.cos(((2 * numpy.pi) / (360. / 6.)) * time_vec) + numpy.cos(((2 * numpy.pi) / (360. / 7.)) * time_vec) + \
             numpy.cos(((2 * numpy.pi) / (360. / 8.)) * time_vec)

    signal = 3 * signal
    
    return time_vec, signal


def data_signal(infile, var, lon, date):
    fin = cdms2.open(infile)
    data = fin(var, latitude=(float(lon) - 0.1, float(lon) + 0.1), time=(date, date), squeeze=1)
    xaxis = data.getLongitude()[:]
    
    return numpy.array(xaxis), numpy.array(data)
    
    
# Individual wavenumber plots

def plot_wavenumbers(num_list, filtered_signal, xaxis):
    """Plot the individual wavenumbers, including their positive and negative wavenumber bits"""
    
    colors = ['blue', 'red', 'green', 'orange', 'pink', 'black', 'purple', 'brown', 'cyan', 'magenta']
    for wavenum in num_list:
        plt.plot(xaxis, 2*filtered_signal[None, wavenum, wavenum], color=colors[wavenum-1], label='w'+str(wavenum))
        plt.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], color=colors[wavenum-1], linestyle=':')
        plt.plot(xaxis, 2*filtered_signal['negative', wavenum, wavenum], color=colors[wavenum-1], linestyle='--')

    plt.legend()
    plt.savefig('individual_wavenumbers.png')
    plt.clf()


def plot_hilbert(num_list, filtered_signal, xaxis):
    """Plot the Hilbert transform and key components of it"""

    for wavenum in num_list:
        plt.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], color='0.5', linestyle='--', label='w'+str(wavenum))

    plt.plot(time_vec, 2*filtered_signal[None, 2, 4], color='blue', label='exclude none')
    plt.plot(time_vec, 2*filtered_signal['positive', 2, 4], color='blue', linestyle=':', label='exclude pos')
    plt.plot(time_vec, 2*filtered_signal['negative', 2, 4], color='blue', linestyle='--', label='exclude neg')

    plt.legend()
    plt.savefig('scipy_w234_results.png')
    plt.clf()

    # Plot amplitude
    plt.plot(time_vec, sig, label='original', color='green')
    plt.plot(time_vec, numpy.abs(2*filtered_signal['positive', 2, 4]), color='blue', label='pos amplitude w234')

    sum_pos_signals = 2*filtered_signal['positive', 2, 2] + 2*filtered_signal['positive', 3, 3] + 2*filtered_signal['positive', 4, 4]
    plt.plot(time_vec, sum_pos_signals, color='blue', linestyle=':', label='postive sum w234')

    sum_all_signals = 2*filtered_signal[None, 2, 2] + 2*filtered_signal[None, 3, 3] + 2*filtered_signal[None, 4, 4]
    plt.plot(time_vec, sum_all_signals, color='blue', linestyle='--', label='all sum w234')

    plt.legend()
    plt.savefig('scipy_w234_hilbert_results.png')
    plt.clf()



# : -. --
#plt.plot(time_vec, 2*filtered_signal, color='orange', label='w234')
#sum_signals = filtered_signal_all_wavenum2 + filtered_signal_all_wavenum3 + filtered_signal_all_wavenum4

def main(inargs):
    """Run the program."""
    
    # Get the data
    
    if switch:
        xaxis, sig = simple_signal()
    else:
        xaxis, sig = data_signal(inargs.infile, inargs.var, inargs.longitude, inargs.date)

    # Do the Hilbert transform (with the fast scipy routines)
    
    sig_fft, sample_freq, freqs, power = cft.fourier_transform(sig, xaxis)
 
    filtered_signal = {}
    wavenum_list = range(inargs.wavenumbers[0], inargs.wavenumbers[-1] + 1)
    for filt in [None, 'positive', 'negative']:
        for wave_min in wavenum_list:
            for wave_max in wavenum_list:
	        filtered_signal[filt, wave_min, wave_max] = cft.inverse_fourier_transform(sig_fft, sample_freq, 
	                                                                                  min_freq=wave_min, max_freq=wave_max, 
										          exclude=filt)
    
    # Plot power spectrum
    
    # Plot using my Hilbert transform to confirm result
    
    my_result = cenv.envelope(sig, inargs.wavenumbers[0], inargs.wavenumbers[-1])
    plt.plot(xaxis, my_result)
    plt.plot(xaxis, sig)
    plt.savefig('my_hilbert_transform.png')
    plt.clf()
    
    


if __name__ == '__main__':

    extra_info =""" 

example:
    ~/Downloads/Data/va_Merra_250hPa_30day-runmean-2002_r360x181.nc
author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Explore the Hilbert transform'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("longitude", type=str, help="Longitude over which to extract the wave")
    parser.add_argument("date", type=str, help="Date for which to extract the wave")

    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[1, 10],
                        help="Wavenumber range [default = (1, 10)]. The upper and lower values are included (i.e. default selection includes 1 and 10).")
    parser.add_argument("--simple", action="store_true", default=False,
                        help="switch for plotting an idealistic sample wave instead [default: False]")
  
    args = parser.parse_args()            

    main(args)
