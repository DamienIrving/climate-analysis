"""
Filename:     plot_temperature_trend.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the spatial trends in ocean temperature

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
import matplotlib.pyplot as plt
from matplotlib import gridspec

import iris
import cf_units
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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def calc_seasonal_cycle(cube):
    """Calculate the seasonal cycle.

    cycle = (max - min) for each 12 month window 

    """

    max_cube = cube.rolling_window('time', iris.analysis.MAX, 12)
    min_cube = cube.rolling_window('time', iris.analysis.MIN, 12)

    seasonal_cycle_cube = max_cube - min_cube

    return seasonal_cycle_cube


def calc_trend(cube, running_mean=True):
    """Calculate linear trend.

    A 12-month running mean can first be applied to the data.

    """

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[0] == 'time'

    if running_mean:
        cube = cube.rolling_window('time', iris.analysis.MEAN, 12)

    time_axis = cube.coord('time')
    time_axis = convert_to_seconds(time_axis)

    trend = numpy.ma.apply_along_axis(linear_trend, 0, cube.data, time_axis.points)
    trend = numpy.ma.masked_values(trend, cube.data.fill_value)

    trend = trend * 60 * 60 * 24 * 365.25  #convert from K/s to K/yr

    return trend


def linear_trend(data, time_axis):
    """Calculate the linear trend.

    polyfit returns [a, b] corresponding to y = a + bx

    """    

    if data.mask[0]:
        return data.fill_value
    else:    
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 1)[-1]


def convert_to_seconds(time_axis):
    """Convert time axis units to seconds."""

    old_units = str(time_axis.units)
    old_timestep = old_units.split(' ')[0]
    new_units = old_units.replace(old_timestep, 'seconds') 

    new_unit = cf_units.Unit(new_units, calendar=time_axis.units.calendar)  
    time_axis.convert_units(new_unit)

    return time_axis


def plot_vertical_mean_trend(trends, lons, lats, gs,
                             tick_max, tick_step, yticks):
    """Plot the vertical mean trends.

    Produces a lon / lat plot.
 
    """

    ax = plt.subplot(gs[0], projection=ccrs.PlateCarree(central_longitude=180.0))
    plt.sca(ax)

    cmap = plt.cm.RdBu_r
    ticks = numpy.arange(-tick_max, tick_max + tick_step, tick_step)
    cf = ax.contourf(lons, lats, trends, transform=ccrs.PlateCarree(),
                     cmap=cmap, extend='both', levels=ticks)

    ax.coastlines()
    ax.set_yticks(yticks, crs=ccrs.PlateCarree())
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.set_xlabel('Longitude', fontsize='small')
    ax.set_ylabel('Latitude', fontsize='small')    

    cbar = plt.colorbar(cf)
    cbar.set_label('$K yr^{-1}$')


def plot_zonal_mean_trend(trends, lats, levs, gs,
                          tick_max, tick_step, yticks):
    """Plot the zonal mean trends.

    Produces a lat / depth plot.

    """

    ax = plt.subplot(gs[1])
    plt.sca(ax)

    cmap = plt.cm.RdBu_r
    ticks = numpy.arange(-tick_max, tick_max + tick_step, tick_step)
    cf = ax.contourf(lats, levs, trends,
                     cmap=cmap, extend='both', levels=ticks)

    ax.invert_yaxis()
    ax.set_xlabel('Latitude', fontsize='small')
    ax.set_ylabel('Depth', fontsize='small')

    cbar = plt.colorbar(cf)
    cbar.set_label('$K yr^{-1}$')
    

def set_yticks(max_lat):
    """Set the ticks for the y-axis"""

    if max_lat > 60:
        yticks = [-80 ,-60, -40, -20, 0, 20, 40, 60, 80]
    else:
        yticks = [-60, -40, -20, 0, 20, 40, 60]

    return yticks


def main(inargs):
    """Run the program."""
    
    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    vm_standard_name = 'vertical_mean_'+inargs.var
    vm_long_name = vm_standard_name.replace('_', ' ')
    zm_standard_name = 'zonal_mean_'+inargs.var
    zm_long_name = zm_standard_name.replace('_', ' ')
    with iris.FUTURE.context(cell_datetime_objects=True):
        vertical_mean_cube = iris.load_cube(inargs.infile, vm_long_name & time_constraint)  
        zonal_mean_cube = iris.load_cube(inargs.infile, zm_long_name & time_constraint)

    lons = vertical_mean_cube.coord('longitude').points
    lats = vertical_mean_cube.coord('latitude').points
    levs = zonal_mean_cube.coord('depth').points
    infile_history = vertical_mean_cube.attributes['history']

    # Calculate seasonal cycle
    running_mean = True
    if inargs.seasonal_cycle:
        vertical_mean_cube = calc_seasonal_cycle(vertical_mean_cube) 
        zonal_mean_cube = calc_seasonal_cycle(zonal_mean_cube)
        running_mean = False

    # Calculate trend
    vertical_mean_trend = calc_trend(vertical_mean_cube, running_mean=running_mean)
    zonal_mean_trend = calc_trend(zonal_mean_cube, running_mean=running_mean)

    # Plot
    fig = plt.figure(figsize=[15, 10])
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1]) 

    vm_tick_max, vm_tick_step = inargs.vm_ticks
    zm_tick_max, zm_tick_step = inargs.zm_ticks
    yticks = set_yticks(inargs.max_lat)
    plot_vertical_mean_trend(vertical_mean_trend, lons, lats, gs,
                             vm_tick_max, vm_tick_step, yticks)
    plot_zonal_mean_trend(zonal_mean_trend, lats, levs, gs,
                          zm_tick_max, zm_tick_step, yticks)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info={inargs.outfile:infile_history})


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Plot the spatial trends in ocean temperature'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input temperature maps file")
    parser.add_argument("var", type=str, help="Input temperature variable name (the standard_name without the vertical_mean or zonal_mean bit)")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--vm_ticks", type=float, nargs=2, default=(0.08, 0.01), metavar=('MAX_AMPLITUDE', 'STEP'),
                        help="Maximum tick amplitude and step size for vertical mean plot [default = 0.2, 0.04]")
    parser.add_argument("--zm_ticks", type=float, nargs=2, default=(0.05, 0.005), metavar=('MAX_AMPLITUDE', 'STEP'),
                        help="Maximum tick amplitude and step size for vertical mean plot [default = 0.1, 0.01]")
    parser.add_argument("--max_lat", type=float, default=60,
                        help="Maximum latitude [default = 60]")

    parser.add_argument("--seasonal_cycle", action="store_true", default=False,
                        help="Switch for plotting the trend in the seasonal cycle instead [default: False]")

    args = parser.parse_args()            
    main(args)
