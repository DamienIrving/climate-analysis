"""Collection of convenient functions that will work with my anaconda or uvcdat install

Included functions:
adjust_lon_range     --  Express longitude values in desired 360 degree interval
single2list          -- Check if item is a list, then convert if not

"""

import numpy


def single2list(item, numpy_array=False):
    """Check if item is a list, then convert if not"""
    
    try:
        test = len(item)
    except TypeError:
        output = [item,]
    else:
        output = item 
        
    if numpy_array and not isinstance(output, numpy.ndarray):
        return numpy.array(output)
    else:
        return output


def adjust_lon_range(lons, radians=True, start=0.0):
    """Express longitude values in the 360 degree (or 2*pi radians)
    interval that begins at start.

    Arguments:
       lons      List of longitude axis values (monotonically increasing)
       radians   Specify whether the input data are in radians (True) or
                 degrees (False). Output will be the same units.
       start     Start value for the output axis (add 360 degrees or 2*pi
                 radians to get the end point)
    """
    
    lons = single2list(lons, numpy_array=True)    
    
    interval360 = 2.0*numpy.pi if radians else 360.0
    end = start + interval360    
    
    less_than_start = numpy.ones([len(lons),])
    while numpy.sum(less_than_start) != 0:
        lons = numpy.where(lons < start, lons + interval360, lons)
        less_than_start = lons < start
    
    more_than_end = numpy.ones([len(lons),])
    while numpy.sum(more_than_end) != 0:
        lons = numpy.where(lons >= end, lons - interval360, lons)
        more_than_end = lons >= end

    return lons
