"""
Collection of commonly used functions for plotting spatial data.

Included functions: 

"""

# Import general Python modules #

import os, sys, pdb, re
import argparse

import iris
from iris.time import PartialDateTime
import iris.plot as iplt
import iris.quickplot as qplt

import matplotlib.pyplot as plt
import matplotlib.cm as mpl_cm

import cartopy
import cartopy.crs as ccrs

import numpy


# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions

standard_names = {'sf' : 'streamfunction',
                  'zg' : 'geopotential_height',
                  'ua' : 'eastward_wind',
                  'va' : 'northward_wind',
                  'tas' : 'surface_air_temperature'}


def get_time_constraint(start, end):
    """Set the time constraint"""
    
    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    assert re.search(date_pattern, start) or start == ''
    assert re.search(date_pattern, end) or end == ''
    
    if not start and not end:
        time_constraint = iris.Constraint()
    elif (start and not end) or (start == end):
        year, month, day = start.split('-')    
        time_constraint = iris.Constraint(time=iris.time.PartialDateTime(year=int(year), month=int(month), day=int(day)))
    elif end and not start:
        year, month, day = end.split('-')    
        time_constraint = iris.Constraint(time=iris.time.PartialDateTime(year=int(year), month=int(month), day=int(day)))
    else:  
        start_year, start_month, start_day = start.split('-') 
        end_year, end_month, end_day = end.split('-')
        time_constraint = iris.Constraint(time=lambda t: PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)) <= t <= PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)))

    return time_constraint


def collapse_time(cube, ntimes, timestep):
    """Select the desired timestep from the time axis"""

    if timestep:
        new_cube = cube[timestep, :, :]
    else:
        print 'Averaging over the %s time points' %(str(ntimes))
        new_cube = cube.collapsed('time', iris.analysis.MEAN)

    return new_cube  


def main(inargs):
    """Run program."""

    # Extract data #
    
    time_constraint = get_time_constraint(inargs.start, inargs.end)
    lat_constraint = iris.Constraint(latitude=lambda y: y <= 0.0)

    with iris.FUTURE.context(cell_datetime_objects=True):
        u_cube = iris.load_cube(inargs.u_file, inargs.u_var & time_constraint & lat_constraint)
        v_cube = iris.load_cube(inargs.v_file, inargs.v_var & time_constraint & lat_constraint)
        if inargs.zg_file:
            zg_cube = iris.load_cube(inargs.zg_file, inargs.zg_var & time_constraint & lat_constraint)

    ntimes = len(u_cube.coords('time')[0].points)
    if ntimes > 1:
        u_cube = collapse_time(u_cube, ntimes, inargs.timestep)
        v_cube = collapse_time(v_cube, ntimes, inargs.timestep)
        if inargs.zg_file:
            zg_cube = collapse_time(zg_cube, ntimes, inargs.timestep)
    
    ## Define the data
    x = u_cube.coords('longitude')[0].points
    y = u_cube.coords('latitude')[0].points
    u = u_cube.data
    v = v_cube.data

    plt.figure(figsize=(8, 10))

    ## Select the map projection
    ax = plt.axes(projection=ccrs.SouthPolarStereo())
   
    ax.set_extent((x.min(), x.max(), y.min(), -30.0), crs=ccrs.PlateCarree())
    
    ## Plot coast and gridlines (currently an error with coastline plotting)
    ax.coastlines()
    ax.gridlines()
    #ax.set_global()

    ## Plot the data
    # Streamplot
    magnitude = (u ** 2 + v ** 2) ** 0.5
    ax.streamplot(x, y, u, v, transform=ccrs.PlateCarree(), linewidth=2, density=2, color=magnitude)

    # Wind vectors
    #ax.quiver(x, y, u, v, transform=ccrs.PlateCarree(), regrid_shape=40) 

    # Contour
    if inargs.zg_file:
        qplt.contour(zg_cube, colors='0.3', linewidths=2)

    if inargs.title:
        plt.title(inargs.title.replace('_',' '))

    plt.savefig(inargs.ofile)
    gio.write_metadata(inargs.ofile)


if __name__ == '__main__':

    extra_info = """
improvements:
  

"""

    description='Plot spatial map.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Input data

    parser.add_argument("--u_file", type=str, default=None, 
                        help="input file name for the zonal wind")
    parser.add_argument("--u_var", type=str, default=None 
                        help="zonal wind variable")
    parser.add_argument("--v_file", type=str, default=None,
                        help="input file name for the meridional wind")
    parser.add_argument("--v_var", type=str, default=None,
                        help="meridional wind variable")

    parser.add_argument("--contour_file", type=str, default=None, 
                        help="input file name for the contours")
    parser.add_argument("--contour_var", type=str, default=None,
                        help="standard_name for the geopotential height zonal anomaly")

    # Time considerations

    parser.add_argument("--start", type=str, default='',
                        help="start date in YYYY-MM-DD format [default = None])")
    parser.add_argument("--end", type=str, default='',
                        help="end date in YYY-MM-DD format [default = None], let START=END for single time step (can be None)")
    parser.add_argument("--timestep", type=int, default=None,
                        help="By default multiple timesteps are averaged. This option allows the specification of a particular timestep")
 
    # Output options

    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--projection", type=str, choices=('cyl', 'nsper', 'spstere', 'npstere'),
                        help="map projection [default: cyl]")

    args = parser.parse_args()              

    main(args)
