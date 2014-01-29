import os, sys

import numpy
import matplotlib.pyplot as plt

module_dir = os.path.join(os.environ['HOME'], 'phd', 'data_processing')
sys.path.insert(0, module_dir)
import calc_envelope


def generate_plot(wave_data, function):
    """Generate plot"""

    font = {'family' : 'serif',
            'color'  : 'blue',
            'weight' : 'normal',
            'size'   : 18,
            }

    plt.plot(x, wave_data, linewidth=1.5)
    plt.plot(x, wave_data, linewidth=1.5)
    
    plt.xlabel('x')
    plt.ylabel('y')
    #plt.axis((0, 2*numpy.pi, -1.1 , 1.1))
    
#    plt.text(3.0, 0.65, r'$y = \sin(3x)$', fontdict=font)
    
    plt.savefig('test_simple.png')


elif plot_type == 'complex':
    x = numpy.linspace(numpy.pi, 3 * numpy.pi, 200)
    N = len(x)
    k = 7
    
    complex_wave = numpy.cos((k - 1)*x) + numpy.cos(k * x) + numpy.cos((k + 1)*x)
    complex_env = calc_envelope.envelope(complex_wave, 1, 20)

    plt.plot(x, complex_wave, linewidth=1.5)
    plt.plot(x, complex_env, linewidth=1.5)

    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis((numpy.pi, 3*numpy.pi, -3.1 , 3.1))

    font = {'family' : 'serif',
            'color'  : 'blue',
            'weight' : 'normal',
            'size'   : 13,
           }
    plt.text(6.9, -2.8, r'$y = \cos(6x) + \cos(7x) + \cos(8x)$', fontdict=font)

    plt.savefig('test_complex.png')


def extract_envelopes(wave_data, selected_range, total_range):
    """Extract the wave envelopes"""
    
    envelopes = {}
    
    envelopes[selected_range] = calc_envelope.envelope(wave_data, 
                                                       selected_range[0], 
						       selected_range[1])
    envelopes[total_range] = calc_envelope.envelope(wave_data, 
                                                    total_range[0], 
						    total_range[1])
    
    for i in range(total_range[0], total_range[1] + 1):
        envelopes[i] = calc_envelope.envelope(wave_data, i, i)


    return envelopes
    

def get_wave(source):
    """Return the wave data, according to the specified source"""
    
    x = numpy.linspace(0, 2 * numpy.pi, 200)
    if source == 'simple':
        wave_data = numpy.sin(3*x)
        function = r'$y = \sin(3x)$'
		
    elif source == 'complex':
        k = 7
	wave_data = numpy.cos((k - 1)*x) + numpy.cos(k * x) + numpy.cos((k + 1)*x)
        function = r'$y = \cos(6x) + \cos(7x) + \cos(8x)$'

    else:
        #READ IN REAL DATA FOR SPECIFIED LAT AND TIMESTEP
	
    return wave_data, function
    

def main(inargs):
    """Run the program"""
    
    wave_data, function = get_wave(inargs.data_source)
    
    envelopes = extract_envelopes(wave_data)

    generate_plot(wave_data, envelopes)


if __name__ == '__main__':
    
    description='Visualise the Zimin et al (2003) wave extraction method'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_source", type=str, 
                        help="""Can be "simple", "complex" or the name of a data file""")
    parser.add_argument("--wavenumbers", type=int, nargs='*', 
                        help="Wavenumbers to be retained in the envelope calculation")
    parser.add_argument("--ofile", type=str, default='test.png',
                        help="Name of output file [default = test.png")	
    
    args = parser.parse_args()            

    main(args)
