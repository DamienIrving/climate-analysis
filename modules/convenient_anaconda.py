"""
Collection of commonly used convenience functions that will work with
my anaconda install but not uvcdat (because uvcdat doesn't play nice with 
pandas or netCDF4

Included functions:
get_time_axis     -- Get the time axis using the netCDF4 module
wavestats_to_df   -- Takes a wavestats netCDF file and returns the output in a Pandas DataFrame

"""

import pandas
import netCDF4
import numpy


def get_time_axis(time_variable):
    """Get the time axis using the netCDF4 module"""

    units = time_variable.units
    calendar = time_variable.calendar
    time_axis = netCDF4.num2date(time_variable[:], units=units, calendar=calendar)        
    
    return time_axis


def wavestats_to_df(infile, var_list):
    """Extract the variables in var_list from the netCDF infile and place them in a pandas DataFrame"""

    fin = netCDF4.Dataset(infile)
    time_axis = get_time_axis(fin.variables['time'])

    data = numpy.zeros((len(time_axis), len(var_list)))
    headers = [] 
    for i, var in enumerate(var_list):
        data[:, i] = fin.variables[var][:]
        headers.append(var)

    output = pandas.DataFrame(data, index=map(lambda x: x.strftime("%Y-%m-%d"), time_axis), columns=headers)

    return output, fin.history
