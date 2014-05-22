import numpy
from matplotlib import pyplot as plt
from scipy import fftpack

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


def inverse_fourier_transform(sig_fft, sample_freq, max_freq=None, min_freq=None):
    """Inverse Fourier Transform.
    
    Input arguments:
        max_freq, min_freq   ->  Can filter to only include a certain
                                 frequency range.
                                 (e.g. for wavenumber 4, freq is 0.25)
    """
    
    if max_freq == min_freq and max_freq:
        sig_fft[numpy.abs(sample_freq) != max_freq] = 0
        print 'Frequencies equal'
    
    if max_freq:
        sig_fft[numpy.abs(sample_freq) > max_freq] = 0
        print 'Setting max freq...'
    
    if min_freq:
        sig_fft[numpy.abs(sample_freq) < min_freq] = 0
        print 'Setting min freq...'
    
    return fftpack.ifft(sig_fft)
    
