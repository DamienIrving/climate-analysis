"""
Filename:     plot_timescale_spectrum.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot some periodograms

"""

# Import general Python modules

import os, sys, pdb
import numpy, pandas
import argparse
import xray

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
    import general_io as gio
    import calc_fourier_transform as cft
    import calc_composite
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def running_mean(darray, window):
    """Calculate the running mean."""

    dframe = darray.to_pandas()
    dframe = pandas.rolling_mean(dframe, window, center=True)
    dframe = dframe.dropna()

    return xray.DataArray(dframe)


def read_data(inargs, runmean_window):
    """Read input data into an xray DataArray."""

    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.variable)

    subset_dict = gio.get_subset_kwargs(inargs)
    #subset_dict['method'] = 'nearest'
    darray = dset_in[inargs.variable].sel(**subset_dict).mean('latitude')
    indep_var = darray['longitude'].values

    if inargs.valid_lon:
        start_lon, end_lon = inargs.valid_lon
        lon_vals = numpy.array([start_lon, end_lon, darray['longitude'].values.min()])          
        assert numpy.sum(lon_vals >= 0) == 3, "Longitudes must be 0 to 360" 
        darray.loc[dict(longitude=slice(0, start_lon))] = 0
        darray.loc[dict(longitude=slice(end_lon, 360))] = 0

    darray = running_mean(darray, runmean_window)
    metadata_dict = {inargs.infile: dset_in.attrs['history']}

    return darray, indep_var, metadata_dict


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

    darray, indep_var, metadata_dict = read_data(inargs, runave)
    inargs.date_curve.append([None, 'all'])

    colors = ['#fbb4b9', '#f768a1', '#ae017e', 'red', 'blue', 'green']
    cindex = 0
    for date_file, leglabel in inargs.date_curve:        
        match_dates, date_metadata = calc_composite.get_datetimes(darray, date_file)
        data_filtered = darray.sel(time=match_dates)

        spectrum_temporal_mean, spectrum_freqs_1D = transform_data(data_filtered.values, indep_var, inargs.scaling)

        ax.plot(spectrum_freqs_1D, spectrum_temporal_mean, 
                label=leglabel, marker='o', color=colors[cindex], linewidth=2.0)

        if date_file:
            metadata_dict[date_file] = date_metadata
        
        cindex = cindex + 1

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
    
    colors = ['#ffffd9', '#edf8b1', '#c7e9b4', '#7fcdbb', '#41b6c4', 
              '#1d91c0', '#225ea8', '#253494', '#081d58'] 
 
    for index, step in enumerate(runmean_windows):
        darray, indep_var, metadata_dict = read_data(inargs, step)
        	
        spectrum_temporal_mean, spectrum_freqs_1D = transform_data(darray.values, indep_var, inargs.scaling)
        
        ax.plot(spectrum_freqs_1D, spectrum_temporal_mean, 
                label=str(step), marker='o', color=colors[index], linewidth=2.0)

    ax.set_xlim([1, inargs.window])
    ax.set_xlabel('wavenumber ($k$)')
    
    if inargs.scaling == 'R2':
        ylabel = 'variance explained ($R_k^2$)'
    else:
        ylabel = inargs.scaling
    ax.set_ylabel('average %s' %(ylabel))
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], fontsize='small')

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
    parser.add_argument("outfile", type=str, help="Output file name")

    # Additional curves for the left panel
    parser.add_argument("--date_curve", type=str, action='append', default=[], metavar=('DATE_FILE', 'LABEL'), nargs=2,
                        help="Date filtered curve for the left hand panel")
			
    # Input data options
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range over which to perform Fourier transform (data averaged over this range) [default = entire]")
    parser.add_argument("--valid_lon", type=float, nargs=2, metavar=('START', 'END'), default=None,
                        help="Longitude range over which to perform Fourier transform (all other values are set to zero) [default = entire]")
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
