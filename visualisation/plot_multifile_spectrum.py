"""
Filename:     plot_multifile_spectrum.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot the density spectrum for multiple data files

"""

# Import general Python modules

import os, sys, pdb
import numpy
import argparse
import matplotlib.pyplot as plt
import math

# Import my modules

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
try:
    import netcdf_io as nio
    import general_io as gio
    import calc_fourier_transform as cft
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')
  

def main(inargs):
    """Run the program."""
    
    plt.figure()     
    for index, input_info in enumerate(inargs.infiles):
        infile, var = input_info
        indata = nio.InputData(infile, var, **nio.dict_filter(vars(inargs), ['time']))
        
        signal = indata.data
        indep_var = signal.getTime()[:]

        sig_fft, sample_freq = cft.fourier_transform(signal, indep_var)
        spectrum, spectrum_freqs = cft.spectrum(sig_fft, scaling=inargs.scaling, variance=numpy.var(signal))

        plt.plot(spectrum_freqs, spectrum, label='FIXME', marker='o') 

    #plt.yscale('log')
    #plt.xlim(0, 500)
    plt.xlabel('frequency [cycles / domain]')
    plt.ylabel('%s' %(inargs.scaling))
    plt.legend()
    
    plt.savefig(inargs.outfile, bbox_inches='tight')
    plt.clf()
    metadata = {indata.fname: indata.global_atts['history']}
    gio.write_metadata(inargs.outfile, file_info=metadata)
    

if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/anaconda/bin/python plot_multifile_spectrum.py 

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot the density spectrum of a single data file for mutliple timescales'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
			
    # Input data options
    parser.add_argument("--infiles", type=str, action='append', metavar=('FILENAME', 'VAR'), default=[], nargs=2,
                        help="additional input file name and variable")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    # Output options
    parser.add_argument("--scaling", type=str, choices=('amplitude', 'power', 'R2'), default='amplitude',
                        help="scaling applied to the amplitude of the spectal density [default=None]")
  
    args = parser.parse_args()            
    args.infiles.insert(0, [args.infile, args.variable])
    
    main(args)
