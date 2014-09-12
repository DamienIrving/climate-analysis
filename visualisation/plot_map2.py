"""
Collection of commonly used functions for plotting spatial data.

Included functions: 

"""

# Import general Python modules #

import iris
import datetime
from iris.time import PartialDateTime

import matplotlib.pyplot as plt
import iris.plot as iplt
import iris.quickplot as qplt

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

def 







def _main(inargs):
    """Run program."""

    # Extract data #
    
    time_constraint = get_time_constraint(inargs.start, inargs.end)
    
    time_constraint = iris.Constraint(time=lambda t: PartialDateTime(year=1989, month=3) <= t <= PartialDateTime(year=1989, month=5))
    lat_constraint = iris.Constraint(latitude=lambda y: y <= 0.0)

    with iris.FUTURE.context(cell_datetime_objects=True):
        u_cube = iris.load_cube(ufile, 'eastward_wind' & time_constraint & lat_constraint)
        v_cube = iris.load_cube(vfile, 'northward_wind' & time_constraint & lat_constraint)

    u_temporal_mean = u_cube.collapsed('time', iris.analysis.MEAN)  
    v_temporal_mean = v_cube.collapsed('time', iris.analysis.MEAN)

    ## Define the data
    x = u_temporal_mean.coords('longitude')[0].points
    y = u_temporal_mean.coords('latitude')[0].points
    u = u_temporal_mean.data
    v = v_temporal_mean.data

    plt.figure(figsize=(8, 10))

    ## Select the map projection
    ax = plt.axes(projection=ccrs.SouthPolarStereo())
   #ax = plt.axes(projection=ccrs.PlateCarree())
   
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
    #qplt.contourf(u_temporal_mean)

    plt.show()


if __name__ == '__main__':

    extra_info = """
improvements:
  

"""

    description='Plot spatial map.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("u_file", type=str, help="input file name for the zonal wind")
    parser.add_argument("u_var", type=str, help="standard_name for the zonal wind")
    parser.add_argument("v_file", type=str, help="input file name for the meridional wind")
    parser.add_argument("v_var", type=str, help="standard_name for the meridional wind")
    parser.add_argument("zg_file", type=str, help="input file name for the geopoential height")
    parser.add_argument("zg_var", type=str, help="standard_name for the geopotential height")

    parser.add_argument("--start", type=str, default=None,
                        help="start date in YYYY-MM-DD format [default = None])")
    parser.add_argument("--end", type=str, default=None,
                        help="end date in YYY-MM-DD format [default = None], let START=END for single time step (can be None)")
 
    parser.add_argument("--ofile", type=str, 
                        help="name of output file [default: test.png]")

    
    parser.add_argument("--quiver_type", type=str, choices=('wind', 'waf'),
                        help="type of quiver being plotted [defualt: wind]")
    parser.add_argument("--quiver_thin", type=int, 
                        help="thinning factor for plotting quivers [defualt: 1]")
    parser.add_argument("--key_value", type=float, 
                        help="size of the wind quiver in the key (plot is not scaled to this) [defualt: 1]")
    parser.add_argument("--quiver_scale", type=float, 
                        help="data units per arrow length unit (smaller value means longer arrow) [defualt: 170]")
    parser.add_argument("--quiver_width", type=float,
                        help="shaft width in arrow units [default: 0.0015, i.e. 0.0015 times the width of the plot]")
    parser.add_argument("--quiver_headwidth", type=float,
                        help="head width as multiple of shaft width [default: 3.5]")
    parser.add_argument("--quiver_headlength", type=float, 
                        help="head length as multiple of shaft width [default: 4.0]")


    args = parser.parse_args()              

    _main(args)