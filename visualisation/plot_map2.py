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

projections = {'PlateCarree': ccrs.PlateCarree(central_longitude=-180.0),
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
    for infile, var, start_date, end_date, timestep, plot_type, plot_number in infile_list:
        assert plot_type in plot_types
        time_constraint = get_time_constraint(start_date, end_date)
	with iris.FUTURE.context(cell_datetime_objects=True):  
            new_cube = iris.load_cube(infile, standard_names[var] & time_constraint & lat_constraint)
        
        ntimes = len(new_cube.coords('time')[0].points)
        if ntimes > 1:
            new_cube = collapse_time(new_cube, ntimes, int(timestep))

        cube_dict[(plot_type, int(plot_number))] = new_cube

    return cube_dict


def plot_flow(x, y, u, v, ax, flow_type):
    """Plot quivers or streamlines"""

    assert flow_type in ['streamlines', 'quivers']

    if flow_type == 'streamlines':
        magnitude = (u ** 2 + v ** 2) ** 0.5
        ax.streamplot(x, y, u, v, transform=ccrs.PlateCarree(), linewidth=2, density=2, color=magnitude)
    elif flow_type == 'quivers':
        ax.quiver(x, y, u, v, transform=ccrs.PlateCarree(), regrid_shape=40) 


def plot_colour(cube, colour_type, colourbar):
    """Plot the colour plot and colourbar"""

    assert colour_type in ['smooth', 'pixels']

    if colour_type == 'smooth':
        if colourbar == 'individual':
            cf = qplt.contourf(cube)
        else:
            cf = iplt.contourf(cube)  #levels, colors=colors, linewidth=0, extend='both')
    elif colour_type == 'pixels':
        cf = qplt.pcolormesh(cube)

    return cf


def plot_contour(cube):
    """Plot the contours"""

    qplt.contour(cube, colors='0.3', linewidths=2)


def set_colourbar(orientation, cf, fig):
    """Define the global colourbar"""

    assert orientation in ('horizontal', 'vertical')

    # left, bottom, width, height
    dimensions = {'horizontal': [0.1, 0.1, 0.8, 0.03],
                  'vertical': [0.85, 0.1, 0.1, 0.08]}

    colorbar_axes = fig.add_axes(dimensions[orientation])
    plt.colorbar(cf, colorbar_axes, orientation=orientation)

    # Add the colour bar
    cbar = plt.colorbar(cf, colorbar_axes, orientation=orientation)

    # Label the colour bar and add ticks
    #cbar.set_label(e1_slice.units)
    #cbar.ax.tick_params(length=0)


def set_spacing(colourbar_type):
    """Set the subplot spacing depending on the requested colourbar.
    
    This function sets aside space at the right side or the bottom of 
    the figure for a vertical or horizontal colourbar respectively.

    The automatic spacing performed by matplotlib will fill the 
    available space (e.g. in a 2 by 2 array the subplots will gravitate
    towards the corners), so final tweaking of the spacing between sub-plots 
    can be achieved by altering  the width and height of the figure itself. 

    """

    assert colourbar_type in ['individual', 'horizontal', 'vertical']

    hspace = 0.05  #height reserved for white space between subplots
    wspace = 0.05  #width reserved for blank space between subplots
    top = 0.95     #top of the subplots of the figure
    left = 0.075   #left side of the subplots of the figure

    bottom = 0.15 if colourbar_type == 'horizontal' else 0.05
    right = 0.825 if colourbar_type == 'vertical' else 0.925 

    plt.gcf().subplots_adjust(hspace=hspace, wspace=wspace, 
                              top=top, bottom=bottom,
                              left=left, right=right)
        

def multiplot(cube_dict, nrows, ncols,
              projection='PlateCarree',
              flow_type='quiver',
              colour_type='smooth',
              title=None,
              ofile='test.png'):
    """Create the plot."""

    fig = plt.figure(figsize=(14, 10))   #width, height  ### ADD TO OPTIONS
    set_spacing(inargs.colourbar)

    if title:
        fig.suptitle(inargs.title.replace('_',' '))

    axis_list = []
    for plotnum in range(1, nrows*ncols + 1):

        ax = plt.subplot(nrows, ncols, plotnum, projection=projections[projection])
        plt.sca(ax)
        #axis_list.append(plt.gca())

        # Mini header
        plt.title('Mini header')

        # Set limits
        if projection == 'SouthPolarStereo':
            ax.set_extent((0, 360, -90.0, -30.0), crs=projections['PlateCarree'])
        else:
            plt.gca().set_global()

        # Add colour plot
        try:
            colour_cube = cube_dict[('colour', plotnum)]    
            cf = plot_colour(colour_cube, colour_type, colourbar)
        except KeyError:
            pass

        # Add streamline or quiverplot
        try:
            u_cube = cube_dict[('uwind', plotnum)]
            v_cube = cube_dict[('vwind', plotnum)]
            x = u_cube.coords('longitude')[0].points
            y = u_cube.coords('latitude')[0].points
            u = u_cube.data
            v = v_cube.data
            plot_flow(x, y, u, v, ax, flow_type)
        except KeyError:
            pass

        # Add contour lines
        try:
            contour_cube = cube_dict[('contour', plotnum)]
            plot_contour(contour_cube)
        except KeyError:
            pass

        plt.gca().coastlines()
        plt.gca().gridlines()#draw_labels=True)
        if not colourbar == 'individual':
            set_colorbar(colourbar, cf, fig)       

    plt.savefig(ofile)


def main(inargs):
    """Run program."""

    # Extract data #
    
    cube_dict = extract_data(inargs.infiles, inargs.projection)
    
    # Creat the plot

    multiplot(cube_dict, inargs.nrows, inargs.ncols,
              projection=inargs.projection,
              flow_type=inargs.flow_type,
              colour_type=inargs.colour_type,
              title=inargs.title,
              ofile=inargs.ofile)
    
    #gio.write_metadata(inargs.ofile)


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
    parser.add_argument("plotnum", type=str, help="plot number corresponding to infile")
    parser.add_argument("nrows", type=int, help="number of rows in the entire grid of plots")
    parser.add_argument("ncols", type=int, help="number of columns in the entire grid of plots")

    parser.add_argument("--infiles", type=str, action='append', default=[], nargs=7,
                        metavar=('FILENAME', 'VAR', 'START', 'END', 'TIMESTEP', 'TYPE', 'PLOTNUM'),  
                        help="additional input file name, variable, start date, end date, plot type and plot number [default: None]")

    # Time considerations

    parser.add_argument("--timestep", type=int, default=None,
                        help="By default multiple timesteps are averaged. This option allows the specification of a particular timestep")
 
    # Plot options

    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--projection", type=str, default='PlateCarree', choices=projections.keys(),
                        help="map projection [default: PlateCarree]")
    parser.add_argument("--flow_type", type=str, default='quiver', choices=('quiver', 'streamlines'),
                        help="what to do with the uwind and vwind data [default=quiver]")
    parser.add_argument("--colour_type", type=str, default='smooth', choices=('smooth', 'pixels'),
                        help="how to present the colours [default=smooth]")
    parser.add_argument("--colourbar", type=str, default='horizontal', choices=('individual', 'horizontal', 'vertical') 
                        help="type of colourbar [default: horizontal]")
    # Output options

    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    

    args = parser.parse_args()              
    args.infiles.insert(0, [args.infile, args.variable, args.start, args.end, args.timestep, args.type, args.plotnum])

    main(args)
