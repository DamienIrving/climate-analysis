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
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions

standard_names = {'sf' : 'streamfunction',
                  'zg' : 'geopotential_height',
                  'ua' : 'eastward_wind',
                  'va' : 'northward_wind',
                  'tas' : 'surface_air_temperature'}

plot_types = ['colour', 'contour', 'uwind', 'vwind', 'stipple']

projections = {'PlateCarree_Greenwich': ccrs.PlateCarree(), # Centred on Greenwich, which means lons go from 0 to 360
               'PlateCarree_Dateline': ccrs.PlateCarree(central_longitude=-180.0),
               'SouthPolarStereo': ccrs.SouthPolarStereo()}

units_dict = {'ms-1': '$m s^{-1}$',
              'm.s-1': '$m s^{-1}$'}


def check_projection(cube, input_projection):
    """Check that the specified input projection is correct"""

    coord_names = [coord.name() for coord in cube.coords()]
    lon_name = next(obj for obj in coord_names if 'lon' in obj)
    first_lon = cube.coord(lon_name).points[0]

    if input_projection == 'PlateCarree_Greenwich':
        assert first_lon == 0.0, \
        'Mismatch between data grid and specified input projection'
    else:
        print 'WARNING: There is no test in this script to see if the data grid matches the specifed input projection'


def collapse_time(cube, ntimes, timestep):
    """Select the desired timestep from the time axis"""

    if timestep == None:
        print 'Averaging over the %s time points' %(str(ntimes))
        new_cube = cube.collapsed('time', iris.analysis.MEAN)
    else:
        new_cube = cube[timestep, :, :]

    return new_cube  


def extract_data(infile_list, input_projection, output_projection):
    """Extract data"""

    if output_projection == 'SouthPolarStereo':
        lat_constraint = iris.Constraint(latitude=lambda y: y <= 0.0)
    else:
        lat_constraint = iris.Constraint()

    cube_dict = {} 
    metadata_dict = {}
    for infile, var, start_date, end_date, timestep, plot_type, plot_number in infile_list:
        assert plot_type in plot_types
        time_constraint = get_time_constraint(start_date, end_date)
	with iris.FUTURE.context(cell_datetime_objects=True):  
            new_cube = iris.load_cube(infile, standard_names[var] & time_constraint & lat_constraint)
        
        check_projection(new_cube, input_projection)
        ntimes = len(new_cube.coords('time')[0].points)
        if ntimes > 1:
            try:
                timestep = int(timestep)
            except ValueError:
                timestep = None
            new_cube = collapse_time(new_cube, ntimes, timestep)

        cube_dict[(plot_type, int(plot_number))] = new_cube
        metadata_dict[infile] = new_cube.attributes['history']

    return cube_dict, metadata_dict


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


def multiplot(cube_dict, nrows, ncols,
              input_projection='PlateCarree_Greenwich',
              #broad plot options
              figure_size=None,
              subplot_spacing=0.05,
              output_projection='PlateCarree_Dateline',
              flow_type='quiver',
              box_list=None,
              #headings
              title=None, subplot_headings=None,
              #colourbar
              colour_type='smooth',
              colourbar_type='horizontal', colourbar_span=0.6,
              units=None,
              palette='jet', extend='neither', ticks=None,
              #output
              ofile='test.png'):
    """Create the plot."""

    fig = plt.figure(figsize=figure_size)
    if not figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    set_spacing(colourbar_type, subplot_spacing)

    if title:
        fig.suptitle(inargs.title.replace('_',' '))

    axis_list = []
    colour_plot_switch = False
    for plotnum in range(1, nrows*ncols + 1):

        ax = plt.subplot(nrows, ncols, plotnum, projection=projections[output_projection])
        plt.sca(ax)

        # Mini header
        try:
            if not subplot_headings[plotnum - 1].lower() == 'none':
                plt.title(subplot_headings[plotnum - 1].replace("_", " "))
        except (TypeError, IndexError):
            pass

        # Set limits
        if output_projection == 'SouthPolarStereo':
            ax.set_extent((0, 360, -90.0, -30.0), crs=projections[input_projection])
        else:
            plt.gca().set_global()

        # Add colour plot
        try:
            colour_cube = cube_dict[('colour', plotnum)]    
            cf = plot_colour(colour_cube, colour_type, colourbar_type, 
                             palette, extend, ticks)
            colour_plot_switch = True
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
            plot_flow(x, y, u, v, ax, flow_type, input_projection)
        except KeyError:
            pass

        # Add contour lines
        try:
            contour_cube = cube_dict[('contour', plotnum)]
            plot_contour(contour_cube)
        except KeyError:
            pass

        # Add boxes
        if box_list:
            plot_boxes(box_list, input_projection)

        # Add plot features
        plt.gca().coastlines()
        plt.gca().gridlines()#draw_labels=True)
        if not colourbar_type == 'individual' and colour_plot_switch:
            plot_units = units if units else colour_cube.units.symbol
            set_colourbar(colourbar_type, colourbar_span, cf, fig, plot_units)       

    plt.savefig(ofile)


def plot_boxes(box_list, input_projection):
    """Add boxes to the plot.
    
    Arguments:
        box  ->  (name, color, style)
    
    """
    styles = {}
    styles['dashed'] = '--'
    styles['solid'] = '-'
    
    for box in box_list: 
        region, color, style = box
	
        assert region in nio.regions.keys()
        assert style in styles.keys()

	south_lat, north_lat = nio.regions[region][0][0: 2]
        west_lon, east_lon = nio.regions[region][1][0: 2]
        
       	# Adjust the longitude values as required
	assert (0.0 <= east_lon <= 360) and  (0.0 <= west_lon <= 360), \
	"""Longitude coordinates for the box must be 0 < lon < 360"""  
	if (east_lon < west_lon) and (west_lon > 180.0):
            west_lon = west_lon - 360.0
	if (east_lon < west_lon) and (west_lon <= 180.0):
            east_lon = east_lon + 360.0

	# Define the plot borders
	borders = {}
	borders['north_lons'] = borders['south_lons'] =  numpy.arange(west_lon, east_lon + 1, 1)
	borders['south_lats'] = numpy.repeat(south_lat, len(borders['south_lons']))
	borders['north_lats'] = numpy.repeat(north_lat, len(borders['south_lons']))

	borders['east_lats'] = borders['west_lats'] = numpy.arange(south_lat, north_lat + 1, 1)
	borders['west_lons'] = numpy.repeat(west_lon, len(borders['west_lats']))
	borders['east_lons'] = numpy.repeat(east_lon, len(borders['west_lats']))

	for side in ['north', 'south', 'east', 'west']:
            x, y = borders[side+'_lons'], borders[side+'_lats']
            plt.plot(x, y, linestyle=style, color=color, transform=projections[input_projection])


def plot_colour(cube, 
                colour_type, colourbar_type, 
                palette, extend, ticks):
    """Plot the colour plot"""

    assert colour_type in ['smooth', 'pixels']

    if palette:
	if hasattr(plt.cm, palette):
            cmap = getattr(plt.cm, palette)
            colors = None
	else:
            print "Error, color option '", palette, "' not a valid option"
            sys.exit(1)

    if colour_type == 'smooth':
        if colourbar_type == 'individual':
            cf = qplt.contourf(cube, cmap=cmap, colors=colors, levels=ticks, extend=extend)
        else:
            cf = iplt.contourf(cube, cmap=cmap, colors=colors, levels=ticks, extend=extend)
            # colors is the option where you can give a list of hex strings
            # I haven't been able to figure out how to get extent to work with that

    elif colour_type == 'pixels':
        cf = qplt.pcolormesh(cube)

    return cf


def plot_contour(cube):
    """Plot the contours"""

    qplt.contour(cube, colors='0.3', linewidths=2)


def plot_flow(x, y, u, v, ax, flow_type, input_projection):
    """Plot quivers or streamlines"""

    assert flow_type in ['streamlines', 'quivers']

    if flow_type == 'streamlines':
        magnitude = (u ** 2 + v ** 2) ** 0.5
        ax.streamplot(x, y, u, v, transform=projections[input_projection], linewidth=2, density=2, color=magnitude)
    elif flow_type == 'quivers':
        ax.quiver(x, y, u, v, transform=projections[input_projection], regrid_shape=40) 


def set_colourbar(orientation, span, cf, fig, units):
    """Define the global colourbar"""

    assert orientation in ('horizontal', 'vertical')

    if orientation == 'horizontal':
        left = (1 - span) / 2.0
        bottom = 0.1
        width = span
        height = 0.025
    elif orientation == 'vertical':
        left = 0.87
        bottom = (1 - span) / 2.0
        width = 0.025
        height = span
        
    colorbar_axes = fig.add_axes([left, bottom, width, height])
    plt.colorbar(cf, colorbar_axes, orientation=orientation)

    # Add the colour bar
    cbar = plt.colorbar(cf, colorbar_axes, orientation=orientation)

    # Label the colour bar and add ticks
    if units in units_dict.keys():
        cbar.set_label(units_dict[units])
    else:
        cbar.set_label(units.replace("_", " "))
    #cbar.ax.tick_params(length=0)


def set_spacing(colourbar_type, subplot_spacing):
    """Set the subplot spacing depending on the requested colourbar.
    
    This function sets aside space at the right side or the bottom of 
    the figure for a vertical or horizontal colourbar respectively.

    The automatic spacing performed by matplotlib will fill the 
    available space (e.g. in a 2 by 2 array the subplots will gravitate
    towards the corners), so final tweaking of the spacing between sub-plots 
    can be achieved by altering  the width and height of the figure itself. 

    """

    assert colourbar_type in ['individual', 'horizontal', 'vertical']

    hspace = subplot_spacing  # height reserved for white space between subplots
    wspace = subplot_spacing  # width reserved for blank space between subplots
    top = 0.95                # top of the subplots of the figure
    left = 0.075              # left side of the subplots of the figure

    bottom = 0.15 if colourbar_type == 'horizontal' else 0.05
    right = 0.825 if colourbar_type == 'vertical' else 0.925 

    plt.gcf().subplots_adjust(hspace=hspace, wspace=wspace, 
                              top=top, bottom=bottom,
                              left=left, right=right)
        

def main(inargs):
    """Run program."""

    # Extract data #
    
    cube_dict, metadata_dict = extract_data(inargs.infiles, inargs.input_projection, inargs.output_projection)
    
    # Creat the plot

    multiplot(cube_dict, inargs.nrows, inargs.ncols,
              input_projection=inargs.input_projection,
              #broad plot options
              output_projection=inargs.output_projection,
              figure_size=inargs.figure_size,
              subplot_spacing=inargs.subplot_spacing,
              flow_type=inargs.flow_type,
              box_list=inargs.boxes,
              #headings
              title=inargs.title,
              subplot_headings=inargs.subplot_headings,
              #colourbar
              colourbar_type=inargs.colourbar_type,
              colour_type=inargs.colour_type,
              colourbar_span=inargs.colourbar_span,
              units=inargs.units,
              palette=inargs.palette, extend=inargs.extend,
              ticks=inargs.ticks,
              #output
              ofile=inargs.ofile)
    
    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info = """
example:
  

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
    parser.add_argument("plotnum", type=str, help="plot number corresponding to infile (grid is filled top left to bottom right)")
    parser.add_argument("nrows", type=int, help="number of rows in the entire grid of plots")
    parser.add_argument("ncols", type=int, help="number of columns in the entire grid of plots")

    parser.add_argument("--infiles", type=str, action='append', default=[], nargs=7,
                        metavar=('FILENAME', 'VAR', 'START', 'END', 'TIMESTEP', 'TYPE', 'PLOTNUM'),  
                        help="additional input file name, variable, start date, end date, plot type and plot number [default: None]")
    parser.add_argument("--input_projection", type=str, default='PlateCarree_Greenwich', choices=projections.keys(),
                        help="input map projection [default: PlateCarree_Greenwich]") 

    # Broad plot options
    
    parser.add_argument("--figure_size", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
    parser.add_argument("--subplot_spacing", type=float, default=0.05,
                        help="minimum spacing between subplots [default=0.05]")
    parser.add_argument("--output_projection", type=str, default='PlateCarree_Dateline', choices=projections.keys(),
                        help="output map projection [default: PlateCarree_Dateline]")
    parser.add_argument("--flow_type", type=str, default='quivers', choices=('quivers', 'streamlines'),
                        help="what to do with the uwind and vwind data [default=quiver]")
    parser.add_argument("--boxes", type=str, action='append', default=None, nargs=3, metavar=('NAME', 'COLOUR', 'STYLE'),
                        help="""draw a box - style can be 'solid' or 'dashed', colour can be a name or fraction for grey shading""")

    # Headings

    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--subplot_headings", type=str, nargs='*', default=None,
                        help="list of subplot headings (in order from top left to bottom right, write none for a blank)")

    # Colourbar

    parser.add_argument("--colour_type", type=str, default='smooth', choices=('smooth', 'pixels'),
                        help="how to present the colours [default=smooth]")
    parser.add_argument("--colourbar_type", type=str, default='horizontal', choices=('individual', 'horizontal', 'vertical'),
                        help="type of colourbar [default: horizontal]")
    parser.add_argument("--colourbar_span", type=float, default=0.6,
                        help="the span of the colour bar (expressed as a fraction) [default: 0.6]")
    parser.add_argument("--palette", type=str, default='jet',
                        choices=('jet', 'jet_r', 'hot', 'hot_r', 'Blues', 'RdBu', 'RdBu_r', 'Oranges'),
                        help="Colourbar colours [defualt: jet]")
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="list of tick marks to appear on the colour bar [default = auto]")
    parser.add_argument("--extend", type=str, choices=('both', 'neither', 'min', 'max'), default='neither',
                        help="selector for arrow points at either end of colourbar [default: neither]")
    parser.add_argument("--units", type=str, default=None, 
                        help="Units (recognised units: ms-1)")

    # Output options

    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    

    args = parser.parse_args()              
    args.infiles.insert(0, [args.infile, args.variable, args.start, args.end, args.timestep, args.type, args.plotnum])

    main(args)
