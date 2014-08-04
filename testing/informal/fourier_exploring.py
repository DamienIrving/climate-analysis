# Define functions used in prior testing # 

def simple_signal():
    """Define a sample signal"""
    
    numpy.random.seed(1234)

    time_step = 1.
    period = 120.

    time_vec = numpy.arange(0, 360, time_step)
#    signal = numpy.cos(((2 * numpy.pi) / period) * time_vec) \ 
#             + 0.5 * numpy.random.randn(time_vec.size)
#    signal = numpy.cos(((2 * numpy.pi) / 360.) * time_vec) \ 
#             + numpy.sin(((2 * numpy.pi) / 180.) * time_vec) \
#             + numpy.sin(((2 * numpy.pi) / 120.) * time_vec) \ 
#             - numpy.cos(((2 * numpy.pi) / 90.) * time_vec) \ 
#             + 0.5 * numpy.random.randn(time_vec.size)
    signal = numpy.cos(((2 * numpy.pi) / (360. / 6.)) * time_vec) \
             + numpy.cos(((2 * numpy.pi) / (360. / 7.)) * time_vec) \
             + numpy.cos(((2 * numpy.pi) / (360. / 8.)) * time_vec)

    signal = 3 * signal
    
    return time_vec, signal



def plot_wavenumbers(num_list, filtered_signal, xaxis, tag=None):
    """Plot the individual wavenumbers, including their 
    positive and negative wavenumber parts"""
    
    colors = ['blue', 'red', 'green', 
              'orange', 'pink', 'black', 
	      'purple', 'brown', 'cyan', 'magenta']
    for wavenum in num_list:
        plt.plot(xaxis, 2*filtered_signal[None, wavenum, wavenum], 
	         color=colors[wavenum-1], label='w'+str(wavenum))
        plt.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], 
	         color=colors[wavenum-1], linestyle=':')
        plt.plot(xaxis, 2*filtered_signal['negative', wavenum, wavenum], 
	         color=colors[wavenum-1], linestyle='--')

    plt.legend()
    outfile = 'individual_wavenumbers_'+tag+'.png' if tag \
              else 'individual_wavenumbers.png'
    plt.savefig(outfile)
    plt.clf()
