"""
Filename:     plot_ohc_trend.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the spatial trend in ocean heat content

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

def linear_trend(data, time_axis):
    """Calculate the linear trend.

    polyfit returns [a, b] corresponding to y = a + bx

    """    

    if data.mask[0]:
        return data.fill_value
    else:    
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 1)[-1]


def undo_unit_scaling(cube):
    """Remove scale factor from input data so unit is Joules.

    Ocean heat content data will often have units like 10^12 J m-2.

    """

    units = str(cube.units)

    if '^' in units:
        scaling = units.split(' ')[0]
        factor = float(scaling.split('^')[-1])
        cube = cube * 10**factor
    else:
        pass

    return cube


def convert_to_seconds(time_axis):
    """Convert time axis units to seconds."""

    old_units = str(time_axis.units)
    old_timestep = old_units.split(' ')[0]
    new_units = old_units.replace(old_timestep, 'seconds') 

    new_unit = cf_units.Unit(new_units, calendar=time_axis.units.calendar)  
    time_axis.convert_units(new_unit)

    return time_axis


def zonal_heat_gain(trends, weights, lon_axis):
    """Calculate the zonal heat gain.

    In moving from W/m2 to W/m need to account for the fact 
      that the length of a degree of longitude is a function of 
      latitude. The formula for the length of one degree of 
      longitude is (pi/180) a cos(lat), where a is the radius of 
      the earth.

    """

    radius = iris.analysis.cartography.DEFAULT_SPHERICAL_EARTH_RADIUS
    
    lon_diffs = numpy.apply_along_axis(lambda x: x[1] - x[0], 1, lon_axis.bounds)
    lon_diffs = lon_diffs[numpy.newaxis, :]
    lon_extents = (math.pi / 180.) * radius * weights[0,:,:] * lon_diffs

    weighted_trends = trends * lon_extents
    zonal_heat_gain = weighted_trends.sum(axis=1) / 10**7

    return zonal_heat_gain


def plot_trends(trends, lons, lats, gs):
    """Plot the trends."""

    ax = plt.subplot(gs[0], projection=ccrs.PlateCarree(central_longitude=180.0))
    plt.sca(ax)

    cmap = plt.cm.RdBu_r
    ticks = numpy.arange(-15, 17.5, 2.5)
    cf = ax.contourf(lons, lats, trends, transform=ccrs.PlateCarree(),
                     cmap=cmap, levels=ticks, extend='both')

    ax.coastlines()
    ax.set_xticks([0, 60, 120, 180, 240, 300, 360], crs=ccrs.PlateCarree())
    ax.set_yticks([-60, -40, -20, 0, 20, 40, 60], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(zero_direction_label=True)
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.set_xlabel('Longitude', fontsize='small')
    ax.set_ylabel('Latitude', fontsize='small')    

    cbar = plt.colorbar(cf)
    cbar.set_label('$Wm^{-2}$')


def plot_zonal_heat_gain(zhg, lats, gs):
    """Plot the zonally integrated trends (i.e. zonal heat gain)"""

    ax = plt.subplot(gs[1])
    plt.sca(ax)
    ax.plot(zhg, lats)
    ax.set_xlabel('Heat gain ($10^7$ $W m^{-1}$)', fontsize='small')
    ax.set_ylabel('Latitude', fontsize='small')
    ax.axvline(0, color='0.7', linestyle='solid')
    ax.set_ylim([lats[0], lats[-1]])


def main(inargs):
    """Run the program."""
    
    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(inargs.infile, 'ocean heat content' & time_constraint)  

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names == ['time', 'latitude', 'longitude']

    time_axis = cube.coord('time')
    lat_axis = cube.coord('latitude')
    lon_axis = cube.coord('longitude')
    if lon_axis.bounds == None:
        lon_axis.guess_bounds()

    # Calculate trend
    cube = undo_unit_scaling(cube)
    time_axis = convert_to_seconds(time_axis)
    trend = numpy.ma.apply_along_axis(linear_trend, 0, cube.data, time_axis.points)
    trend = numpy.ma.masked_values(trend, cube.data.fill_value)

    # Calculate zonal mean heat gain
    weights = cosine_latitude_weights(cube)
    zhg = zonal_heat_gain(trend, weights, lon_axis)

    # Plot
    fig = plt.figure(figsize=[15, 3])
    gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1]) 
    plot_trends(trend, lon_axis.points, lat_axis.points, gs)
    plot_zonal_heat_gain(zhg, lat_axis.points, gs)

    plt.savefig(inargs.outfile, bbox_inches='tight')


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Plot the spatial trend in ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input ocean heat content file")
    parser.add_argument("var", type=str, help="Input variable standard_name")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            
    main(args)
