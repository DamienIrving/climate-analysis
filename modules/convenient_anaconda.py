"""
Collection of commonly used convenience functions that will work with
my anaconda install but not uvcdat (because uvcdat doesn't play nice with 
pandas or netCDF4

Included functions:
pandas_dt_selector  --  Create a datetime selector for a Pandas DataFrame
get_time_axis       --  Get the time axis using the netCDF4 module
nc_to_df            --  Takes a netCDF file and returns the output in a Pandas DataFrame

"""

import os, sys, pdb

import numpy

import pandas
import netCDF4


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
    import netcdf_io as nio
    import general_io as gio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')

# Functions

def pandas_dt_selector(times_str, season=None, start=None, end=None):
    """Define a Pandas datetime selector based on the supplied datetime column""" 
    
    #note that selections can be as complex as:
    #((3 <= month) & (month <= 5)) | ((20 <= month) & (month <= 23))
    
    times_dt = pandas.to_datetime(times_str, format='%Y-%m-%d')

    month_selection = {}
    month_selection['DJF'] = (12, 1, 2)
    month_selection['MAM'] = (3, 4, 5)
    month_selection['JJA'] = (6, 7, 8)
    month_selection['SON'] = (9, 10, 11)

    combined_selection = numpy.ones(len(times_dt), dtype=bool)  #Initialise with all true

    if season:
        months = times_dt.map(lambda x: x.month)
        season_selection = (months.map(lambda val: val in month_selection[season]))
        combined_selection = combined_selection & season_selection
    
    if start:
        datetime_start = datetime.strptime(start, '%Y-%m-%d')
        start_selection = times_dt >= datetime_start  
        combined_selection = combined_selection & start_selection
    
    if end:
        datetime_end = datetime.strptime(end, '%Y-%m-%d')
        end_selection = times_dt <= datetime_end
        combined_selection = combined_selection & end_selection
    
    return combined_selection


def get_time_axis(time_variable):
    """Get the time axis using the netCDF4 module"""

    units = time_variable.units
    calendar = time_variable.calendar
    time_axis = netCDF4.num2date(time_variable[:], units=units, calendar=calendar)        
    
    return time_axis


def nc_to_df(infile, var_list, lat=None):
    """Extract the variables in var_list from the netCDF infile and place them in a pandas DataFrame
    
    Keyword arguments
    lat --  (min, max, method), where method can be mermax or spatave
    
    """

    # Define data selection options

    options = {}
    if lat:
        if lat[0] == lat[1]:
            options['latitude'] = float(lat[0])
        else:
            options['latitude'] = (float(lat[0]), float(lat[1]))
            assert lat[2] in ['mermax', 'spatave']
            options[lat[2]] = True
        
    # Extract data
    
    indata = nio.InputData(infile, var_list[0], 
                           **nio.dict_filter(options, ['latitude', 'mermax', 'spatave']))

    time_axis = indata.data.getTime().asComponentTime()
    data = numpy.zeros((len(time_axis), len(var_list)))
    data[:, 0] = numpy.array(indata.data)
    headers = [var_list[0]] 
    for i, var in enumerate(var_list[1:]):
        indata = nio.InputData(infile, var, **nio.dict_filter(options, ['latitude', 'mermax', 'spatave']))
        data[:, i+1] = numpy.array(indata.data)
        headers.append(var)

    output = pandas.DataFrame(data, index=map(lambda x: gio.standard_datetime(x), time_axis), columns=headers)

    return output, indata.global_atts['history']
