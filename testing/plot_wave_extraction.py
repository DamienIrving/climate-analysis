import os, sys

import numpy
import matplotlib.pyplot as plt

module_dir = os.path.join(os.environ['HOME'], 'phd', 'data_processing')
sys.path.insert(0, module_dir)
import calc_envelope


plot_type = sys.argv[1]



if plot_type == 'simple':
    x = numpy.linspace(0, 2 * numpy.pi, 200)
    N = len(x)
    
    simple_wave = numpy.sin(2*x)
    simple_env = calc_envelope.envelope(simple_wave, 1, 20)

    plt.plot(x, simple_wave)
    plt.plot(x, simple_env)

    plt.savefig('test_simple.png')

elif plot_type == 'complex':
    x = numpy.linspace(numpy.pi, 3 * numpy.pi, 200)
    N = len(x)
    k = 7
    
    complex_wave = numpy.cos((k - 1)*x) + numpy.cos(k * x) + numpy.cos((k + 1)*x)
    complex_env = calc_envelope.envelope(complex_wave, 1, 20)

    plt.plot(x, complex_wave)
    plt.plot(x, complex_env)

    plt.text(2, 0.65, r'$\cos(2 \pi t) \exp(-t)$')

    plt.savefig('test_complex.png')



