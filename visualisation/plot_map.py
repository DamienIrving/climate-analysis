"""
Collection of commonly used functions for plotting spatial data.

"""

# Import general Python modules

import os, sys, pdb, re
import argparse, operator

import matplotlib
matplotlib.use('Agg')

import iris
import iris.plot as iplt
import iris.quickplot as qplt

import matplotlib.pyplot as plt
import matplotlib.cm as mpl_cm

import cartopy
import cartopy.crs as ccrs

import numpy

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


# Define functions and global lists/dicts

plot_types = ['colour', 'contour', 'uwind', 'vwind', 'hatching']

input_projections = {'PlateCarree': ccrs.PlateCarree(),
                     'RotatedPole_260E_20N': ccrs.RotatedPole(pole_longitude=260, pole_latitude=20),
                     'RotatedPole_250E_20N': ccrs.RotatedPole(pole_longitude=250, pole_latitude=20),
                     'RotatedPole_270E_20N': ccrs.RotatedPole(pole_longitude=270, pole_latitude=20),
                     'RotatedPole_260E_15N': ccrs.RotatedPole(pole_longitude=250, pole_latitude=15),
                    }
#Do not use the central_longitude option when defining input_projections
#(iris can figure out longitude range on it's own) 

output_projections = {'PlateCarree': ccrs.PlateCarree(),
                      'PlateCarree_Dateline': ccrs.PlateCarree(central_longitude=180.0),
                      'SouthPolarStereo': ccrs.SouthPolarStereo(),
                      'Orthographic': ccrs.Orthographic(central_longitude=240, central_latitude=-45),
                      'RotatedPole_260E_20N_shift180': ccrs.RotatedPole(260, 20, central_rotated_longitude=180),
                     }

units_dict = {'ms-1': '$m s^{-1}$',
              'm.s-1': '$m s^{-1}$',
              '1000000 m2.s-1': '$10^6$m$^2$s$^{-1}$'}

line_style_dict = {'dashed': '--',
                   'solid': '-'}

hatch_style_dict = {'dots': '.',
                    'fwdlines_wide': '/',
                    'bwdlines_normal': '\\',
                    'bwdlines_tight': '\\\\',
                    'stars': '*'}


def collapse_time(cube, ntimes, timestep):
    """Select the desired timestep from the time axis."""

    if timestep == None:
        print 'Averaging over the %s time points' %(str(ntimes))
        new_cube = cube.collapsed('time', iris.analysis.MEAN)
    else:
        assert new_cube.coords()[0] == 'time'
        new_cube = cube[timestep, :, :]

    return new_cube  


def duplicate_input(in_list, nrows, ncols, in_type):
    """Duplicate an input value (if necessary) to match number of plots."""

    if len(in_list) == 1:
        out_list = in_list * (nrows * ncols)
    else:
        out_list = in_list

    assert len(out_list) == (nrows * ncols), \
    "Must specify an output %s for each plot" %(in_type)

    return out_list


def extract_data(infile_list, output_projection):
    """Extract data."""

    cube_dict = {} 
    metadata_dict = {}
    plot_numbers = []
    max_layers=0
    for infile, long_name, start_date, end_date, timestep, plot_type, plot_number, input_projection in infile_list:
        
        assert plot_type[:-1] in plot_types
        assert input_projection in input_projections.keys()

        # Define data constraints
        time_constraint = get_time_constraint(start_date, end_date)
        if output_projection[int(plot_number) - 1] == 'SouthPolarStereo':
            lat_constraint = iris.Constraint(latitude=lambda y: y <= 0.0)
        else:
            lat_constraint = iris.Constraint()

        # Read data
        with iris.FUTURE.context(cell_datetime_objects=True):
            new_cube = iris.load_cube(infile, long_name & time_constraint & lat_constraint)       
        try:
            new_cube = iris.util.squeeze(new_cube)
        except AttributeError:
            pass  # squeeze is not available with older versions of iris

        coord_names = [coord.name() for coord in new_cube.coords()]
        if 'time' in coord_names:
            ntimes = len(new_cube.coords('time')[0].points)
            if ntimes == 1:
                pass
            elif ntimes > 1:
                try:
                    timestep = int(timestep)
                except ValueError:
                    timestep = None
                new_cube = collapse_time(new_cube, ntimes, timestep)

        new_cube.attributes['input_projection'] = input_projection

        # Define outputs
        cube_dict[(plot_type, int(plot_number))] = new_cube
        metadata_dict[infile] = new_cube.attributes['history']
        plot_numbers.append(int(plot_number))

        layer = int(plot_type[-1])
        if layer > max_layers:
            max_layers = layer

    return cube_dict, metadata_dict, set(plot_numbers), max_layers


def get_palette(palette_name):
    """Take a palette name and return the corresponding colourmap."""

    if hasattr(plt.cm, palette_name):
        cmap = getattr(plt.cm, palette_name)
    elif palette_name in mpl_cm.cmap_d.keys():
        cmap = mpl_cm.get_cmap(palette_name)
    else:
        print "Error, color option '", palette_name, "' not a valid option"
        sys.exit(1)

    return cmap


def get_spatial_info(cube):
    """Get the spatial information required for plotting."""

    x = cube.coord('longitude').points
    y = cube.coord('latitude').points
    inproj = input_projections[cube.attributes['input_projection']]

    return x, y, inproj


def get_time_constraint(start, end):
    """Set the time constraint."""
    
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
        time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)) <= t <= iris.time.PartialDateTime(year=int(end_year), month=int(end_month), day=int(end_day)))

    return time_constraint


def multiplot(cube_dict, nrows, ncols,
              #size, spacing, projection, etc
              figure_size=None,
              subplot_spacing=0.05,
              output_projection=['PlateCarree_Dateline',],
              blank_plots=[],
              max_layers=0,
              #spatial bounds
              spstereo_limit=-30,
              region=['None',],
              #lines
              line_list=None,
              grid_lines=True,
              grid_labels=False,
              #headings
              title=None, title_size='large', 
              subplot_headings=None, side_headings=None, subplot_heading_size='medium',
              #colourbar
              no_colourbar=['False'],
              colour_type='smooth',
              colourbar_type='global', colourbar_orientation='horizontal', global_colourbar_span=0.6,
              colourbar_number_size='small',
              units=[None],
              units_size='small',
              palette=['hot_r',], extend='neither', colourbar_ticks=None,
              #contours
              contour_levels=None,
              contour_labels=False,
              contour_colours=[],
              contour_width=1.5,
              #flow
              flow_type='quiver',
              streamline_palette='YlGnBu',
              streamline_magnitude=False,
              streamline_colour='0.8',
              streamline_bounds=None,
              #hatching
              hatch_bounds=(0.0, 0.05),
              hatch_styles=('bwdlines_tight'),
              #output
              ofile='test.png'):
    """Create the plot."""

    fig = plt.figure(figsize=figure_size)
    if not figure_size:
        print 'figure width: %s' %(str(fig.get_figwidth()))
        print 'figure height: %s' %(str(fig.get_figheight()))

    set_spacing(colourbar_type, colourbar_orientation, subplot_spacing)

    if title:
        fig.suptitle(title.replace('_',' '), fontsize=title_size)

    axis_list = []
    layers = range(0, max_layers + 1)
    colour_plot_switch = False

    output_projection = duplicate_input(output_projection, nrows, ncols, "projection")
    region = duplicate_input(region, nrows, ncols, "region")
    palette = duplicate_input(palette, nrows, ncols, "palette")
    units = duplicate_input(units, nrows, ncols, "units")
    no_colourbar = duplicate_input(no_colourbar, nrows, ncols, "no colourbar switch")
    no_colourbar = map(eval, no_colourbar)
    if colourbar_ticks:
        colourbar_ticks = duplicate_input(colourbar_ticks, nrows, ncols, "colourbar ticks")

    if len(output_projection) == 1:
        output_projection = output_projection * (nrows * ncols)
    assert len(output_projection) == (nrows * ncols), \
    "Must specify an output projection for each plot"
   
    for plotnum in range(1, nrows*ncols + 1):

        if not plotnum in blank_plots:

            out_proj_name = output_projection[plotnum - 1]
            out_proj_object = output_projections[out_proj_name]
            out_region_name = region[plotnum - 1]
            palette_name = palette[plotnum - 1]
            units_name = units[plotnum - 1]
            no_colourbar_switch = no_colourbar[plotnum - 1]

            if colourbar_ticks:
                colourbar_tick_list = colourbar_ticks[plotnum -1]
            else:
                colourbar_tick_list = None 

            ax = plt.subplot(nrows, ncols, plotnum, projection=out_proj_object)
            plt.sca(ax)

            # Mini headers
            try:
                if not side_headings[plotnum - 1].lower() == 'none':
                    #ax.set_ylabel(side_headings[plotnum - 1].replace("_", " "), fontsize=subplot_heading_size)
                    plt.text(-0.1, 0.6, side_headings[plotnum - 1].replace("_", " "), fontsize=subplot_heading_size, transform=ax.transAxes, rotation='vertical')                    
                    #ax.set_title(side_headings[plotnum - 1].replace("_", " "), fontsize=subplot_heading_size, rotation='vertical', x=-0.1, y=0.5)
            except (TypeError, IndexError):
                pass

            try:
                if not subplot_headings[plotnum - 1].lower() == 'none':
                    plt.title(subplot_headings[plotnum - 1].replace("_", " "), fontsize=subplot_heading_size)
            except (TypeError, IndexError):
                pass

            # Set limits
            if out_proj_name == 'SouthPolarStereo':
                ax.set_extent((0, 360, -90.0, spstereo_limit), crs=output_projections['PlateCarree_Dateline'])
                grid_labels=False  #iris does not support this yet
            elif out_region_name != 'None':
                south_lat, north_lat, west_lon, east_lon = gio.regions[out_region_name]
                ax.set_extent((west_lon, east_lon, south_lat, north_lat), crs=out_proj_object)
            else:
                plt.gca().set_global()

            for layer in layers:

                # Add colour plot
                colour_label = 'colour'+str(layer)
                try:
                    colour_cube = cube_dict[(colour_label, plotnum)]
                    cf = plot_colour(colour_cube, ax, colour_type, colourbar_type, 
                                     palette_name, extend, colourbar_tick_list)
                    units_name = units_name if units_name else colour_cube.units.symbol
                    if colourbar_type == 'individual' and not no_colourbar_switch:
                        set_individual_colourbar(colourbar_orientation, cf, units_name, units_size, colourbar_number_size)
                    colour_plot_switch = True
                    if layer > 0:
                        print "WARNING: More than one colour layer. Only the uppermost will show."
                except KeyError:
                    pass

                # Add streamline or quiverplot
                uwind_label = 'uwind'+str(layer)
                vwind_label = 'vwind'+str(layer)
                try:
                    u_cube = cube_dict[(uwind_label, plotnum)]
                    v_cube = cube_dict[(vwind_label, plotnum)]
                    
                    x = u_cube.coords('longitude')[0].points
                    y = u_cube.coords('latitude')[0].points
                    u = u_cube.data
                    v = v_cube.data
                    plot_flow(x, y, u, v, ax, flow_type,
                              palette=streamline_palette,
                              colour=streamline_colour, 
                              plot_magnitude=streamline_magnitude, 
                              colour_bounds=streamline_bounds)
                except KeyError:
                    pass

                # Add contour lines
                contour_label = 'contour'+str(layer)
                if contour_colours:
                    try:
                        contour_colour=contour_colours[layer]
                    except IndexError:
                        contour_colour='k'
                else:
                    contour_colour='k'

                try:
                    contour_cube = cube_dict[(contour_label, plotnum)]
                    plot_contour(contour_cube, ax, contour_levels, contour_labels, 
                                 width=contour_width,
                                 colour=contour_colour)
                except KeyError:
                    pass

                # Add hatching
                hatching_label = 'hatching'+str(layer)
                try:
                    hatch_cube = cube_dict[(hatching_label, plotnum)]
                    plot_hatching(hatch_cube, ax, hatch_bounds, hatch_styles)
                except KeyError:
                    pass

            # Add lines
            if line_list:
                plot_lines(line_list)

            # Add plot features
            plt.gca().coastlines()
            if grid_lines:
                plt.gca().gridlines(draw_labels=grid_labels)
            if not no_colourbar_switch:
                if colourbar_type == 'global' and colour_plot_switch:
                    set_global_colourbar(colourbar_orientation, global_colourbar_span, cf, fig, units_name, units_size, colourbar_number_size)       

    fig.savefig(ofile, bbox_inches='tight')


def plot_colour(cube, ax,
                colour_type, colourbar_type, 
                palette, extend, ticks):
    """Plot the colour plot."""

    assert colour_type in ['smooth', 'pixels']

    x, y, inproj = get_spatial_info(cube)
    cmap = get_palette(palette) if palette else None
    if colour_type == 'smooth':
        cf = ax.contourf(x, y, cube.data, transform=inproj,  
                         cmap=cmap, levels=ticks, extend=extend)
        #colors is the option where you can give a list of hex strings
        #haven't been able to figure out how to get extent to work with that
    elif colour_type == 'pixels':
        cf = ax.pcolormesh(x, y, cube.data, transform=inproj, cmap=cmap, vmin=ticks[0], vmax=ticks[-1])

    return cf


def plot_contour(cube, ax, levels, labels_switch,
                 width=1.5, colour='k'):
    """Plot the contours."""

    x, y, inproj = get_spatial_info(cube)
    contour_plot = ax.contour(x, y, cube.data, transform=inproj,
                              colors=colour, linewidths=width, levels=levels)  
    print 'contour levels:', contour_plot.levels
    if labels_switch:
        plt.clabel(contour_plot, fmt='%.1f')

    
def plot_flow(x, y, u, v, ax, flow_type, 
              palette='YlGnBu', colour='0.8', 
              plot_magnitude=False, colour_bounds=None):
    """Plot quivers or streamlines."""

    assert flow_type in ['streamlines', 'quivers']

    if colour_bounds:
        vmin, vmax = colour_bounds
        norm = matplotlib.colors.Normalize(vmin=0, vmax=30)
    else:
        norm = None

    if flow_type == 'streamlines' and plot_magnitude:
        magnitude = (u ** 2 + v ** 2) ** 0.5
        cmap = get_palette(palette)
        ax.streamplot(x, y, u, v, transform=ccrs.PlateCarree(),
                      color=magnitude, cmap=cmap, norm=norm)  #linewidth=2, density=2
    elif flow_type == 'streamlines':
        ax.streamplot(x, y, u, v, transform=ccrs.PlateCarree(), color=colour)
    elif flow_type == 'quivers':
        ax.quiver(x, y, u, v, transform=ccrs.PlateCarree(), regrid_shape=40) 


def plot_hatching(cube, ax, hatch_bounds, hatch_styles):
    """Plot the hatching."""

    hatch_styles_converted = []
    for style in hatch_styles:
        hatch_styles_converted.append(hatch_style_dict[style])

    x, y, inproj = get_spatial_info(cube)
    ax.contourf(x, y, cube.data, transform=inproj, 
                colors='none', levels=hatch_bounds, hatches=hatch_styles_converted)
    
    # An alternative would be:
    # I found that hatch with contourf only works for certain file formats and can disappear 
    # when you put it in a pdf. This was a matplotlib bug that may have been fixed?

    # This code does the job for all file formats I have tested:
    # def stipple(pCube, thresh=0.05, central_long=0):
    #     """
    #     Stipple points using plt.scatter for values below thresh in pCube.
    #     If you have used a central_longitude in the projection, other than 0,
    #     this must be specified with the central_long keyword
    #     """
    #     xOrg = pCube.coord('longitude').points
    #     yOrg = pCube.coord('latitude').points
    #     nlon = len(xOrg)
    #     nlat = len(yOrg)
    #     xData = np.reshape( np.tile(xOrg, nlat), pCube.shape )
    #     yData = np.reshape( np.repeat(yOrg, nlon), pCube.shape )
    #     sigPoints = pCube.data < thresh
    #     xPoints = xData[sigPoints] - central_long
    #     yPoints = yData[sigPoints]
    #     plt.scatter(xPoints,yPoints,s=1, c='k', marker='.', alpha=0.5) 


def plot_lines(line_list):
    """Add lines to the plot.
    
    Args:
      line_list (list/tuple): Each item specifies the details of a new 
        line (start_lat, end_lat, start_lon, end_lon, color, style, input_projection, resolution)
    
    """
    
    for line in line_list: 
        start_lat, end_lat, start_lon, end_lon, color, style, input_projection, resolution = line
    
        assert style in line_style_dict.keys()
        assert resolution in ['high', 'low']

        start_lat = float(start_lat)
        start_lon = float(start_lon)
        end_lat = float(end_lat)
        end_lon = float(end_lon)

        lons = iris.analysis.cartography.wrap_lons(numpy.array([start_lon, end_lon]), 0, 360)
        # FIXME: start=0 might not work for all input/output projection combos

        if resolution == 'low':
            lats = numpy.array([start_lat, end_lat])         
        elif resolution == 'high':
	    assert start_lat == end_lat or start_lon == end_lon, \
	    "High res lines need constant lat or lon in reference coordinate system"

            if start_lat == end_lat:
                lons = numpy.arange(lons[0], lons[-1] + 0.5, 0.5)
                lats = numpy.repeat(start_lat, len(lons))
            else:
                lats = numpy.arange(start_lat, end_lat + 0.5, 0.5)
                lons = numpy.repeat(lons[0], len(lats))

        plt.plot(lons, lats, 
                 linestyle=line_style_dict[style], 
                 color=color, 
                 transform=input_projections[input_projection])


def set_global_colourbar(orientation, span, cf, fig, units, units_size, number_size):
    """Define the global colourbar."""

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
        cbar.set_label(units_dict[units], fontsize=units_size)
    else:
        cbar.set_label(units.replace("_", " "), fontsize=units_size)
    cbar.ax.tick_params(labelsize=number_size)


def set_individual_colourbar(orientation, cf, units, label_size, number_size):
    """Define the colourbar for an individual plot."""

    cbar = plt.colorbar(cf, orientation=orientation)

    if units in units_dict.keys():
        cbar.set_label(units_dict[units], fontsize=label_size)
    else:
        cbar.set_label(units.replace("_", " "), fontsize=label_size)
    cbar.ax.tick_params(labelsize=number_size)


def set_spacing(colourbar_type, colourbar_orientation, subplot_spacing):
    """Set the subplot spacing depending on the requested colourbar.
    
    This function sets aside space at the right side or the bottom of 
    the figure for a vertical or horizontal colourbar respectively.

    The automatic spacing performed by matplotlib will fill the 
    available space (e.g. in a 2 by 2 array the subplots will gravitate
    towards the corners), so final tweaking of the spacing between sub-plots 
    can be achieved by altering the width and height of the figure itself. 

    """

    assert colourbar_type in ['individual', 'global']
    assert colourbar_orientation in ['horizontal', 'vertical']

    hspace = subplot_spacing  # height reserved for white space between subplots
    wspace = subplot_spacing  # width reserved for blank space between subplots
    top = 0.95                # top of the subplots of the figure
    left = 0.075              # left side of the subplots of the figure

    if colourbar_type == 'global' and colourbar_orientation == 'horizontal':
        bottom = 0.15
    else:
        bottom = 0.05

    if colourbar_type == 'global' and colourbar_orientation == 'vertical':
        right = 0.825
    else:
        right = 0.925 

    plt.gcf().subplots_adjust(hspace=hspace, wspace=wspace, 
                              top=top, bottom=bottom,
                              left=left, right=right)
        

def get_blanks(nrows, ncols, plot_set):
    """Return a list of plot locations that should remain blank."""

    assert type(plot_set) == set

    nplots = nrows * ncols
    plot_numbers = range(1, nplots + 1)

    return list(set(plot_numbers) - plot_set)


def main(inargs):
    """Run program."""

    # Adjust user inputs if required
    inargs.output_projection = duplicate_input(inargs.output_projection,
                                               inargs.nrows, inargs.ncols,
                                               "projection")

    # Extract data
    cube_dict, metadata_dict, plot_set, max_layers = extract_data(inargs.infile, inargs.output_projection)
    if inargs.exclude_blanks:
        blanks = get_blanks(inargs.nrows, inargs.ncols, plot_set)
    else:
        blanks = []

    # Creat the plot
    multiplot(cube_dict, inargs.nrows, inargs.ncols,
              #size, spacing, projection, etc
              output_projection=inargs.output_projection,
              figure_size=inargs.figure_size,
              subplot_spacing=inargs.subplot_spacing,
              blank_plots=blanks,
              max_layers=max_layers,
              #spatial bounds
              spstereo_limit=inargs.spstereo_limit,
              region=inargs.region,
              #lines
              line_list=inargs.line,
              grid_lines=not inargs.no_grid_lines,
              grid_labels=inargs.grid_labels,
              #headings
              title=inargs.title,
              title_size=inargs.title_size,
              subplot_headings=inargs.subplot_headings,
              side_headings=inargs.side_headings,
              subplot_heading_size=inargs.subplot_heading_size,
              #colourbar
              no_colourbar=inargs.no_colourbar,
              colourbar_orientation=inargs.colourbar_orientation,
              colourbar_type=inargs.colourbar_type,
              colour_type=inargs.colour_type,
              global_colourbar_span=inargs.global_colourbar_span,
              colourbar_ticks=inargs.colourbar_ticks,
              units=inargs.units,
              units_size=inargs.units_size,
              colourbar_number_size=inargs.colourbar_number_size,
              palette=inargs.palette, extend=inargs.extend,
              #contours
              contour_levels=inargs.contour_levels,
              contour_labels=inargs.contour_labels,
              contour_colours=inargs.contour_colours,
              contour_width=inargs.contour_width,
              #flow
              flow_type=inargs.flow_type,
              streamline_palette=inargs.streamline_palette,
              streamline_magnitude=inargs.streamline_magnitude,
              streamline_colour=inargs.streamline_colour,
              streamline_bounds=inargs.streamline_bounds,
              #hatching
              hatch_bounds=inargs.hatch_bounds,
              hatch_styles=inargs.hatch_styles,
              #output
              ofile=inargs.ofile)
    
    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info = """
example:
  /usr/local/anaconda/bin/python plot_map.py 1 1 
  --palette RdBu_r 
  --colourbar_ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0 
  --output_projection SouthPolarStereo 
  --subplot_headings DJF 
  --infile zg_anom.nc zg_DJF none none none contour0 1 
  --contour_levels -150 -120 -90 -60 -30 0 30 60 90 120 150

"""

    description='Plot spatial map.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Input data
    parser.add_argument("nrows", type=int, help="number of rows in the entire grid of plots")
    parser.add_argument("ncols", type=int, help="number of columns in the entire grid of plots")

    parser.add_argument("--infile", type=str, action='append', default=[], nargs=8,
                        metavar=('FILENAME', 'VAR_LONG_NAME', 'START(YYYY-MM-DD)', 'END(YYYY-MM-DD)', 
                                 'TIMESTEP(can be none)', 
                                 'TYPE/LAYER(e.g. uwind0)', 
                                 'PLOTNUM',
                                 'PROJECTION'),  
                        help="""input file [default: None]:
                                TYPE can be uwind, vwind, contour, colour or hatching
                                PLOTNUM starts at 1, goes top left to bottom right
                                PROJECTION is PlateCarree for regular lat/lon grid""")

    # Plot size, spacing, projection etc
    parser.add_argument("--output_projection", type=str, nargs='*', choices=output_projections.keys(), default=['PlateCarree_Dateline',],
                        help="""output map projection: 
                                default is all PlateCarree_Dateline
                                specify a projection for all plots (order top left to bottom right, write none for blank)
                                or indicate a single choice to be applied to all plots""")
    parser.add_argument("--exclude_blanks", action="store_true", default=False,
                        help="switch for excluding plots that do not plot infile data [default: False]")
    parser.add_argument("--figure_size", type=float, default=None, nargs=2, metavar=('WIDTH', 'HEIGHT'),
                        help="size of the figure (in inches)")
    parser.add_argument("--subplot_spacing", type=float, default=0.05,
                        help="minimum spacing between subplots [default=0.05]")

    # Spatial bounds
    region_choices = gio.regions.keys()
    region_choices.append('None')
    parser.add_argument("--region", type=str, nargs='*', choices=region_choices, default=['None',],
                        help="""name of predefined region to plot:
                                default is all global
                                specify a region for all plots (order top left to bottom right, write none for blank)
                                or indicate a single choice to be applied to all plots""")
    parser.add_argument("--spstereo_limit", type=float, default=-30,
                        help="highest latitude to be plotted if the map projection is South Polar Stereographic")
                        
    # Lines and labels
    parser.add_argument("--line", type=str, action='append', default=None, nargs=8, 
                        metavar=('START_LAT', 'END_LAT', 'START_LON', 'END_LON', 'COLOUR', 'STYLE', 'PROJECTION', 'RES'),
                        help="""plot a line: 
                                STYLE can be 'solid' or 'dashed', 
                                COLOUR can be a name or fraction for grey shading
                                RES can be 'low' or 'high'""")
    parser.add_argument("--grid_labels", action="store_true", default=False,
                        help="switch for having grid labels [default: False]")
    parser.add_argument("--no_grid_lines", action="store_true", default=False,
                        help="switch for turning off grid lines [default: False]")

    # Headings
    text_sizes = ['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']
    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
    parser.add_argument("--title_size", type=str, default='large', choices=text_sizes,
                        help="plot title size [default: large]")
    parser.add_argument("--subplot_headings", type=str, nargs='*', default=None,
                        help="list of subplot headings (in order from top left to bottom right, write none for a blank)")
    parser.add_argument("--subplot_heading_size", type=str, default='medium', choices=text_sizes,
                        help="subplot heading size [default: medium]")
    parser.add_argument("--side_headings", type=str, nargs='*', default=None,
                        help="list of side (vertical) headings (in order from top left to bottom right, write none for a blank)")

    # Colourbar
    parser.add_argument("--palette", type=str, nargs='*', default=['hot_r',],
                        help="""colorbar palette:
                                default is hot_r
                                specify a palette for all plots (order top left to bottom right)
                                or indicate a single choice to be applied to all plots""")

    parser.add_argument("--no_colourbar", type=str, nargs='*', choices=('True', 'False'), default=['False'],
                        help="""switch for not plotting the colourbar:
                                default is False
                                specify true or false for all plots (order top left to bottom right)
                                or indicate a single choice to be applied to all plots""")
    parser.add_argument("--colour_type", type=str, default='smooth', choices=('smooth', 'pixels'),
                        help="how to present the colours [default=smooth]")
    parser.add_argument("--colourbar_type", type=str, default='global', choices=('individual', 'global'),
                        help="type of colourbar [default: global]")
    parser.add_argument("--colourbar_orientation", type=str, default='horizontal', choices=('horizontal', 'vertical'),
                        help="orientation of colourbar [default: horizontal]")
    parser.add_argument("--global_colourbar_span", type=float, default=0.6,
                        help="the span of the global colour bar (expressed as a fraction) [default: 0.6]")

    parser.add_argument("--colourbar_ticks", type=float, nargs='*', action='append', default=None,
                        help="""list of tick marks to appear on the colourbar: 
                                default is auto generated
                                specify a tick list for all plots by making mutliple calls to colourbar_ticks 
                                (order top left to bottom right)
                                or indicate a single choice to be applied to all plots""")
    parser.add_argument("--colourbar_number_size", type=str, default='small', choices=text_sizes,
                        help="size of the colourbar numbers [default: small]") 

    parser.add_argument("--extend", type=str, choices=('both', 'neither', 'min', 'max'), default='neither',
                        help="selector for arrow points at either end of colourbar [default: neither]")

    parser.add_argument("--units", type=str, nargs='*', default=[None], 
                        help="""Units (recognised units: ms-1)
                                default is file units
                                specify a unit for all plots (order top left to bottom right)
                                or indicate a single choice to be applied to all plots""")
    parser.add_argument("--units_size", type=str, default='small', choices=text_sizes,
                        help="Size of the units label [default: small]")

    # Contour lines
    parser.add_argument("--contour_levels", type=float, nargs='*', default=None,
                        help="list of contour levels to plot [default = auto]")
    parser.add_argument("--contour_labels", action="store_true", default=False,
                        help="switch for having contour labels [default: False]")
    parser.add_argument("--contour_colours", type=str, nargs='*', default=[],
                        help="list of contour colours in layer order [default = black]")
    parser.add_argument("--contour_width", type=float, default=1.5,
                        help="contour line width [default = 1.5]")

    # Flow
    parser.add_argument("--flow_type", type=str, default='quivers', choices=('quivers', 'streamlines'),
                        help="what to do with the uwind and vwind data [default=quiver]")
    parser.add_argument("--streamline_magnitude", action="store_true", default=False,
                        help="switch for coloring the streamlines according to their magnitude")
    parser.add_argument("--streamline_palette", type=str, default='YlGnBu',
                        help="streamline colour palette (for magnitude plot)")
    parser.add_argument("--streamline_colour", type=str, default='0.8',
                        help="streamline colour (for non-magnitude plot)")
    parser.add_argument("--streamline_bounds", type=float, nargs=2, metavar=('MIN', 'MAX'), default=None,
                        help="min and max for streamline colours [default = auto]")

    # Hatching
    parser.add_argument("--hatch_bounds", type=float, nargs='*', default=(0.0, 0.05),   
                        help="list of bounds for the hatching [default: 0.0, 0.05]") 
    parser.add_argument("--hatch_styles", type=str, nargs = '*', default=('bwdlines_tight'), choices=hatch_style_dict.keys(), 
                        help="type of hatching for each bound interval [default: bwdlines_tight]")  

    # Output options
    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    

    args = parser.parse_args()              
    main(args)
