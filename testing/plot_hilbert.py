"""
Filename:     calc_fourier_transform.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules

import sys, os
import argparse
import numpy
import matplotlib.pyplot as plt
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




#cenv.envelope(inwave, kmin, kmax)
#cenv.fourier_transform(inwave)
#cenv.hilbert_transform(inwave_hat, kmin, kmax)

#cft.inverse_fourier_transform(sig_fft, sample_freq, min_freq=, max_freq=, exclude=)
#cft.fourier_transform(signal, indep_var)


# Create data 

numpy.random.seed(1234)

time_step = 1.
period = 120.

time_vec = numpy.arange(0, 360, time_step)
simple_sig = numpy.cos(((2 * numpy.pi) / period) * time_vec) + 0.5 * numpy.random.randn(time_vec.size)
combined_sig = numpy.cos(((2 * numpy.pi) / 360.) * time_vec) + numpy.sin(((2 * numpy.pi) / 180.) * time_vec) + \
               numpy.sin(((2 * numpy.pi) / 120.) * time_vec) - numpy.cos(((2 * numpy.pi) / 90.) * time_vec) 
               #+ 0.5 * numpy.random.randn(time_vec.size)

sig = 3 * combined_sig

plt.plot(time_vec, sig)
plt.savefig('original_signal.png')
plt.clf()


# Use my current Hilbert transform method
my_result = cenv.envelope(sig, 2, 4)
plt.plot(time_vec, my_result)
plt.plot(time_vec, sig)
plt.savefig('my_hilbert_transform.png')
plt.clf()

# Use the scipy fft and ifft functions to try and re-create the Fourier transform
sig_fft, sample_freq, freqs, power = cft.fourier_transform(sig, time_vec)

filtered_signal_all_wavenum2 = cft.inverse_fourier_transform(sig_fft, sample_freq, min_freq=2, max_freq=2, exclude=None)
plt.plot(time_vec, 2*filtered_signal_all_wavenum2, color='blue', linestyle='--', label='w2')

filtered_signal_all_wavenum3 = cft.inverse_fourier_transform(sig_fft, sample_freq, min_freq=3, max_freq=3, exclude=None)
plt.plot(time_vec, 2*filtered_signal_all_wavenum3, color='blue', linestyle=':', label='w3')

filtered_signal_all_wavenum4 = cft.inverse_fourier_transform(sig_fft, sample_freq, min_freq=4, max_freq=4, exclude=None)
plt.plot(time_vec, 2*filtered_signal_all_wavenum4, color='blue', linestyle='-.', label='w4')

filtered_signal_all_wavenum24 = cft.inverse_fourier_transform(sig_fft, sample_freq, min_freq=2, max_freq=4, exclude=None)
plt.plot(time_vec, 2*filtered_signal_all_wavenum24, color='orange', label='w234')

sum_signals = filtered_signal_all_wavenum2 + filtered_signal_all_wavenum3 + filtered_signal_all_wavenum4
plt.plot(time_vec, 2*filtered_signal_all_wavenum24, color='blue', label='sum')

plt.legend()
plt.savefig('scipy_w234_results.png')
plt.clf()

