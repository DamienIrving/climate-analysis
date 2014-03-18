import os, sys
import argparse

import numpy
import matplotlib.pyplot as plt

import cdms2

module_dir = os.path.join(os.environ['HOME'], 'phd', 'data_processing')
sys.path.insert(0, module_dir)
import calc_envelope


def generate_plot(wave_data, function_text, x_data, envelopes, ofile):
    """Generate plot"""

    plt.plot(x_data, numpy.array(wave_data), linewidth=1.5, label=function_text)
    
    for wavenumbers in envelopes.keys():
        tag = str(wavenumbers[0])+'-'+str(wavenumbers[1])
        plt.plot(x_data, envelopes[wavenumbers], linestyle='--', linewidth=1.5, label=tag)
        
    plt.xlabel('x')
    plt.ylabel('y')
    #plt.axis((0, 2*numpy.pi, -1.1 , 1.1))
    plt.xlim(numpy.min(x_data), numpy.max(x_data))
    
    plt.legend(loc=4, ncol=2)
    plt.savefig(ofile)


def extract_envelopes(wave_data, bounds_list):
    """Extract the wave envelopes"""
    
    envelopes = {}
    for bounds in bounds_list:
        envelopes[bounds] = calc_envelope.envelope(wave_data, bounds[0], bounds[1])
 
    return envelopes
    

def get_wave(source, var, time_bounds, lat):
    """Return the wave data and function name, according to the specified source"""
    
    x = numpy.linspace(0, 2 * numpy.pi, 200)
    nsteps = len(x)
    amplitude = numpy.ones(nsteps)
    if source == 'simple':
	wave_data = numpy.sin(3*x)
        function_text = r'$y = \sin(3x)$'
	envelope_list = [(1, 20), (3, 3), (2, 4)]
		
    elif source == 'complex':
	k = 7
	wave_data = numpy.cos((k - 1)*x) + numpy.cos(k * x) + numpy.cos((k + 1)*x)
        function_text = r'$y = \cos(6x) + \cos(7x) + \cos(8x)$'
        envelope_list = [(1, 20), (7, 9), (6, 10), (8, 8)]

    elif source == 'zw3_smooth_variation':
	wave_data = numpy.abs(numpy.sin(0.5*x)) * numpy.cos(3*x)
        function_text = r'$y = \sin(0.5x) \cos(3x)$'
        envelope_list = [(1, 20), (2, 4), (2, 3), (1, 3), (3, 3)]

    elif source == 'zw3_breaks':
	wave_data = numpy.abs(numpy.sin(2*x)) * numpy.cos(3*x)
        function_text = r'$y = \sin(2x) \cos(3x)$'
        envelope_list = [(1, 20), (2, 4), (2, 7), (3, 3)]

    elif source == 'zw3_stops':
	ramp = numpy.arange(0, 1, 0.025)
	amplitude[80:120] = numpy.zeros(40)
	amplitude[40:80] = ramp[::-1]
	amplitude[120:160] = ramp
	
	wave_data = amplitude * numpy.cos(3*x)
        function_text = r'$y = \cos(3x), with ramp down$'
        envelope_list = [(1, 20), (2, 4), (1, 3), (2, 3), (3, 3)]

    elif source == 'zw3_random':
	wave_data = numpy.cos(3*x)
	wave_data[70:130] = numpy.random.uniform(-1, 1, size=60)
        function_text = r'$y = \cos(3x), with random$'
        envelope_list = [(1, 20), (2, 4), (2, 3), (1, 3), (1, 5), (3, 3)]

    else:
        fin = cdms2.open(source)
	wave_data = fin(var, time=time_bounds, latitude=lat, squeeze=1)
	assert len(wave_data.shape) == 1, \
	'Must select only one time step and latitude circle'
	x = wave_data.getLongitude()[:]
	function_text = 'v-wind'
	envelope_list = [(1, 20), (2, 4), (2, 3), (3, 4), (1, 5), (3, 3)]
	
    return wave_data, x, function_text, envelope_list
    

def main(inargs):
    """Run the program"""
    
    wave_data, x_data, function_text, envelope_list = get_wave(inargs.data_source, inargs.var, inargs.time_bounds, inargs.lat)
    
    envelopes = extract_envelopes(wave_data, envelope_list)

    generate_plot(wave_data, function_text, x_data, envelopes, inargs.ofile)


if __name__ == '__main__':
    
    description='Visualise the Zimin et al (2003) wave extraction method'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("data_source", type=str, 
                        help="""Can be "simple", "complex", ... , or the name of a data file""")
    
    parser.add_argument("--ofile", type=str, default='test.png',
                        help="Name of output file [default = test.png]")
    parser.add_argument("--var", type=str, default='va',
                        help="Name of the variable to read from the input file [default = va]")
    parser.add_argument("--time_bounds", nargs=2, type=str, default=('1996-04-01', '1996-04-30'),
                        help="Bounds for time step selection [default = 1996-04-01, 1996-04-30]")
    parser.add_argument("--lat", type=float, default=-55,
                        help="Latitude selection [default = -55]")			
     
    args = parser.parse_args()            

    main(args)
