"""
Filename:     plot_ocean_trend_ensemble.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Plot the spatial trends in the ocean

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib import ticker

import iris


# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

vis_dir = os.path.join(repo_dir, 'visualisation')
sys.path.append(vis_dir)

try:
    import general_io as gio
    import plot_ocean_trend
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions


def get_metadata(inargs, data_cube, climatology_cube):
    """Get the metadata dictionary."""
    
    metadata_dict = {}
    metadata_dict[inargs.infile] = data_cube.attributes['history']

    if climatology_cube:                  
        metadata_dict[inargs.climatology_file] = climatology_cube.attributes['history']

    return metadata_dict


def main(inargs):
    """Run the program."""

    assert len(inargs.climatology_files) == len(inargs.infiles)
    assert len(inargs.ticks) == len(inargs.infiles)

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint()

    height = 8 * inargs.nrows
    width = 8 * inargs.ncols
    fig = plt.figure(figsize=(width, height))
    fig.suptitle(inargs.basin.capitalize(), fontsize='x-large')
    colorbar_axes = None
    gs = gridspec.GridSpec(inargs.nrows, inargs.ncols)
 
    standard_name = 'zonal_mean_%s_%s' %(inargs.basin, inargs.var)
    long_name = standard_name.replace('_', ' ')

    metadata_dict = {}
    for plotnum, filename in enumerate(inargs.infiles):

        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(filename, long_name & time_constraint)  
            metadata_dict[filename] = cube.attributes['history']

        climatology = plot_ocean_trend.read_climatology(inargs.climatology_files[plotnum], long_name)
        metadata_dict[inargs.climatology_files[plotnum]] = climatology.attributes['history']

        trend, units = plot_ocean_trend.get_trend_data(cube, already_trend=False, scale_factor=inargs.scale_factor)

        lats = cube.coord('latitude').points
        levs = cube.coord('depth').points            

        title = cube.attributes['model_id']
        ylabel = 'Depth (%s)' %(cube.coord('depth').units)

        tick_max, tick_step = inargs.ticks[plotnum]
        ticks = plot_ocean_trend.set_ticks(tick_max, tick_step)
        contour_levels = plot_ocean_trend.get_countour_levels(inargs.var, 'zonal_mean')

        plot_ocean_trend.plot_zonal_mean_trend(trend, lats, levs, gs, plotnum,
                                               ticks, title, units, ylabel,
                                               inargs.palette, colorbar_axes,
                                               climatology, contour_levels)

    plt.savefig(inargs.outfile, bbox_inches='tight')
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

    parser.add_argument("infiles", type=str, nargs='*', help="Input ocean maps files")
    parser.add_argument("var", type=str, help="Input variable name (the standard_name without the vertical_mean or zonal_mean bit)")
    parser.add_argument("basin", type=str, choices=('pacific', 'indian', 'atlantic', 'globe'), help="Type of plot")
    parser.add_argument("nrows", type=int, help="number of rows in the entire grid of plots")
    parser.add_argument("ncols", type=int, help="number of columns in the entire grid of plots")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--trend", action="store_true", default=False,
                        help="Use this flag if data is already trend [default: False]")

    parser.add_argument("--climatology_files", type=str, nargs='*', default=None,
                        help="Plot climatology contours on zonal mean plots [default=None]")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--ticks", type=float, nargs=2, action='append', default=[], metavar=('MAX_AMPLITUDE', 'STEP'),
                        help="Maximum tick amplitude and step size for colorbar")
    parser.add_argument("--max_lat", type=float, default=60,
                        help="Maximum latitude [default = 60]")

    parser.add_argument("--palette", type=str, choices=('RdBu_r', 'BrBG_r'), default='RdBu_r',
                        help="Color palette [default: RdBu_r]")

    parser.add_argument("--scale_factor", type=int, default=1,
                        help="Scale factor (e.g. scale factor of 3 will multiply trends by 10^3 [default=1]")

    args = parser.parse_args()            
    main(args)
