"""
Filename:     plot_timescale_spectrum.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot some periodograms

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


def composite_plot(ax, inargs, runave=30, label=None):
    """Plot periodogram that compares composites."""

    # Get input data
    indata = nio.InputData(inargs.infile, inargs.variable, runave=runave,
                           **nio.dict_filter(vars(inargs), ['latitude', 'time']))

    indep_var = indata.data.getLongitude()[:]
    metadata_dict = {inargs.infile: indata.global_atts['history']}

    composite_dict = {'PWI > 90 pctl': inargs.upper_date_file,
                      'PWI < 10 pctl': inargs.lower_date_file,
                      'all timesteps': None}

    # Create the plot
    for leglabel, date_file in composite_dict.iteritems():        
        data_filtered, date_metadata, size_filtered = calc_composite.filter_dates(indata.data, date_file)
        spectrum_temporal_mean, spectrum_freqs_1D = transform_data(data_filtered, indep_var, inargs.scaling)

        ax.plot(spectrum_freqs_1D, spectrum_temporal_mean, label=leglabel, marker='o')

        if date_file:
            metadata_dict[date_file] = date_metadata

    ax.set_xlim([1, inargs.window])
    ax.set_xlabel('wavenumber ($k$)')
    
    if inargs.scaling == 'R2':
        ylabel = 'variance explained ($R_k^2$)'
    else:
        ylabel = inargs.scaling
    ax.set_ylabel('average %s' %(ylabel))
    ax.legend(fontsize='small')

    if label:
        ax.text(0.03, 0.95, label, transform=ax.transAxes, fontsize='large')

    return metadata_dict


def timescale_plot(ax, inargs, label=None):
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
        
        ax.plot(spectrum_freqs_1D, spectrum_temporal_mean, 
                label=str(step), marker='o', color=colors[index])

    ax.set_xlim([1, inargs.window])
    ax.set_xlabel('wavenumber ($k$)')
    
    if inargs.scaling == 'R2':
        ylabel = 'variance explained ($R_k^2$)'
    else:
        ylabel = inargs.scaling
    ax.set_ylabel('average %s' %(ylabel))
    ax.legend(fontsize='small')

    if label:
        ax.text(0.03, 0.95, label, transform=ax.transAxes, fontsize='large')


def main(inargs):
    """Run the program."""
    
    # Initialise plot
    fig = plt.figure(figsize=inargs.figure_size)
    if not inargs.figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    ax1 = plt.subplot(1, 2, 1)
    ax2 = plt.subplot(1, 2, 2)

    # Generate the plots
    metadata_dict = composite_plot(ax1, inargs, label='(a)')
    timescale_plot(ax2, inargs, label='(b)')
    
    plt.savefig(inargs.outfile, bbox_inches='tight')
    plt.clf()

    # Metadata
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)
    

if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
  python plot_timescale_spectrum.py va_data.nc va
  dates_upper.txt dates_lower.txt output.png 
  --latitude -55 --scaling R2 
  --runmean 1 5 30 60 90 180 365 
  --figure_size 14.0 6.0

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
    parser.add_argument("upper_date_file", type=str, help="File containing dates for the upper composite (e.g. > 90th percentile)")
    parser.add_argument("lower_date_file", type=str, help="File containing dates for the lower composite (e.g. < 10th percentile)")
    parser.add_argument("outfile", type=str, help="Output file name")
			
    # Input data options
    parser.add_argument("--latitude", type=float,
                        help="Latitude over which to perform the Fourier Transform [default = entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    # Analysis options
    parser.add_argument("--window", type=int, default=8,
                        help="upper limit on the frequencies included in the plot [default=8]")
    parser.add_argument("--runmean", type=int, nargs='*', default=None,
                        help="running mean windows to include (e.g. 1 5 30 60 90 180 365)")
    parser.add_argument("--scaling", type=str, choices=('amplitude', 'power', 'R2'), default='R2',
                        help="scaling applied to the amplitude of the spectal density [default=None]")

    # Plot options
    parser.add_argument("--figure_size", type=float, default=(14.0, 6.0), nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
  
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
