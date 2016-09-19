"""
Filename:     plot_ocean_trend.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the spatial trends in the ocean

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
import matplotlib.pyplot as plt
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable

import iris
from iris.analysis.cartography import cosine_latitude_weights
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

long_titles = {'argo': 'full depth (0-2000m)',
               'surface': 'surface (0-50m)',
               'shallow': 'shallow (50-350m)',
               'middle': 'mid (350-700m)',
               'deep': 'deep (700-2000m)'}


def get_countour_levels(variable, plot_type, scale_factor=1.0):
    """Define levels for contour plot"""

    step_defaults = {('sea_water_potential_temperature', 'zonal_mean'): 2.5,
                     ('sea_water_temperature', 'zonal_mean'): 2.5,
                     ('sea_water_salinity', 'zonal_mean'): 0.25,
                     ('sea_water_density', 'zonal_mean'): 0.5,
                     ('sea_water_potential_temperature', 'vertical_mean'): 5.0,
                     ('sea_water_temperature', 'vertical_mean'): 5.0,
                     ('sea_water_salinity', 'vertical_mean'): 1.0,
                     ('sea_water_density', 'vertical_mean'): 0.5}

    step = step_defaults[(variable, plot_type)]
    step = step / float(scale_factor)    

    levels = numpy.arange(0.0, 350.0, step)

    return levels


def get_metadata(inargs, data_cube, climatology_cube):
    """Get the metadata dictionary."""
    
    metadata_dict = {}
    metadata_dict[inargs.infile] = data_cube.attributes['history']

    if climatology_cube:                  
        metadata_dict[inargs.climatology_file] = climatology_cube.attributes['history']

    return metadata_dict


def normalise_data(data):
    """Normalise the data."""

    abs_data = numpy.abs(data)

    min_val = abs_data.min()
    max_val = abs_data.max()

    abs_normalised_data = (abs_data - min_val) / (max_val - min_val)

    normalised_data = abs_normalised_data * numpy.sign(data)

    return normalised_data 


def plot_vertical_mean_trend(trends, lons, lats, gs, plotnum,
                             ticks, yticks,
                             title, units, palette,
                             climatology, contour_levels):
    """Plot the vertical mean trends.

    Produces a lon / lat plot.
 
    """

    ax = plt.subplot(gs[plotnum], projection=ccrs.PlateCarree(central_longitude=180.0))
    plt.sca(ax)

    cmap = eval('plt.cm.'+palette)
    cf = ax.contourf(lons, lats, trends, transform=ccrs.PlateCarree(),
                     cmap=cmap, extend='both', levels=ticks)
    if type(climatology) == iris.cube.Cube:
        cplot = ax.contour(lons, lats, climatology.data, transform=ccrs.PlateCarree(),
                           colors='0.2', levels=contour_levels)
        plt.clabel(cplot, contour_levels[0::2], fmt='%2.1f', colors='0.2', fontsize=8)

    ax.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.set_xlabel('Longitude', fontsize='small')
    ax.set_ylabel('Latitude', fontsize='small')    
    ax.set_title(long_titles[title])
    ax.coastlines()

    cbar = plt.colorbar(cf)
    cbar.set_label(units)


def plot_zonal_mean_trend(trends, lats, levs, gs, plotnum,
                          ticks, title, units, ylabel,
                          palette, cbar_ax,
                          climatology, contour_levels):
    """Plot the zonal mean trends.

    Produces a lat / depth plot.

    """

    axMain = plt.subplot(gs[plotnum])
    plt.sca(axMain)

    cmap = eval('plt.cm.'+palette)
    cf = axMain.contourf(lats, levs, trends,
                         cmap=cmap, extend='both', levels=ticks)
    if type(climatology) == iris.cube.Cube:
        cplot_main = axMain.contour(lats, levs, climatology.data, colors='0.2', levels=contour_levels)
        plt.clabel(cplot_main, contour_levels[0::2], fmt='%2.1f', colors='0.2', fontsize=8)

    # Deep section
    axMain.set_ylim((500.0, 2000.0))
    axMain.invert_yaxis()
    axMain.set_xlim((-70, 70))
    axMain.xaxis.set_ticks_position('bottom')
    axMain.set_xticks([-60, -40, -20, 0, 20, 40, 60])

    # Shallow section
    divider = make_axes_locatable(axMain)
    axShallow = divider.append_axes("top", size=2.2, pad=0.1, sharex=axMain)
    axShallow.contourf(lats, levs, trends,
                       cmap=cmap, extend='both', levels=ticks)
    if type(climatology) == iris.cube.Cube:
        cplot_shallow = axShallow.contour(lats, levs, climatology.data, colors='0.2', levels=contour_levels)
        plt.clabel(cplot_shallow, contour_levels[0::2], fmt='%2.1f', colors='0.2', fontsize=8)
    axShallow.set_ylim((0.0, 500.0))
    axShallow.invert_yaxis()
    axShallow.set_xlim((-70, 70))
    plt.setp(axShallow.get_xticklabels(), visible=False)

    # Labels
    plt.title(title)
    #plt.axhline(y=50, linestyle='dashed', color='0.5')
    #plt.axhline(y=350, linestyle='dashed', color='0.5')
 
    axMain.set_xlabel('Latitude', fontsize='small')
    plt.ylabel(ylabel, fontsize='small')
    #plt.axhline(y=700, linestyle='dashed', color='0.5')

    cbar = plt.colorbar(cf, cbar_ax)
    cbar.set_label(units)
    

def read_climatology(climatology_file, long_name):
    """Read the optional climatology data."""

    if climatology_file:
        with iris.FUTURE.context(cell_datetime_objects=True):
            climatology_cube = iris.load_cube(climatology_file, long_name)
        climatology = climatology_cube
    else:
        climatology = None

    return climatology


def set_ticks(tick_max, tick_step, tick_scale=1.0):
    """Set the colorbar ticks."""

    ticks = numpy.arange(-tick_max, tick_max + tick_step, tick_step)
    if (len(ticks) % 2 == 0): #even
        ticks = ticks[0:-1]
    ticks = ticks / tick_scale

    return ticks


def set_yticks(max_lat):
    """Set the ticks for the y-axis"""

    if max_lat > 60:
        yticks = [-80 ,-60, -40, -20, 0, 20, 40, 60, 80]
    else:
        yticks = [-60, -40, -20, 0, 20, 40, 60]

    return yticks


def get_trend_data(cube, already_trend=False, normalise=False):
    """Get the trend data.

    Args:
      cube (iris.cube.Cube): Data cube
      already_trend (bool): Indicate whether the data
        already represent a trend
      normalise (bool): Normalise the trend

    """

    if already_trend:
        trend = cube.data
        units = cube.units
    else:
        trend = timeseries.calc_trend(cube, running_mean=False,
                                      per_yr=True, remove_scaling=False)

        if not cube.units == 1:
            units = '$%s yr^{-1}$' %(cube.units)
        else:
            units = '$yr^{-1}$'

    if normalise:
        trend = normalise_data(trend)
        units = units+' (normalised)'

    return trend, units


def main(inargs):
    """Run the program."""

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    if inargs.plot_type == 'vertical_mean':
        plot_names = ['argo', 'surface', 'shallow', 'middle', 'deep']
        fig = plt.figure(figsize=[10, 25])
        gs = gridspec.GridSpec(5, 1)
    elif inargs.plot_type == 'zonal_mean':
        plot_names = ['globe', 'indian', 'pacific', 'atlantic']
        fig = plt.figure(figsize=[18, 12])
        fig.subplots_adjust(right=0.85)
        colorbar_axes = fig.add_axes([0.9, 0.2, 0.02, 0.6])
        gs = gridspec.GridSpec(2, 2)
 
    for plotnum, plot_name in enumerate(plot_names):
        standard_name = '%s_%s_%s' %(inargs.plot_type, plot_name, inargs.var)
        long_name = standard_name.replace('_', ' ')
        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(inargs.infile, long_name & time_constraint)  

        # Calculate seasonal cycle
        if inargs.seasonal_cycle:
            cube = timeseries.calc_seasonal_cycle(cube) 

        # Calculate trend
        trend, units = get_trend_data(cube, already_trend=inargs.trend)

        # Plot
        climatology = read_climatology(inargs.climatology_file, long_name)
        if inargs.plot_type == 'vertical_mean':
            lons = cube.coord('longitude').points
            lats = cube.coord('latitude').points
        
            tick_max, tick_step = inargs.vm_ticks
            ticks = set_ticks(tick_max, tick_step, tick_scale=inargs.vm_tick_scale[plotnum])
            contour_levels = get_countour_levels(inargs.var, inargs.plot_type,
                                                 scale_factor=inargs.vm_tick_scale[plotnum])

            yticks = set_yticks(inargs.max_lat)
            plot_vertical_mean_trend(trend, lons, lats, gs, plotnum,
                                     ticks, yticks,
                                     plot_name, units, inargs.palette,
                                     climatology, contour_levels)
        
        elif inargs.plot_type == 'zonal_mean':
            lats = cube.coord('latitude').points
            levs = cube.coord('depth').points            

            ylabel = 'Depth (%s)' %(cube.coord('depth').units)
            tick_max, tick_step = inargs.zm_ticks
            ticks = set_ticks(tick_max, tick_step)
            contour_levels = get_countour_levels(inargs.var, inargs.plot_type)

            plot_zonal_mean_trend(trend, lats, levs, gs, plotnum,
                                  ticks, plot_name, units, ylabel,
                                  inargs.palette, colorbar_axes,
                                  climatology, contour_levels)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')

    metadata_dict = get_metadata(inargs, cube, climatology) 
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Plot the spatial trends in the ocean'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input ocean maps file")
    parser.add_argument("var", type=str, help="Input variable name (the standard_name without the vertical_mean or zonal_mean bit)")
    parser.add_argument("plot_type", type=str, choices=('vertical_mean', 'zonal_mean'), help="Type of plot")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--trend", action="store_true", default=False,
                        help="Use this flag if data is already trend [default: False]")

    parser.add_argument("--climatology_file", type=str, default=None,
                        help="Plot climatology contours on zonal mean plot [default=None]")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--vm_ticks", type=float, nargs=2, default=(0.2, 0.04), metavar=('MAX_AMPLITUDE', 'STEP'),
                        help="Maximum tick amplitude and step size for vertical mean plot [default = 0.1, 0.02]")
    parser.add_argument("--vm_tick_scale", type=float, nargs=5, default=(1, 1, 1, 1, 1), metavar=('full', 'surface', 'shallow', 'mid', 'deep'),
                        help="Divide the ticks by this amount")

    parser.add_argument("--zm_ticks", type=float, nargs=2, default=(0.05, 0.01), metavar=('MAX_AMPLITUDE', 'STEP'),
                        help="Maximum tick amplitude and step size for vertical mean plot [default = 0.05, 0.01]")
    parser.add_argument("--max_lat", type=float, default=60,
                        help="Maximum latitude [default = 60]")

    parser.add_argument("--seasonal_cycle", action="store_true", default=False,
                        help="Switch for plotting the trend in the seasonal cycle instead [default: False]")

    parser.add_argument("--palette", type=str, choices=('RdBu_r', 'BrBG_r'), default='RdBu_r',
                        help="Color palette [default: RdBu_r]")

    args = parser.parse_args()            
    main(args)
