"""
Collection of commonly used functions for general file input and output.

Functions:
  check_xrayDataset        -- Check xray.Dataset for data format compliance
  get_cmip5_file_details   -- Extract details from a CMIP5 filename
  get_subset_kwargs        -- Get keyword arguments for xray subsetting
  get_time_constraint      -- Get the time constraint used for reading an iris cube 
  get_timescale            -- Get the timescale
  get_timestamp            -- Return a time stamp that includes the command line entry
  iris_vertical_constraint -- Define vertical constraint for iris cube loading.
  read_dates               -- Read in a list of dates
  set_dim_atts             -- Set dimension attributes
  set_global_atts          -- Update the global attributes of an xray.DataArray
  set_outfile_date         -- Take an outfile name and replace existing date with new one
  standard_datetime        -- Convert any arbitrary date/time to standard format: YYYY-MM-DD
  update_history_att       -- Update the global history attribute of an xray.DataArray
  vertical_bounds_text     -- Geneate text describing the vertical bounds of a data selection
  write_dates              -- Write a list of dates
  write_metadata           -- Write a metadata output file

"""

# Import general Python modules

import os, sys, pdb
import datetime, numpy
from dateutil import parser
from collections import defaultdict
import re
import iris

# Import my modules

try:
    from git import Repo 
    cwd = os.getcwd()
    repo_dir = '/'
    for directory in cwd.split('/')[1:]:
        repo_dir = os.path.join(repo_dir, directory)
        if directory == 'climate-analysis':
            break
    try:
        MODULE_HASH = Repo(repo_dir).head.commit.hexsha
    except AttributeError: # Older versions of gitpython work differently
        MODULE_HASH = Repo(repo_dir).commits()[0].id
except ImportError:
    MODULE_HASH = 'unknown'

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
try:
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

#[south_lat, north_lat, west_lon, east_lon]
regions = {'asl': [-75, -60, 180, 310],
           'aus': [-45, -10, 110, 160],
           'ausnz': [-50, 0, 100, 185],
           'emia': [-10, 10, 165, 220],
           'emib': [-15, 5, 250, 290],
           'emic': [-10, 20, 125, 145],
           'eqpacific': [-30, 30, 120, 280],
           'nino1': [-10, -5, 270, 280],
           'nino2': [-5, 0, 270, 280],
           'nino12': [-10, 0, 270, 280],
           'nino3': [-5, 5, 210, 270],
           'nino34': [-5, 5, 190, 240],
           'nino4': [-5, 5, 160, 210],
           'point': [-59.25, -59.25, 255, 255],
           'sh': [-90, 0, 0, 360],
           'shextropics15': [-90, -15, 0, 360],
           'shextropics20': [-90, -20, 0, 360],
           'shextropics30': [-90, -30, 0, 360],
           'small': [-5, 0, 10, 15],
           'tropics': [-30, 30, 0, 360],
           'glatt': [20, 80, -180, 180],
           'nonpolar70': [-70, 70, 0, 360],
           'nonpolar80': [-80, 80, 0, 360],
           'sh-psa': [-90, 0, 90, 450],
           'sh-psa-extra': [-90, 30, 90, 450],
           'world-dateline': [-90, 90, 0, 360],
           'world-dateline-duplicate360': [-90, 90, 0, 360],
           'world-greenwich': [-90, 90, -180, 180],
           'world-psa': [-90, 90, 90, 450],
           'zw31': [-50, -45, 45, 60],
           'zw32': [-50, -45, 161, 171],
           'zw33': [-50, -45, 279, 289],
           }


def check_xrayDataset(dset, var_list):
    """Check xray.Dataset for data format compliance.
    
    Args:
      dset (xray.Dataset)
      vars (list of str): Variables to check
    
    """
    
    var_list = uconv.single2list(var_list)
    for var in var_list:
    
        # Variable attributes
        assert 'units' in dset[var].attrs.keys(), \
        "variable must have a units attribute"
    
        assert 'long_name' in dset[var].attrs.keys(), \
        "variable must have a long_name attribute"
    
        assert len(dset[var].attrs['long_name'].split(' ')) == 1, \
        "long_name must have no spaces" # Iris plotting library requires this
    
        # Axis names and order
        accepted_dims = ['time', 'latitude', 'longitude', 'level']
        for dim_name in dset[var].dims:
            assert dim_name in accepted_dims, \
            "accepted dimension names are %s" %(" ".join(accepted_dims))

        correct_order = []
        for dim_name in accepted_dims:
            if dim_name in dset[var].dims:
                correct_order.append(dim_name)
    
        if dset[var].dims != tuple(correct_order):
            print 'swapping dimension order...'
            dset[var] = dset[var].transpose(*correct_order)
        
    # Axis values 
    if 'latitude' in dset.keys():
        lat_values = dset['latitude'].values
        
        assert lat_values[0] <= lat_values[-1], \
        'Latitude axis must be in ascending order'
        
    if 'longitude' in dset.keys():
        lon_values = dset['longitude'].values
    
        assert lon_values[0] <= lon_values[-1], \
        'Longitude axis must be in ascending order'
    
        assert 0 <= lon_values.max() <= 360, \
        'Longitude axis must be 0 to 360E'

        assert 0 <= lon_values.min() <= 360, \
        'Longitude axis must be 0 to 360E'


def get_cmip5_file_details(cube):
    """Extract model, experiment and run information from CMIP5 file attributes.

    Args:
      cube (iris.cube.Cube): Data cube containing standard CMIP5 global attributes

    """

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']

    physics = cube.attributes['physics_version']
    realization = cube.attributes['realization']
    initialization = cube.attributes['initialization_method']

    run = 'r'+str(realization)+'i'+str(initialization)+'p'+str(physics)    

    # To get same information from a file name...
    #name = filename.split('/')[-1]
    #components = name.split('_')
    #model, experiment, run = components[2:5]

    return model, experiment, run


def get_subset_kwargs(namespace):
    """Get keyword arguments for xray subsetting.
    
    namespace is usually generated by argparse at the beginning of a script.

    Args:
      namespace (argparse.Namespace) 
    
    """

    kwarg_dict = {}
    try:
        south_lat, north_lat, west_lon, east_lon = regions[namespace.region]
        kwarg_dict['latitude'] = slice(south_lat, north_lat)
	kwarg_dict['longitude'] = slice(west_lon, east_lon)
    except AttributeError:
        pass 

    for dim in ['time', 'latitude', 'longitude']:
        kwarg_dict = _sel_or_slice(namespace, dim, kwarg_dict)

    return kwarg_dict


def get_time_constraint(time_list):
    """Get the time constraint used for reading an iris cube."""
    
    start_date, end_date = time_list

    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    assert re.search(date_pattern, start_date)
    assert re.search(date_pattern, end_date)

    if (start_date == end_date):
        year, month, day = start_date.split('-')    
        time_constraint = iris.Constraint(time=iris.time.PartialDateTime(year=int(year), month=int(month), day=int(day)))
    else:  
        start_year, start_month, start_day = start_date.split('-') 
        end_year, end_month, end_day = end_date.split('-')
        time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)) <= t.point <= iris.time.PartialDateTime(year=int(end_year), month=int(end_month), day=int(end_day)))

    return time_constraint

    
def get_timescale(times):
    """Get the timescale.
    
    Args:
      times (list/tuple): Tuple containing two or more numpy.datetime64 instances. 
        The difference between them is used to determine the timescale. 

    """

    diff = times[1] - times[0]

    thresholds = {'yearly': numpy.timedelta64(365, 'D'),
                  'monthly': numpy.timedelta64(27, 'D'),
                  'daily': numpy.timedelta64(1, 'D'),
                  '12hourly': numpy.timedelta64(12, 'h'),
                  '6hourly': numpy.timedelta64(6, 'h'),
                  'hourly': numpy.timedelta64(1, 'h')}
    
    timescale = None
    scales = ['yearly', 'monthly', 'daily', '12hourly', '6hourly', 'hourly']
    for key in scales:
        if diff >= thresholds[key]:
            timescale = key
            break
    
    if not timescale:
        print 'Invalid timescale data.'
        print 'Must be between hourly and yearly.'
        sys.exit(1)

    print timescale

    return timescale


def get_timestamp():
    """Return a time stamp that includes the command line entry."""
    
    time_stamp = """%s: %s %s (Git hash: %s)""" %(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 
                                                  sys.executable, 
                                                  " ".join(sys.argv), 
                                                  MODULE_HASH[0:7])

    return time_stamp


def iris_vertical_constraint(min_depth, max_depth):
    """Define vertical constraint for iris cube loading."""
    
    if min_depth and max_depth:
        level_subset = lambda cell: min_depth <= cell <= max_depth
        level_constraint = iris.Constraint(depth=level_subset)
    elif max_depth:
        level_subset = lambda cell: cell <= max_depth
        level_constraint = iris.Constraint(depth=level_subset)
    elif min_depth:
        level_subset = lambda cell: cell >= min_depth    
        level_constraint = iris.Constraint(depth=level_subset)
    else:
        level_constraint = iris.Constraint()
    
    return level_constraint


def read_dates(infile):
    """Read a file of dates (one per line) and write to a list.

    Assumes there is a metadata file corresponding to infile which 
    has exactly the same name but ends with .met

    """
    
    fin = open(infile, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()

    file_body = infile.split('.')[0]
    with open (file_body+'.met', 'r') as metfile:
        date_metadata=metfile.read()

    return date_list, date_metadata


def salinity_unit_check(cube):
    """Check CMIP5 salinity units.

    Most modeling groups store their salinity data
    in units of g/kg (typically ranging from 5 to 45 g/kg)
    and label that unit "psu" (which iris doesn't 
    recognise and converts to unknown).

    Some random data files in some runs have some stored 
    with units of kg/kg and the unit is labelled 1.

    This function converts to g/kg and unknown.

    Args:
      cube (iris.cube.Cube) 

    """

    if cube.units == '1':
        cube.data = cube.data * 1000

    data_max = cube.data.max()
    data_min = cube.data.min()
    
    assert data_max < 75.0, 'Data max is %f' %(data_max)
    assert data_min > 0.0 , 'Data min is %f' %(data_min)

    cube.units = 'g/kg'   #cf_units.Unit('unknown')

    return cube


def _sel_or_slice(inargs, dim, kw_dict):
    """Select or slice."""

    try:
        in_dim = eval('inargs.'+dim)
        if type(in_dim) in (float, int):        
            kw_dict[dim] = in_dim
        else:
            start, end = in_dim
            if start == end:
                kw_dict[dim] = start
            else:
                kw_dict[dim] = slice(start, end)
    except AttributeError:
        pass

    return kw_dict


def set_dim_atts(dset_out, time_units):
    """Set dimension attributes.
    
    Used when writing a new file using xray when the data
    was originally an iris cube.
    
    """
    
    dset_out['time'].attrs = {'calendar': 'standard', 
                              'long_name': 'time',
                              'units': time_units,
                              'axis': 'T'}
    dset_out['latitude'].attrs = {'standard_name': 'latitude',
                                  'long_name': 'latitude',
                                  'units': 'degrees_north',
                                  'axis': 'Y'}
    dset_out['longitude'].attrs = {'standard_name': 'longitude',
                                   'long_name': 'longitude',
                                   'units': 'degrees_east',
                                   'axis': 'X'}
    
    return dset_out


def set_global_atts(dset, dset_template, hist_dict):
    """Update the global attributes of an xray.DataArray.
    
    Args:
      dset (xray.DataArray): DataArray that needs updating
      dset_template (dict): Template global attributes
      hist_dict (dict): History atts from each input file
        (keys = filename, values = history attribute)
    
    """
    
    dset.attrs = dset_template
    
    if 'calendar' in dset.attrs.keys():
        del dset.attrs['calendar']  # Iris does not like it

    dset.attrs['history'] = write_metadata(file_info=hist_dict)


def set_outfile_date(outfile, new_date):
    """Take an outfile name and replace the existing date
    (in YYYY-MM-DD format) with new_date."""

    new_dt = parser.parse(str(new_date))
    
    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    assert re.search(date_pattern, outfile), \
    """Output file must contain the date of the final timestep in the format YYYY-MM-DD"""
    
    return re.sub(r'([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', new_dt.strftime("%Y-%m-%d"), outfile)


def standard_datetime(dt):
    """Take any arbitrarty date/time and convert to the standard
    I use for all outputs: YYYY-MM-DD."""

    new_dt = parser.parse(str(dt))

    return new_dt.strftime("%Y-%m-%d")


def vertical_bounds_text(level_axis, user_top, user_bottom):
    """Generate text describing the vertical bounds of a data selection."""
    
    if user_top and user_bottom:
        level_text = '%f down to %f' %(user_top, user_bottom)
    elif user_bottom:
        level_text = 'input data surface (%f) down to %f' %(level_axis[0], user_bottom)
    elif user_top:
        level_text = '%f down to input data bottom (%f)' %(user_top, level_axis[-1])
    else:
        level_text = 'full depth of input data (%f down to %f)' %(level_axis[0], level_axis[-1])
    
    return level_text


def write_dates(outfile, date_list):
    """Write a list of dates to file."""
    
    fout = open(outfile, 'w')
    for date in date_list:
        fout.write(str(date)+'\n')
    fout.close()


def write_metadata(ofile=None, file_info=None, extra_notes=None):
    """Write a metadata output file.
    
    Args:
      ofile (str, optional): Name of output file that we want to create a .met file 
        alongside (i.e. new file with .met extension will be created)
      file_info (dict, optional): A dictionary where keys are filenames and values are 
        the global attribute history
      extra_notes (list, optional): List containing character strings of extra information 
        (output is one list item per line)
      
    """
    
    result = ''
        
    # Write the timestamp
    time_stamp = get_timestamp()
    result += time_stamp + '\n'
    
    # Write the extra info
    if extra_notes:
        result += 'Extra notes: \n'
        for line in extra_notes:
            result += line + '\n'
    
    # Write the file details
    if file_info:
        assert type(file_info) == dict
        nfiles = len(file_info.keys())
        for fname, history in file_info.iteritems():
            if nfiles > 1:
                result += 'History of %s: \n %s \n' %(fname, history)
            else:
                result += '%s \n' %(history)
    
    # Create outfile or return string
    if ofile:
        fname, extension = ofile.split('.')
        fout = open(fname+'.met', 'w')
        fout.write(result) 
        fout.close()
    else:
        return result
