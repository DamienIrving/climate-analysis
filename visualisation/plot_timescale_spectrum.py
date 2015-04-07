"""
Filename:     plot_timescale_spectrum.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot the density spectrum of a single data file for mutliple timescales

"""

# Import general Python modules

import os, sys, pdb
import numpy
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
anal_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(anal_dir)
try:
    import netcdf_io as nio
    import general_io as gio
    import calc_fourier_transform as cft
    import calc_composite
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions, global variables etc

colors = ['blue', 'cyan', 'green', 'yellow', 'orange', 'red', 'magenta', 'purple', 'brown', 'black']    


def transform_data(signal, indep_var, scaling):
    """Do the Fourier Transform."""

    sig_fft, sample_freq = cft.fourier_transform(signal, indep_var)
    spectrum, spectrum_freqs = cft.spectrum(sig_fft, sample_freq, 
                                            scaling=scaling, 
                                            variance=numpy.var(signal))
	
    spectrum_temporal_mean = numpy.mean(spectrum, axis=0)
    spectrum_freqs_1D = numpy.mean(spectrum_freqs, axis=0)

    return spectrum_temporal_mean, spectrum_freqs_1D


def composite_plot(plt, inargs, runave=30):
    """Plot periodogram that compares composites."""

    assert inargs.date_files

    indata = nio.InputData(inargs.infile, inargs.variable, runave=runave,
                           **nio.dict_filter(vars(inargs), ['latitude', 'time']))

    indep_var = indata.data.getLongitude()[:]
    metadata_dict = {inargs.infile: indata.global_atts['history']}

    composite_dict = {'PWI > 90pct': inargs.date_files[0],
                      'PWI < 10pct': inargs.date_files[1],
                      'all timesteps': None}

    for label, date_file in composite_dict.iteritems():        
        data_filtered, date_metadata, size_filtered = calc_composite.filter_dates(indata.data, date_file)
        spectrum_temporal_mean, spectrum_freqs_1D = transform_data(data_filtered, indep_var, inargs.scaling)

        plt.plot(spectrum_freqs_1D, spectrum_temporal_mean, label=label, marker='o')

        if date_file:
            metadata_dict[date_file] = date_metadata

    plt.xlim(1, inargs.window)
    plt.xlabel('wavenumber ($k$)')
    
    if inargs.scaling == 'R2':
        ylabel = 'variance explained ($R_k^2$)'
    else:
        ylabel = inargs.scaling
    plt.ylabel('average %s' %(ylabel))
    plt.legend()

    return metadata_dict


def timescale_plot(plt, inargs):
    """Plot periodogram that compares various timescales."""

    if inargs.runmean:
        runmean_windows = inargs.runmean
    else:
        runmean_windows = [1]
    
    for index, step in enumerate(runmean_windows):
        
        indata = nio.InputData(inargs.infile, inargs.variable, runave=step,
                               **nio.dict_filter(vars(inargs), ['latitude', 'time']))
	
        signal = indata.data
        indep_var = signal.getLongitude()[:]

        spectrum_temporal_mean, spectrum_freqs_1D = transform_data(signal, indep_var, inargs.scaling)
        
        plt.plot(spectrum_freqs_1D, spectrum_temporal_mean, 
                 label=str(step), marker='o', color=colors[index])

    plt.xlim(1, inargs.window)
    plt.xlabel('wavenumber ($k$)')
    
    if inargs.scaling == 'R2':
        ylabel = 'variance explained ($R_k^2$)'
    else:
        ylabel = inargs.scaling
    plt.ylabel('average %s' %(ylabel))
    plt.legend()

    metadata_dict = {inargs.infile: indata.global_atts['history']}

    return metadata_dict


def main(inargs):
    """Run the program."""
    
    plt.figure()

    assert inargs.plot_type in ('timescale', 'composite')
    if inargs.plot_type == 'timescale':
        metadata_dict = timescale_plot(plt, inargs)
    elif inargs.plot_type == 'composite':
        metadata_dict = composite_plot(plt, inargs)

    plt.savefig(inargs.outfile, bbox_inches='tight')
    plt.clf()
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)
    

if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/anaconda/bin/python plot_timescale_spectrum.py 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/va_Merra_250hPa_daily_r360x181.nc va 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/figures/tscale_anal/amp-spectra-va_Merra_250hPa_daily-2000-2009_r360x181-55S.png 
  --runmean 1 5 10 15 30 60 90 180 365 
  --latitude -55

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Plot the density spectrum of a single data file for mutliple timescales'
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
    argparser.add_argument("--date_files", type=str, nargs=2, metavar=('UPPER', 'LOWER'), default=None, 
                           help="File containing dates for the upper and lower composite")

    # Plot type
    argparser.add_argument("--plot_type", type=str, choices=('timescale', 'composite'), default='timescale',
                           help="type of plot to generate [default=timescale]")

    # Output options
    argparser.add_argument("--window", type=int, default=10,
                           help="upper limit on the frequencies included in the plot [default=10]")
    argparser.add_argument("--runmean", type=int, nargs='*',
                           help="running mean windows to include (e.g. 1 5 30 90 180)")
    argparser.add_argument("--scaling", type=str, choices=('amplitude', 'power', 'R2'), default='amplitude',
                           help="scaling applied to the amplitude of the spectal density [default=None]")
  

    args = argparser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
