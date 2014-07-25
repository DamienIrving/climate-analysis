"""
Filename:     plot_freq_spectra.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules

import matplotlib.pyplot as plt
import os, sys
import numpy
import argparse

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
    for step in [1, 5, 10, 30, 90, 180]:
        indata = nio.InputData(inargs.infile, inargs.variable, runave=step,
                               **nio.dict_filter(vars(inargs), ['time', 'latitude']))
    
        signal = indata.data
        indep_var = signal.getLongitude()[:]

        sig_fft, sample_freq = cft.fourier_transform(signal, indep_var)
        amp_spectrum = cft.spectrum(sig_fft, output='amplitude')
	
	if 'y' in indata.data.getOrder():
            amp_spectrum_lat_mean = numpy.mean(amp_spectrum, axis=1)
	    x = sample_freq[0, 0, 1:inargs.window+1]
        else:
	    amp_spectrum_lat_mean = amp_spectrum
	    x = sample_freq[0, 1:inargs.window+1]
	amp_spectrum_temp_lat_mean = numpy.mean(amp_spectrum_lat_mean, axis=0)
    
	amp_mean = numpy.mean(amp_spectrum_temp_lat_mean[1:inargs.window+1])
	amp_std = numpy.std(amp_spectrum_temp_lat_mean[1:inargs.window+1])
	y = (amp_spectrum_temp_lat_mean[1:inargs.window+1] - amp_mean) / amp_std
    
        plt.plot(x, y, label=str(step), marker='o')  # Because I think a freq of 0 makes no sense

    plt.xlabel('Frequency [cycles / domain]')
    plt.ylabel('normalised amplitude')
    plt.legend()
    
    plt.savefig(inargs.outfile)
    plt.clf()
    metadata = [[indata.fname, indata.id, indata.global_atts['history']],]
    gio.write_metadata(inargs.outfile, file_info=metadata)
    

if __name__ == '__main__':

    extra_info =""" 
example (irvingnix.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.5.1/bin/cdat plot_freq_spectra.py 
  /home/dbirving/Downloads/Data/va_Merra_250hPa_30day-runmean-2002_r360x181.nc 
  va test.png --latitude -70 -40

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot the average amplitude spectrum'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
			
    # Input data options
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range over which to perform the Fourier Transform [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    # Output options
    parser.add_argument("--window", type=int, default=10,
                        help="upper limit on the frequencies included in the plot")

  
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
