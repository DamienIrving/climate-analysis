"""
Filename:     plot_hilbert.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot the components of a Hilbert transform

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
import xray

import seaborn
seaborn.set_context('paper')


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
except ImportError:
    raise ImportError('Must run this script from within the climate-analysis git repo')


# Define functions

def get_hemisphere(lat):
    """For a given latitude, return N or S."""

    if lat < 0.0:
        return 'S'
    else:
        return 'N' 


def extract_data(dset, var, lat_range, valid_lon, dates):
    """Extract data for the given latitude and dates.""" 

    start_lat, end_lat = lat_range
    data_dict = {}
    for date in dates:
        if start_lat == end_lat:
            darray = dset[var].sel(time=date, latitude=start_lat, method='nearest')
        else:
            darray = dset[var].sel(time=date, latitude=slice(start_lat, end_lat)).mean('latitude')
        if valid_lon:
            start_lon, end_lon = valid_lon
            lon_vals = numpy.array([start_lon, end_lon, darray['longitude'].values.min()])          
            assert numpy.sum(lon_vals >= 0) == 3, "Longitudes must be 0 to 360" 

            darray.loc[dict(longitude=slice(0, start_lon,))] = 0
            darray.loc[dict(longitude=slice(end_lon, 360))] = 0
        data_dict[date] = darray
    
    if start_lat == end_lat:
        lat_target = darray['latitude'].values.tolist()
        lat_tag = '%s%s' %(str(abs(lat_target)), get_hemisphere(lat_target))
    else:
        lat_tag = '%s%s to %s%s' %(str(abs(start_lat)), get_hemisphere(start_lat),
                                   str(abs(end_lat)), get_hemisphere(end_lat))

    return data_dict, lat_tag
 

def plot_periodogram(plot_axis, data_dict, wmin, wmax):
    """Add a small periodgram to the plot."""

    fig = plt.gcf()
    x = 0.195
    y = 0.70
    width = 0.16
    height = 0.18
    subax = fig.add_axes([x, y, width, height])
    xvals = numpy.arange(wmin, wmax + 1)
    yvals = []
    for w in xvals:
        yvals.append(data_dict['positive', w, w].max()) 

    subax.plot(xvals, numpy.array(yvals), marker='o', color='black')
    
    subax.set_ylabel('amplitude ($ms^{-1}$)', fontsize='xx-small')
    subax.set_xlabel('wavenumber', fontsize='xx-small')
    subax.tick_params(axis='x', labelsize='xx-small')
    subax.tick_params(axis='y', labelsize='xx-small')


def plot_hilbert(data_dict, date_list,
                 wmin, wmax,
                 nrows, ncols,
                 lat_tag,
                 outfile='test.png',
                 highlights=[],
                 env_list=[],
                 legend_list=[],
                 ybounds=None,
                 figure_size=None,
                 periodogram=False,
                 no_title=False,
                 axis_size='small', legend_size='small', title_size='large'):
    """Create the plot."""

    fig = plt.figure(figsize=figure_size)
    if not figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    if env_list:
        env_flat = numpy.array(env_list).flatten()
        wlower = numpy.min([env_flat.min(), wmin])
        wupper = numpy.max([env_flat.max(), wmax])
    else:
        wlower = wmin
        wupper = wmax

    for index in range(0, len(date_list)):
        plotnum = index + 1
        date = date_list[index]
        darray = data_dict[date]
        xaxis = darray['longitude'].values
        data = darray.values.squeeze()

        ax = plt.subplot(nrows, ncols, plotnum)
        plt.sca(ax)

        # Fourier transform
        sig_fft, sample_freq = cft.fourier_transform(data, xaxis)

        # Calculate individual Fourier components
        filtered_signal = {}
        for filt in [None, 'positive', 'negative']:
            for wave_min in range(wlower, wupper + 1):
                for wave_max in range(wlower, wupper + 1):
                    filtered_signal[filt, wave_min, wave_max] = cft.inverse_fourier_transform(sig_fft, sample_freq, 
                                                                                              min_freq=wave_min, 
                                                                                              max_freq=wave_max, 
                                                                                              exclude=filt)

        #ax.axhline(y=0.0, linestyle='-', color='0.8')

        # Plot individual wavenumber components
        for wavenum in range(wmin, wmax):
            color = '#1b9e77' if wavenum in highlights else '0.5' 
            ax.plot(xaxis, 2*filtered_signal['positive', wavenum, wavenum], color=color, linestyle='--')
        ax.plot(xaxis, 2*filtered_signal['positive', wmax, wmax], color='0.5', linestyle='--', label='Fourier components')

        # Plot reconstructed signal and envelope
        env_colors = ['#d95f02', 'blue', 'orange', 'cyan']
        count = 0
        for emin, emax in env_list:
            tag = 'wave envelope (wavenumbers %i-%i)'  %(emin, emax)
            ax.plot(xaxis, numpy.abs(2*filtered_signal['positive', emin, emax]), color=env_colors[count], label=tag, linewidth=2.0)

            tag = 'reconstructed signal (wavenumbers %i-%i)'  %(emin, emax)
            ax.plot(xaxis, 2*filtered_signal['positive', emin, emax], color=env_colors[count], linestyle='--', label=tag, linewidth=2.0)
            count = count + 1

        # Plot original signal
        tag = 'mean meridional wind, %s'  %(lat_tag)
        ax.plot(xaxis, data, color='#7570b3', label=tag, linewidth=2.0)

        # Plot details
        ax.set_xlim(0, 360)
        if ybounds:
            ax.set_ylim(ybounds) 

        if not no_title:
            ax.set_title(date, fontsize=title_size)
        
        ax.set_ylabel('$m s^{-1}$', fontsize=axis_size)
        ax.set_xlabel('longitude', fontsize=axis_size)
        ax.tick_params(axis='x', labelsize=axis_size)
        ax.tick_params(axis='y', labelsize=axis_size)

        if index in legend_list:
            handles, labels = ax.get_legend_handles_labels()
            ax.legend(handles[::-1], labels[::-1], loc=4, fontsize=legend_size)
        
        # Make a little subplot
        if periodogram:
            plot_periodogram(ax, filtered_signal, wmin, wmax)
        
    fig.savefig(outfile, bbox_inches='tight')


def main(inargs):
    """Plot each timestep."""

    # Extract data
    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.variable)

    data_dict, lat_tag = extract_data(dset_in, inargs.variable, 
                                      inargs.latitude, inargs.valid_lon, 
                                      inargs.dates)    

    # Create the plot
    if not inargs.legend_list:
        legend_list = []
    else:
        legend_list = inargs.legend_list

    wmin, wmax = inargs.wavenumbers
    plot_hilbert(data_dict, inargs.dates,
                 wmin, wmax,
                 inargs.nrows, inargs.ncols,
                 lat_tag,
                 outfile=inargs.ofile,
                 ybounds=inargs.ybounds,
                 figure_size=inargs.figure_size,
                 highlights=inargs.highlights,
                 env_list=inargs.envelope,
                 legend_list=legend_list,
                 periodogram=inargs.periodogram,
                 no_title=inargs.no_title,
                 axis_size=inargs.axis_label_size,
                 legend_size=inargs.legend_label_size,
                 title_size=inargs.title_size,)

    gio.write_metadata(inargs.ofile, file_info={inargs.infile: dset_in.attrs['history']})


if __name__ == '__main__':

    description = 'Plot the components of a Hilbert transform.'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("ofile", type=str, help="name of output file")
    parser.add_argument("nrows", type=int, help="number of rows in the entire grid of plots")
    parser.add_argument("ncols", type=int, help="number of columns in the entire grid of plots")

    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START_LAT', 'END_LAT'), default=(0.0, 0.0),
                        help="Latitude range over which average data before extracting and plotting the waves (for single lat, make start=end) [default = 0]")
    parser.add_argument("--valid_lon", type=float, nargs=2, metavar=('START', 'END'), default=None,
                        help="Longitude range over which to perform Fourier Transform (all other values are set to zero) [default = entire]")
    parser.add_argument("--dates", type=str, nargs='*',
                        help="Dates to plot")
    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[1, 9],
                        help="Wavenumbers to include on the plot")    
    parser.add_argument("--highlights", type=int, nargs='*', default=[],
                        help="Wavenumers to highlight")
    parser.add_argument("--envelope", type=int, action='append', nargs=2, metavar=('WAVE_MIN', 'WAVE_MAX'), default=[],
                        help="Envelope to plot")

    parser.add_argument("--legend_list", type=int, nargs='*', default=None,
                        help="Figures to include a legend on (start counting from 0) [default = none]")
    parser.add_argument("--periodogram", action="store_true", default=False,
                        help="Plot a periodogram in the corner")
    parser.add_argument("--no_title", action="store_true", default=False,
                        help="Do not plot title")

    sizes = ('xx-small', 'x-small', 'small', 'medium', 'large')
    parser.add_argument("--axis_label_size", type=str, default='small', choices=sizes,
                        help="Size for the axis markers and labels [default = small]")
    parser.add_argument("--legend_label_size", type=str, default='small', choices=sizes,
                        help="Size for the legend labels [default = small]")
    parser.add_argument("--title_size", type=str, default='large', choices=sizes,
                        help="Size for the plot titles [default = large]")

    parser.add_argument("--ybounds", type=float, nargs=2, metavar=('LOWER', 'UPPER'), default=None,
                        help="y-axis bounds (there are defaults set for each timescale)")
    parser.add_argument("--figure_size", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")

    args = parser.parse_args()            

    main(args)
