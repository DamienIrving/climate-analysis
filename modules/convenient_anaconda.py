"""
Collection of commonly used convenience functions that will work with
my anaconda install but not uvcdat (because uvcdat doesn't play nice with 
pandas or netCDF4

Included functions:
wavestats_to_df   -- Takes a wavestats netCDF file and returns the output in a Pandas DataFrame

"""

import pandas
import netCDF4
import numpy


def wavestats_to_df(infile):
    """Extract wave envelope stats and output to pandas DataFrame"""

    fin = netCDF4.Dataset(infile)
    time_axis = get_time_axis(fin.variables['time'])

    var_list = ['ampmean', 'ampmedian', 'extent', 'startlon', 'endlon']

    data = numpy.zeros((len(time_axis), len(var_list)))
    headers = [] 
    for i, var in enumerate(var_list):
        data[:, i] = fin.variables[var][:]
        headers.append(var)

    output = pandas.DataFrame(data, index=map(lambda x: x.strftime("%Y-%m-%d"), time_axis), columns=headers)

    return output, fin.history
