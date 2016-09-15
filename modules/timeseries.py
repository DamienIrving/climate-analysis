"""Collection of functions for dealing with timeseries.

Functions:
  calc_seasonal_cycle  -- Calculate the seasonal cycle
  calc_trend           -- Calculate the linear trend
  convert_to_annual    -- Convert the data to annual mean

"""

import numpy
import iris
import iris.coord_categorisation
import cf_units
import pdb


def _convert_to_seconds(time_axis):
    """Convert time axis units to seconds.

    Args:
      time_axis(iris.DimCoord)

    """

    old_units = str(time_axis.units)
    old_timestep = old_units.split(' ')[0]
    new_units = old_units.replace(old_timestep, 'seconds') 

    new_unit = cf_units.Unit(new_units, calendar=time_axis.units.calendar)  
    time_axis.convert_units(new_unit)

    return time_axis


def _linear_trend(data, time_axis):
    """Calculate the linear trend.

    polyfit returns [a, b] corresponding to y = a + bx

    """    

    if data.mask[0]:
        return data.fill_value
    else:    
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 1)[-1]


def _undo_unit_scaling(cube):
    """Remove scale factor from input data so unit is Joules.

    Ocean heat content data will often have units like 10^12 J m-2.

    Args:
      cube (iris.cube.Cube)

    """

    units = str(cube.units)

    if '^' in units:
        scaling = units.split(' ')[0]
        factor = float(scaling.split('^')[-1])
        cube = cube * 10**factor
    else:
        pass

    return cube


def calc_seasonal_cycle(cube):
    """Calculate the seasonal cycle.

    cycle = (max - min) for each 12 month window 

    Args:
      cube (iris.cube.Cube)

    """

    max_cube = cube.rolling_window('time', iris.analysis.MAX, 12)
    min_cube = cube.rolling_window('time', iris.analysis.MIN, 12)

    seasonal_cycle_cube = max_cube - min_cube

    return seasonal_cycle_cube


def calc_trend(cube, running_mean=True, per_yr=True, remove_scaling=False):
    """Calculate linear trend.

    Args:
      cube (iris.cube.Cube)
      running_mean(bool, optional): 
        A 12-month running mean can first be applied to the data
      yr (bool, optional):
        Change units from per second to per year

    """

    coord_names = [coord.name() for coord in cube.dim_coords]
    assert coord_names[0] == 'time'

    cube = _undo_unit_scaling(cube)
    if running_mean:
        cube = cube.rolling_window('time', iris.analysis.MEAN, 12)

    time_axis = cube.coord('time')
    time_axis = _convert_to_seconds(time_axis)

    trend = numpy.ma.apply_along_axis(_linear_trend, 0, cube.data, time_axis.points)
    trend = numpy.ma.masked_values(trend, cube.data.fill_value)

    if per_yr:
        trend = trend * 60 * 60 * 24 * 365.25

    return trend


def convert_to_annual(cube):
    """Convert data to annual timescale.

    Args:
      cube (iris.cube.Cube)

    """

    iris.coord_categorisation.add_year(cube, 'time')
    cube = cube.aggregated_by(['year'], iris.analysis.MEAN)
    cube.remove_coord('year')

    return cube





