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
import pdb 

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


#def _decimal_places(diff):
#    """Determine the decimal place rounding for a 
#    given difference between min and max ticks."""
#    
#    if diff > 100.0:
#        dec = 0
#    elif diff > 5.0:
#        dec = 1
#    else:
#        dec = math.floor(math.fabs(math.log10(diff)) + 2)
#    
#    return int(dec)
#
#
#def _set_colourbar(data, colourbar_colour, ticks, discrete_segments, extend):
#    """Set the colourbar."""
#
#    #Setup colour map (unless custom which is created later)
#    continuous_colourbar = False if discrete_segments or ticks else True
#    
#    if colourbar_colour:
#        if hasattr(plt.cm, colourbar_colour):
#            colourmap = getattr(plt.cm, colourbar_colour)
#        elif(isinstance(colourbar_colour, matplotlib.colors.LinearSegmentedColormap)):
#            colourmap = colourbar_colour
#        else:
#            print "Error, color option '", colourbar_colour, "' not a valid option"
#            sys.exit(1)
#            
#    #Get the min/max level for colourbar settings
#    if ticks:
#        min_level = ticks[0]
#        max_level = ticks[-1]
#    else:
#        max_level = numpy.max(data)
#        min_level = numpy.min(data)
#        diff = max_level - min_level
#        if isinstance(discrete_segments, list):
#            step = diff / float(len(discrete_segments))
#        elif discrete_segments:
#            step = diff / float(discrete_segments)
#        else:
#            step = diff / 10.0
#            
#        ticks = list(numpy.arange(min_level, max_level+(step/2), step))
#
#    dec = _decimal_places(max_level - min_level)
#    space = abs(ticks[0] - ticks[1])*0.2
#    
#    if extend == 'both':
#        min_level = min_level - space
#        max_level = max_level + space
#        ticks.append(max_level)
#        ticks.insert(0, min_level)
#
#    if extend == 'max':
#        max_level = max_level + space
#        ticks.append(max_level)
#            
#    if extend == 'min':
#        min_level = min_level - space
#        ticks.insert(0, min_level)
#
#
#    #Colourbar can be converted to a number of discete segments or a custom
#    #colourmap can be defined forcing it to a discrete map
#    if isinstance(discrete_segments, list):
#        if discrete_segments[0] in globals():
#            for i in range(0, len(discrete_segments)):
#                discrete_segments[i] = globals()[discrete_segments[i]]
#
#    if isinstance(discrete_segments, list):
#        if len(discrete_segments) != (len(ticks) - 1):
#            print 'Number of input colour segments does not match number of ticks - check extension setting'
#            sys.exit(1)
#        colourmap = matplotlib.colors.ListedColormap(discrete_segments[:], 'indexed')
#    elif discrete_segments:
#        if discrete_segments != (len(ticks) - 1):
#            print 'Number of input colour segments does not match number of ticks - check extension setting'
#            sys.exit(1)
#        colourmap = _generate_colourmap(colourmap, discrete_segments)
#    elif not continuous_colourbar:
#        colourmap = _generate_colourmap(colourmap, len(ticks))        
#        
#    #Remove added elements as we dont wont these displayed
#    if extend == 'both':
#        ticks = ticks[1: -1]
#    
#    if extend == 'max':
#        ticks = ticks[0: -1]
#
#    if extend == 'min':
#        ticks = ticks[1:]
#    
#    return ticks, colourmap, min_level, max_level, dec


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
    cube = iris.load_cube(fname, inargs.variable)
 
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
    im = iplt.contourf(cube, 20, cmap=inargs.palette)

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

    # Plot the colourbar
#    if inargs.ticks or inargs.discrete_segments:
#        ticks, colourmap, dec = _set_colourbar(cube.data, 
#                                               inargs.colourbar_colour, 
#                                               inargs.ticks, 
#                                               inargs.discrete_segments, 
#                                               inargs.extend)
#        
#        cb = plt.colorbar(mappable=im,
#                          orientation=inargs.orientation, 
#                          ticks=ticks, 
#                          extend=inargs.extend, 
#                          format='%.'+str(dec)+'f')
  
    cb = plt.colorbar(mappable=im, orientation=inargs.orientation)

    if inargs.units in recognised_units.keys():
        cb.set_label(recognised_units[inargs.units])
    elif inargs.units:
        cb.set_label(inargs.units)
        
    
    if inargs.ofile:
        plt.savefig(inargs.ofile)
    else:
        plt.show()


if __name__ == '__main__':

    extra_info = """ 



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

    parser.add_argument("--time_bounds", type=str, nargs=2, default=None,
                        help="start & end date for the time axis (e.g. 1979-01-01 1979-01-21)")
    parser.add_argument("--time_tick_interval", type=int, default=2,
                        help="Internal between time tick labels")

    parser.add_argument("--ofile", type=str, default=None,
                        help="name of output file [default: show]")

    parser.add_argument("--orientation", type=str, choices=('horizontal', 'vertical'), default='vertical',
                        help="Orientation of the colourbar")
    parser.add_argument("--title", type=str,
                        help="plot title [default: None]")
  
    parser.add_argument("--palette", type=str, default=None,
                        choices=('jet', 'jet_r', 'hot', 'hot_r', 'Blues', 'RdBu', 'RdBu_r'),
                        help="Colourbar name [defualt: jet]")
    parser.add_argument("--units", type=str, default=None,
                        help="Units (recognised units: ms-1)")
#    parser.add_argument("--ticks", type=float, nargs='*',
#                        help="list of tick marks to appear on the colour bar")
#    parser.add_argument("--discrete_segments", type=str, nargs='*',
#                        help="list of colours to appear on the colour bar")
#    parser.add_argument("--extend", type=str, choices=('both', 'neither', 'min', 'max'), default='neither',
#                        help="selector for arrow points at either end of colourbar [default: 'neither']")



    args = parser.parse_args()              
    _main(args)

