import os, sys

import numpy
import matplotlib.pyplot as plt

module_dir = os.path.join(os.environ['HOME'], 'phd', 'data_processing')
sys.path.insert(0, module_dir)
import calc_envelope


plot_type = sys.argv[1]

font = {'family' : 'serif',
        'color'  : 'blue',
        'weight' : 'normal',
        'size'   : 18,
        }

if plot_type == 'simple':
    x = numpy.linspace(0, 2 * numpy.pi, 200)
    N = len(x)
    
    simple_wave = numpy.sin(3*x)
    simple_env = calc_envelope.envelope(simple_wave, 3, 3)

    plt.plot(x, simple_wave, linewidth=1.5)
    plt.plot(x, simple_env, linewidth=1.5)
    
    plt.xlabel('x')
    plt.ylabel('y')
    plt.axis((0, 2*numpy.pi, -1.1 , 1.1))
    
    font = {'family' : 'serif',
            'color'  : 'blue',
            'weight' : 'normal',
            'size'   : 18,
           }
    plt.text(3.0, 0.65, r'$y = \sin(3x)$', fontdict=font)
    
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



