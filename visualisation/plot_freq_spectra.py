"""
Filename:     plot_freq_spectra.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules

import os, sys, pdb
import math, numpy
import argparse
import matplotlib.pyplot as plt
from dateutil import parser
import cdms2

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


colors = ['blue', 'cyan', 'green', 'yellow', 'orange', 'red', 'magenta', 'purple', 'brown', 'black']    

def set_title(lat, time_bounds):
    """Set the title for the plot""" 

    title = 'Ave spectra, %s to %s, lat: %s' %(str(time_bounds[0]), str(time_bounds[1]), str(lat)) 

    return title


def common_date_format(date_list):
    """Convert a list of dates to the %Y-%m-%d format"""

    date_list = map(str, date_list)
    date_list = map(parser.parse, date_list)
    date_list = map(lambda x: x.strftime("%Y-%m-%d"), date_list)

    return date_list


def adjust_time_bounds(infile, time_bounds, window):
    """Adjust the time bounds so that there is enough data
    in the selection to calculate the running mean"""

    fin = cdms2.open(infile)
    time_axis = fin.getAxis('time').asComponentTime()  #will fail if the name of the time axis isn't time
    fin.close()

    time_axis_common = common_date_format(time_axis)
    time_bounds_common = common_date_format(time_bounds)
    old_start, old_end = time_bounds_common

    old_start_index = 0
    for date in time_axis_common:
        if old_start in date:
            break
        old_start_index = old_start_index + 1
    assert old_start_index != len(time_axis), "Original start index (relative to the time axis) not found"    

    old_end_index = -1
    for date in time_axis_common[::-1]:
        if old_end in date:
            break
        old_end_index = old_end_index - 1
    assert old_end_index != -1 - len(time_axis), "Original end index (relative to the time axis) not found" 

    new_start_index = int(old_start_index - math.ceil((window - 1) / 2.))  # genutil leaves more off the front in uneven circumstances
    new_end_index = int(old_end_index + math.floor((window - 1) / 2.))

    return [str(time_axis[new_start_index]), str(time_axis[new_end_index])]



def main(inargs):
    """Run the program."""
    
    title = set_title(inargs.latitude, inargs.time)
    plt.figure() 
    if inargs.runmean:
        runmean_windows = inargs.runmean
    else:
        runmean_windows = [1]
    
    for index, step in enumerate(runmean_windows):
        if inargs.time:
            inargs.time = adjust_time_bounds(inargs.infile, inargs.time, step)
        
        indata = nio.InputData(inargs.infile, inargs.variable, runave=step,
                               **nio.dict_filter(vars(inargs), ['latitude', 'time']))
    
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
    
        plt.plot(x, y, label=str(step), marker='o', color=colors[index])  # Because I think a freq of 0 makes no sense

    plt.xlabel('Frequency [cycles / domain]')
    plt.ylabel('normalised amplitude')
    plt.legend()
    plt.title(title)
    
    plt.savefig(inargs.outfile)
    plt.clf()
    metadata = {indata.fname: indata.global_atts['history']}
    gio.write_metadata(inargs.outfile, file_info=metadata)
    

if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.3.0/bin/cdat plot_freq_spectra.py 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_daily_r360x181.nc va 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/figures/tscale_anal/amp-spectra-va_Merra_250hPa_daily-2000-2009_r360x181-55S.png 
  --time 1990-01-01 2009-12-31 
  --runmean 1 5 10 15 30 60 90 180 365 
  --latitude -55

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot the average amplitude spectrum'
    argparser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    argparser.add_argument("infile", type=str, help="Input file name")
    argparser.add_argument("variable", type=str, help="Input file variable")
    argparser.add_argument("outfile", type=str, help="Output file name")
			
    # Input data options
    argparser.add_argument("--latitude", type=float,
                           help="Latitude over which to perform the Fourier Transform [default = entire]")
    argparser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                           help="Time period [default = entire]")

    # Output options
    argparser.add_argument("--window", type=int, default=10,
                           help="upper limit on the frequencies included in the plot")
    argparser.add_argument("--runmean", type=int, nargs='*',
                           help="running mean windows to include (e.g. 1 5 30 90 180)")
  
    args = argparser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
