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

plot_types = ['colour', 'contour', 'uwind', 'vwind', 'stipple']

projections = {'PlateCarree': ccrs.PlateCarree(),
               'SouthPolarStereo': ccrs.SouthPolarStereo()}


def get_time_constraint(start, end):
    """Set the time constraint"""
    
    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    if start.lower() == 'none':
        start = None
    else:
        assert re.search(date_pattern, start)

    if end.lower() == 'none':
        end = None
    else:
        assert re.search(date_pattern, end)

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


def extract_data(infile_list, projection):
    """Extract data"""

    if projection == 'SouthPolarStereo':
        lat_constraint = iris.Constraint(latitude=lambda y: y <= 0.0)
    else:
        lat_constraint = iris.Constraint()

    cube_dict = {}
    for key in plot_types:
        cube_dict[key] = []
        type_count[key] = 0 

    for infile, var, start_date, end_date, timestep, plot_type in infile_list:
        assert plot_type in plot_types
        time_constraint = get_time_constraint(inargs.start, inargs.end)
	with iris.FUTURE.context(cell_datetime_objects=True):  
            new_cube = iris.load_cube(infile, standard_names[var] & time_constraint & lat_constraint)
        
        ntimes = len(new_cube.coords('time')[0].points)
        if ntimes > 1:
            new_cube = collapse_time(new_cube, ntimes, int(timestep))

        cube_dict[plot_type].append(new_cube)
        type_count[plot_type] += 1

    nplots = numpy.max(type_count.values())

    return cube_dict, nplots


def plot_flow(x, y, u, v, ax, flow_type):
    """Plot quivers or streamlines"""

    assert flow_type in ['streamlines', 'quivers']

    if flow_type == 'streamlines':
        magnitude = (u ** 2 + v ** 2) ** 0.5
        ax.streamplot(x, y, u, v, transform=ccrs.PlateCarree(), linewidth=2, density=2, color=magnitude)
    elif flow_type == 'quivers':
        ax.quiver(x, y, u, v, transform=ccrs.PlateCarree(), regrid_shape=40) 



def multiplot(cube_dict, nplots,
              projection='PlateCarree',
              flow_type='quiver'
              title=None,
              ofile='test.png'):
    """Create the plot."""

    plt.figure(figsize=(8, 10))

    # Setup the map
    ax = plt.axes(projection=projections[projection])
    ax.set_extent((x.min(), x.max(), y.min(), -30.0), crs=projections['PlateCarree'])

    ax.coastlines()
    ax.gridlines()
    #ax.set_global()

    # Plot away!

    for plotnum in range(0, nplots):

        # Streamline or quiverplot
        try:
            u_cube = cube_dict['uwind'][plotnum]
            v_cube = cube_dict['vwind'][plotnum]
            x = u_cube.coords('longitude')[0].points
            y = u_cube.coords('latitude')[0].points
            u = u_cube.data
            v = v_cube.data
            plot_flow(x, y, u, v, ax, flow_type)
        except IndexError:
            pass

        # Contour lines
        try:
            cont_cube = cube_dict['contour'][plotnum]
            qplt.contour(cont_cube, colors='0.3', linewidths=2)
        except IndexError:
            pass



       
    if title:
        plt.title(inargs.title.replace('_',' '))

    plt.savefig(ofile)


def main(inargs):
    """Run program."""

    # Extract data #
    
    cube_dict, nplots = extract_data(inargs.infiles, inargs.projection)
    
    # Creat the plot

    multiplot(cube_dict, nplots,
              projection=inargs.projection,
              flow_type=inargs.flow_type,
              title=inargs.title,
              ofile=inargs.ofile)
    

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

    parser.add_argument("infile", type=str, help="input file name")
    parser.add_argument("variable", type=str, help="input file variable")
    parser.add_argument("start", type=str, help="start date in YYYY-MM-DD format (can be none)")
    parser.add_argument("end", type=str, help="end date in YYY-MM-DD, let START=END for single time step (can be None)")
    parser.add_argument("timestep", type=str, help="for data with a time axis of len > 1 pick a timestep (can be None)")
    parser.add_argument("type", type=str, help="plot type: can be uwind, vwind, contour, colour, stipple")

    parser.add_argument("--infiles", type=str, action='append', default=[], nargs=5,
                        metavar=('FILENAME', 'VAR', 'START', 'END', 'TIMESTEP', 'TYPE'),  
                        help="additional input file name, variable, start date, end date and plot type [default: None]")

    # Time considerations

    parser.add_argument("--timestep", type=int, default=None,
                        help="By default multiple timesteps are averaged. This option allows the specification of a particular timestep")
 
    # Plot options

    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--projection", type=str, default='PlateCarree', choices=projections.keys(),
                        help="map projection [default: PlateCarree]")
    parser.add_argument("--flow_type", type=str, default='quiver', choices=('quiver', 'streamlines'),
                        help="what to do with the uwind and vwind data")

    # Output options

    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    

    args = parser.parse_args()              
    args.infiles.insert(0, [args.infile, args.variable, args.start, args.end, args.timestep, args.type])

    main(args)
