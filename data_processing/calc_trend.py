"""
Filename:     calc_trend.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the linear trend

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
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

try:
    import general_io as gio
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions
    
def calc_linear_trend(data, xaxis):
    """Calculate the linear trend.
    polyfit returns [a, b] corresponding to y = a + bx
    """    

    if data.mask[0]:
        return data.fill_value
    else:    
        return numpy.polynomial.polynomial.polyfit(xaxis, data, 1)[-1]


def get_trend_cube(cube, xaxis='time'):
    """Get the trend data.

    Args:
      cube (iris.cube.Cube)
      xaxis (iris.cube.Cube)

    """

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[0] == 'time'

    if xaxis == 'time':
        trend_data = timeseries.calc_trend(cube, per_yr=True)
        trend_unit = ' yr-1'
    else:
        trend_data = numpy.ma.apply_along_axis(calc_linear_trend, 0, cube.data, xaxis.data)
        trend_data = numpy.ma.masked_values(trend_data, cube.data.fill_value)
        trend_unit = ' '+str(xaxis.units)+'-1'

    trend_cube = cube[0, ::].copy()
    trend_cube.data = trend_data
    trend_cube.remove_coord('time')
    trend_cube.units = str(cube.units) + trend_unit

    return trend_cube


def main(inargs):
    """Run the program."""

    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time_bounds)
    except AttributeError:
        time_constraint = iris.Constraint()

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube_list = iris.load(inargs.infile, time_constraint)
        infile_metadata = {inargs.infile: cube_list[0].attributes['history']}
        if inargs.xaxis:
            xfile, xvar = inargs.xaxis
            xaxis = iris.load_cube(xfile, xvar & time_constraint)
            infile_metadata[xfile] = xaxis.attributes['history']
        else:
            xaxis = 'time'    

    out_list = iris.cube.CubeList([])
    atts = cube_list[0].attributes    
    atts['history'] = gio.write_metadata(file_info=infile_metadata)
    for cube in cube_list:
        trend_cube = get_trend_cube(cube, xaxis=xaxis)
        trend_cube.attributes = atts

        out_list.append(trend_cube)

    iris.FUTURE.netcdf_no_unlimited = True
    iris.save(out_list, inargs.outfile)

if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Calculate the linear trend at each grid point'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input ocean maps file")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time_bounds", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    parser.add_argument("--xaxis", type=str, nargs=2, metavar=('FILE', 'VARIABLE'), default=None,
                        help="Variable to use for xaxis instead of time")

    args = parser.parse_args()            
    main(args)
