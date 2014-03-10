"""
Plot a hovmoller diagram

"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import iris
import iris.plot as iplt
import iris.unit

import datetime

import argparse

import math


timescales = {'YEARLY': ['%y', 'mdates.YearLocator'],
              'MONTHLY': ['%b %y', 'mdates.MonthLocator'],
              'WEEKLY': ['%d/%m/%y', 'mdates.WeekdayLocator'],
              'DAILY': ['%d/%m/%y', 'mdates.DayLocator'],
              'HOURLY': ['%m/%d %H:%M', 'mdates.HourLocator'],
              'MINUTELY': ['%m/%d %H:%M', 'mdates.MinuteLocator'],
              'SECONDLY': ['%m/%d %H:%M', 'mdates.MinuteLocator']}

recognised_units = {'ms-1': '$m s^{-1}$',
                    'm s-1': '$m s^{-1}$'}


def periodConstraint(cube, t1, t2):
    """Define a time bounds constraint"""

    assert type(t1) == datetime.datetime
    assert type(t2) == datetime.datetime 

    timeUnits = cube.coord('time').units
    t1 = timeUnits.date2num(t1)
    t2 = timeUnits.date2num(t2)

    return iris.Constraint(time=lambda cell: t1 < cell.point < t2)


def _main(inargs):
 
    # Load the cube
    fname = inargs.infile
    #cube = iris.load_cube(fname, inargs.variable)
    cube = iris.load_cube(fname, iris.Constraint(inargs.variable, 
                                                 longitude=lambda v: inargs.lon_bounds[0] < v < inargs.lon_bounds[1]))

    # Apply time constraint
    if inargs.time_bounds:
        year1, month1, day1 = inargs.time_bounds[0].split('-')
        year2, month2, day2 = inargs.time_bounds[1].split('-')
        t1 = datetime.datetime(int(year1), int(month1), int(day1))
        t2 = datetime.datetime(int(year2), int(month2), int(day2))
        time_constraint = periodConstraint(cube, t1, t2)
        cube = cube.extract(time_constraint)

    # Now that we have our data in a nice way, lets create the plot
    # contour with 20 levels
    im = iplt.contourf(cube, 
                       levels=range(int(inargs.colorbar_bounds[0]), int(inargs.colorbar_bounds[1])), 
                       extend='max', cmap=inargs.palette)
    #im = iplt.pcolormesh(cube, cmap=inargs.palette)

    # Put a custom label on the x axis
    plt.xlabel('longitude')

    # Stop matplotlib providing clever axes range padding
    plt.axis('tight')

    # Set the time axis ticks
    interval = '(interval=%s)' %(str(inargs.time_tick_interval))
    locator = eval(timescales[inargs.timescale][1]+interval) 
    plt.gca().yaxis.set_major_locator(locator)

    # And format the ticks to just show the year-month-day
    plt.gca().yaxis.set_major_formatter(mdates.DateFormatter(timescales[inargs.timescale][0]))

    cb = plt.colorbar(mappable=im, orientation=inargs.orientation)

    if inargs.units in recognised_units.keys():
        cb.set_label(recognised_units[inargs.units])
    elif inargs.units:
        cb.set_label(inargs.units)
        
    if inargs.title:
        plt.title(inargs.title.replace('_',' '))    

    if inargs.ofile:
        plt.savefig(inargs.ofile)
    else:
        plt.show()


if __name__ == '__main__':

    extra_info = """ 
example (irvingnix@earthsci.unimelb.edu.au)
    python plot_hovmoller.py 
    ~/Downloads/Data/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270_absolute14_lon195-340.nc 
    envelope DAILY --time_bounds 1980-01-01 1980-02-01 --units ms-1 --title January_1980
    
    """

    description='Plot hovmoller diagram'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="input file name")
    parser.add_argument("variable", type=str, help="input file variable (long_name)")
    parser.add_argument("timescale", type=str, choices=timescales.keys(),
                        help="timescale of plotted data")

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None, metavar=('START', 'END'),
                        help="start & end date for the time axis (e.g. 1979-01-01 1979-01-21)")
    parser.add_argument("--time_tick_interval", type=int, default=2,
                        help="Interval between time tick labels")
    parser.add_argument("--colorbar_bounds", type=float, nargs=2, default=(0, 20), metavar=('MIN', 'MAX'),
                        help="Maximum and minimum values on colorbar") 
    parser.add_argument("--lon_bounds", type=float, nargs=2, default=(0, 360), metavar=('START', 'END'),
                        help="start & end longitude for the x-axis [default = 0, 360]")			

    parser.add_argument("--ofile", type=str, default=None,
                        help="name of output file [default: show]")

    parser.add_argument("--orientation", type=str, choices=('horizontal', 'vertical'), default='vertical',
                        help="Orientation of the colourbar")
    parser.add_argument("--title", type=str, default=None,
                        help="plot title [default: None]")
  
    parser.add_argument("--palette", type=str, default=None,
                        choices=('jet', 'jet_r', 'hot', 'hot_r', 'Blues', 'RdBu', 'RdBu_r'),
                        help="Colourbar name [defualt: jet]")
    parser.add_argument("--units", type=str, default=None,
                        help="Units (recognised units: ms-1)")


    args = parser.parse_args()              
    _main(args)

