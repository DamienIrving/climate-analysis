"""
Collection of commonly used classes, functions and global variables
for reading/writing variables to a netCDF file

To import:
module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)

Included functions:
convert_units        -- Convert units
coordinate_pairs     -- Produce all lat/lon pairs for a given grid
dict_filter          -- Filter dictionary 
get_datetime         -- Return datetime instances for list of dates/times
hi_lo                -- Update highest and lowest value
list_kwargs          -- List keyword arguments of a function
regrid_uniform       -- Regrid data to a uniform output grid
running_average      -- Calculate running average
scale_offset         -- Apply scaling and offset factors
single2list          -- Check if item is a list, then convert if not
temporal_aggregation -- Create a temporal aggregate of 
                        the input data (i.e. raw, climatology or anomaly)
time_axis_check      -- Check whether 2 time axes are the same
write_netcdf         -- Write an output netCDF file
xy_axis_check        -- Check whether 2 lat or lon axes are the same

Included classes:
InputData            -- Extract and subset data

"""

__author__ = 'Damien Irving'

import os
import sys
import re
import copy

import inspect
import calendar
import datetime
from dateutil.parser import *

import numpy
from scipy import stats

import cdutil
import genutil
import cdms2
#if hasattr(cdms2, 'setNetcdfDeflateFlag'):
cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)
import MV2
import regrid2

from git import Repo
REPO_DIR = os.path.join(os.environ['HOME'], 'git_repo', 'phd')
MODULE_HASH = Repo(REPO_DIR).head.commit.hexsha

## Alternative provenance tracking, if netcdf_io.py 
#  was under version control directly ##
#repo_dir = os.path.abspath(os.path.dirname(__file__))
#MODULE_HASH = Repo(repo_dir).head.commit.hexsha

import pdb

## Define regions ##

# The 3rd argument here works as follows:
# - First two letters: 'c' or 'o' for closed or open upper/loweer bounds
# - Third letter represents the search method: 
#   'b' bounds, 'n' node, 'e' extranode, 's' select

# [(minlat, maxlat), (minlon, maxlon)]

regions = {'aus': [(-45, -10, 'cc'), (110, 160, 'cc')],
           'ausnz': [(-50, 0, 'cc'), (100, 185, 'cc')],
           'emia': [(-10, 10, 'cc'), (165, 220, 'cc')],
           'emib': [(-15, 5, 'cc'), (250, 290, 'cc')],
           'emic': [(-10, 20, 'cc'), (125, 145, 'cc')],
           'eqpacific': [(-30, 30, 'cc'), (120, 280, 'cc')],
           'nino1': [(-10, -5, 'cc'), (270,280,'cc')],
           'nino2': [(-5, 0, 'cc'), (270, 280, 'cc')],
           'nino12': [(-10, 0, 'cc'), (270, 280, 'cc')],
           'nino3': [(-5, 5, 'cc'), (210, 270, 'cc')],
           'nino34': [(-5, 5, 'cc'), (190, 240, 'cc')],
           'nino4': [(-5, 5, 'cc'), (160, 210, 'cc')],
           'sh': [(-90, 0, 'cc'), (0, 360, 'cc')],
           'shextropics': [(-90, -30, 'cc'), (0, 360, 'cc')],
           'tropics': [(-30, 30, 'cc'), (0, 360, 'cc')],
           'greenwich': [(-90, 90, 'cc'), (-180, 180, 'cc')],
	   'glatt': [(20, 80, 'cc'), (-180, 180, 'cc')],
           'dateline': [(-90, 90, 'cc'), (0, 360, 'cc')],
           'nonpolar70': [(-70, 70, 'cc'), (0, 360, 'cc')],
	   'nonpolar80': [(-80, 80, 'cc'), (0, 360, 'cc')]
           }


## Classes/functions ##

class InputData:
    """Extract and subset data."""

    def __init__(self, fname, var_id, convert=False, **kwargs):
	"""Extract desired data from an input file.
	
	Keyword arguments (with examples):
	
	SUBSETTORS
        latitude  -- (-30, 30)
        level     -- (1000.)
        longitude -- (120, 165)
        region    -- aus
        time      -- ('1979-01-01', '2000-12-31', 'MONTH/SEASON'), 
		     MONTH/SEASON (optional 3rd argument): 
                     'JAN', 'FEB', ..., 'DEC'
		     'DJF', ... 'SON'	

	MANIPULATORS
	agg       -- (quantity, season, lower_time_bound, upper_time_bound)
                     quantity: 'raw', 'climatology' or 'anomaly'
                     season: ANNUALCYCLE, SEASONALCYCLE, DJF, MJJASO etc
                     time_bounds (optional):
                     e.g. '1979-01-01', '1980-12-31'
        convert   -- True or False (for converting units)
        grid      -- (startLat,nlat,deltaLat,
	              startLon,nlon,deltaLon)
        runave    -- window size for the running average 

        The order of operations is as follows: subset data,
        temporal aggregation (agg), running average (runave),
        regrid (grid), convert units 
       		
        self.data has all the attributes and methods
	of a typical cdms2 variable. For instance:
        - self.data.getLatitude()
	- self.data.getLatitude()
	- self.data.getTime()
	- self.data.attributes (dictionary incl. _FillValue, units etc)       
	
        """

        infile = cdms2.open(fname)       	
        _infile_attribute_check(infile, var_id)
        kwargs['order'] = _define_order(infile, var_id)

        # Subset input data #

        if kwargs.has_key('region'):   
            try:
                kwargs['latitude'], kwargs['longitude'] = regions[kwargs['region']]
                self.minlat, self.maxlat = kwargs['latitude'][0:2]
                self.minlon, self.maxlon = kwargs['longitude'][0:2]
                self.region = kwargs['region']
	    except KeyError:
                print 'region not defined - using all spatial data...'    
	    del kwargs['region']

        #remove None values
        for key in kwargs:
            if not kwargs[key]:
	        del kwargs[key]

        subsettors = ['latitude', 'level', 'longitude', 'time']
        subset_kwargs = {}
        for key in kwargs.keys():
            if key in subsettors:
                subset_kwargs[key] = kwargs[key]

        data = _subset_data(infile, var_id, **subset_kwargs)        
       
        # Manipulate the subsetted data #  

	if kwargs.has_key('agg'):
            quantity = kwargs['agg'][0]
	    timescale = kwargs['agg'][1]
            times = [kwargs['agg'][2], kwargs['agg'][3]] if len(kwargs['agg']) > 2 else None
            data = temporal_aggregation(data, timescale, quantity, time_period=times)

        if kwargs.has_key('runave'):
            data = running_average(data, window) if window > 1 else data

        if kwargs.has_key('grid'):
            data = regrid_uniform(data, kwargs['grid'])            

        if convert:
	    data = convert_units(data)

        # Set object attributes #

        self.data = data
	self.fname = fname
	self.id = var_id
	self.global_atts = infile.attributes
	
	infile.close()
    

    def datetime_axis(self):
        """Return the time axis, expressed as a list of datetime objects."""
     
        return get_datetime(self.data.getTime().asComponentTime())
        

    def months(self):
        """Return array containing the months"""        
 
        datetimes = self.data.getTime().asComponentTime()
        
        months = []
	for datetime in datetimes:
	    months.append(int(str(datetime).split('-')[1]))    

        return months


    def picker(self, **kwargs):
        """Select data based on non-contiguous axis values.
	
	Keyword arguments (with examples)
	latitude  -- (-30, -15, 5, 30)
        level     -- (1000.)
        longitude -- (120, 165, 190)
        time      -- ('1979-01', '1983-02', '2000-12-31', )
		     
        """

        pick = genutil.picker(**kwargs)
        
        return self.data(pick)


    def years(self):
        """Return array containing the years"""        
 
        datetimes = self.data.getTime().asComponentTime()
        
        years = []
	for datetime in datetimes:
            years.append(int(str(datetime).split('-')[0]))
	        
        return years


    def temporal_composite(self, index, 
                           method=None, limit=1.0, bound='upper', season=None, average=False,
			   normalise=False, remove_ave=False):
        """Extract composite from data, based on the time axis.
	
	Positional arguments:
	  index      --  a cdms2.tvariable.TransientVariable instance
	                 respresenting a data timeseries 
	  method     --  method for determining the composite threshold
	  limit      --  value applied to that method (e.g. 1.0 standard
	                 deviations)
          bound      --  indicates what type of bound the limit is
          average    --  collect up all the composite members in this category
                         and calculate the mean 
          normalise  --	 normalise the data before calculating the composite	     
	  remove_ave --  remove average in the normalisation procedure
	
        """
	
	assert isinstance(index, cdms2.tvariable.TransientVariable)
	assert method in [None, 'std']
        assert type(limit) == float
	assert season in [None, 'ann', 'djf', 'mam', 'jja', 'son']
        assert bound in ['upper', 'lower', 'between']

        # Check that the input data and index have the same time axis #

        time_axis_check(self.data.getTime(), index.getTime())
	
	# Normalise the input data #
	
	if normalise:
	    data_complete = normalise_data(self.data, sub_mean=remove_ave)
	else:
	    data_complete = self.data

        # Extract the season #

        if season == 'ann':
            season = None

        if season:
            seasons = {'djf': [12, 1, 2],
                       'mam': [3, 4, 5],
                       'jja': [6, 7, 8],
                       'son': [9, 10, 11]}
            indices0 = numpy.where(numpy.array(self.months()) == seasons[season][0], 1, 0)
            indices1 = numpy.where(numpy.array(self.months()) == seasons[season][1], 1, 0)
            indices2 = numpy.where(numpy.array(self.months()) == seasons[season][2], 1, 0)
            indices = numpy.nonzero((indices0 + indices1 + indices2) == 1)
            data_season = temporal_extract(data_complete, indices)
	    index = temporal_extract(index, indices)
	else:
	    data_season = data_complete

        # Extract the data that pass the threshold #

        if method == 'std':
            threshold = genutil.statistics.std(index) * limit
        else:
            threshold = limit 

        tests = {'upper': 'index > threshold',
                 'lower': 'index < threshold',
                 'between': '-threshold < index < threshold'}

        indices_include = numpy.nonzero(numpy.where(eval(tests[bound]), 1, 0) == 1)
        indices_exclude = numpy.nonzero(numpy.where(eval(tests[bound]), 1, 0) == 0)
        data_in_composite = temporal_extract(data_season, indices_include)
        data_out_composite = temporal_extract(data_season, indices_exclude)
        
        # Perform the t-test 
	# To perform a Welch's t-test (two independent samples, unequal variances), need the 
        # latest version of scipy in order to use the equal_var keyword argument
	
	t, p_vals = stats.ttest_ind(data_in_composite, data_out_composite, axis=0) #equal_var=False) 

        # Perform necessary averaging #

#        count = numpy.shape(composite)[0]
#        
#        final_composite = MV2.average(composite, axis=0) if average else composite
#        final_composite.count = count

        return data_in_composite, p_vals


#    def eddy
#    def mask


def convert_units(data):
    """Convert units.
        
    kg m-2 s-1 or K will be converted to 
    mm/day or Celsius.

    Arguments:
    data -- InputData instance or cdms2 transient variable
            (i.e. must have a 'units' attribute)

    """
    #There would be scope to use the genutil udunits module
    #here, however I couldn't figure out how to get it to
    #do the rainfall conversion, plus then all file variables
    #would need to have unidata udunits consistent units
    
    # Switch units #
    
    if data.units[0:10] == 'kg m-2 s-1':
        newdata = MV2.multiply(data, 86400.0)
        newdata.units = 'mm d-1'
    
    elif data.units[0] == 'K':
        newdata = MV2.subtract(data, 273.16)
        newdata.units = 'Celsius'
    
    else:
        print 'Original units not recognised.'
        print 'Units have not been converted.'

        newdata = data


    return newdata 


def coordinate_pairs(lat_axis, lon_axis):
    """Take the latitude and longitude values from given grid axes
    and produce a flattened lat and lon array, with element-wise pairs 
    corresponding to every grid point.
    
    """
    
    lon_mesh, lat_mesh = numpy.meshgrid(lon_axis, lat_axis)  # This is the correct order
    
    return lat_mesh.flatten(), lon_mesh.flatten()
    

def _define_order(infile, var_id, template='tyxz'):
    """Take an input file and output the desired order,
    according to the template.

    e.g. for (lat, lon) input data, output = 'yx'
         for (time, lon) input data, output = 'tx'
    """

    assert type(infile) == cdms2.dataset.CdmsFile
     
    input_order = ''
    for dimension in infile.listdimension(vname=var_id):
	if not dimension in ['bound', 'nv']:
	    input_order = input_order + infile.getAxis(dimension).axis.lower()

    order = copy.deepcopy(template)
    for item in template:
        if not item in input_order:
            order = order.replace(item, '')

    return order


def dict_filter(indict, key_list):
    """Filter dictionary according to specified keys."""
    
    return dict((key, value) for key, value in indict.iteritems() if key in key_list)


def get_datetime(datetime_list):
    """Return a datetime instance for a given list of dates/times.
    
    Arguments:

    times -- List values must be expressed in component time, 
             consistent with the cdat asComponentTime() method
             e.g. 1979-01-01 12:00:0.0  

    """

    assert isinstance(datetime_list, (list, tuple, str)), \
    'input argument must be a list or tuple of datetimes'

    datetime_object_list = []
    for item in datetime_list:
        #compensate for 60.0 seconds which genutil.filters.runningaverage
	#can produce
	if not str(item)[-4] in ['0', '1', '2', '3', '4', '5', ':']:
	    item = str(item)[0:-5]        
        datetime_object_list.append(parse(str(item)))

    return datetime_object_list


def _get_timescale(times):
    """Get the timescale.
    
    Arguments:
    times -- Tuple containing two datetime instances.
             The difference between them is used to 
             determine the timescale. 

    """

    diff = times[1] - times[0]

    thresholds = {'yearly': datetime.timedelta(days=365),
                  'monthly': datetime.timedelta(days=27),
                  'daily': datetime.timedelta(days=1),
                  '12hourly': datetime.timedelta(hours=12),
                  '6hourly': datetime.timedelta(hours=6),
                  'hourly': datetime.timedelta(hours=1)}
    
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


def hi_lo(data_series, current_max, current_min):
    """Determines the new highest and lowest value"""
    
    try:
       highest = MV2.max(data_series)
    except:
       highest = max(data_series)
    
    if highest > current_max:
        new_max = highest
    else:
        new_max = current_max
    
    try:    
        lowest = MV2.min(data_series)
    except:
        lowest = min(data_series)
    
    if lowest < current_min:
        new_min = lowest
    else:
        new_min = current_min
    
    return new_max, new_min


def _infile_attribute_check(infile, var_id):
    """Check for criticial attriutes in the input file"""

    assert type(infile) == cdms2.dataset.CdmsFile

    # Global file attributes #
    
    assert hasattr(infile, 'history'), \
    'Input file must have history global attribute'

    # File dimension attributes #
    
    for dimension in infile.listdimension():
	if not dimension in ['bound', 'nv']:
	    assert 'axis' in infile.getAxis(dimension).attributes.keys(), \
	    'Input dimensions must have an axis attribute that is X, Y, Z or T'

    # Variable attributes #

    var_atts = infile.listattribute(vname=var_id)
    assert 'missing_value' in var_atts, \
    'Input variable must have missing_value attribute'
    assert 'long_name' in var_atts, \
    'Input variable must have long_name attribute'
    assert 'units' in var_atts, \
    'Input variable must have units attribute'


def list_kwargs(func):
    """List keyword arguments of a function."""
    
    details = inspect.getargspec(func)
    nopt = len(details.defaults)
    
    return details.args[-nopt:]


def normalise_data(indata, sub_mean=False):
    """Normalise data.
    
    Method is (x - mean) / std,
    where removing the mean is optional
    
    """
    
    assert isinstance(indata, cdms2.tvariable.TransientVariable)
    
    if sub_mean:
        mean = cdutil.averager(indata, axis='t')
	data = indata - mean
    else:
        data = indata

    std = genutil.statistics.std(indata, axis=0)
    
    return data / std 


def regrid_uniform(data, target_grid):
    """Regrid data to a uniform output grid"""

    ingrid = data.getGrid()
    
    if isinstance(target_grid, cdms2.grid.TransientRectGrid):
        outgrid = target_grid
    else:
        assert isinstance(target_grid, (list, tuple)) and len(target_grid) == 6, \
	'Target grid must be a cdms2.grid.TransientRectGrid or list specifying: startLat, nlat, deltaLat, startLon, nlon, deltaLon'
	
	startLat, nlat, deltaLat, startLon, nlon, deltaLon = target_grid
        outgrid = cdms2.createUniformGrid(startLat, nlat, deltaLat, startLon, nlon, deltaLon)
    
    regridFunc = regrid2.Horizontal(ingrid, outgrid)
    
    return regridFunc(data)
     

def running_average(data, window):
    """Calculate running average with desired window."""

    assert type(window) == int, \
    'Window for running average must be an integer'

    run_ave = genutil.filters.runningaverage(data, window) if window > 1 else data

    return run_ave 
    

def scale_offset(data, scale=1.0, offset=0.0):
    """Apply scaling and offset factors.
    
    new_data = (old_data*scale) + offset

    """
    
    return numpy.ma.add(numpy.ma.multiply(data, float(scale)),
                        float(offset))


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


def _subset_data(infile, var_id, **kwargs):
    """Take a subset of the infile data
    
    Valid kwargs (with examples)
    
    latitude  -- (-30, 30)
    level     -- (1000.)
    longitude -- (120, 165)
    region    -- aus
    time      -- ('1979-01-01', '2000-12-31', 'MONTH/SEASON'), 
	          options: 'JAN', 'FEB', ..., 'DEC'
	                   'DJF', ... 'SON'
    """     

    assert type(infile) == cdms2.dataset.CdmsFile      
    	
    if kwargs.has_key('time'):
	assert isinstance(kwargs['time'], (list, tuple)), \
	'time selector must be a list or tuple'

	assert len(kwargs['time']) == 2 or len(kwargs['time']) == 3, \
	'time selector must be length two or three'

        date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
	assert re.search(date_pattern, kwargs['time'][0]) or kwargs['time'][0].lower() == 'none'
	assert re.search(date_pattern, kwargs['time'][1]) or kwargs['time'][1].lower() == 'none'
	valid_trange = re.search(date_pattern, kwargs['time'][0]) and re.search(date_pattern, kwargs['time'][1])

        month_dict = {'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 
		      'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8, 
        	      'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12}
        season_dict = {'DJF': ('JAN', 'FEB', 'DEC'),
		       'MAM': ('MAR', 'APR', 'MAY'),
        	       'JJA': ('JUN', 'JUL', 'AUG'),
        	       'SON': ('SEP', 'OCT', 'NOV')}
	if len(kwargs['time']) == 3 and kwargs['time'][2].lower() != 'none':
	    assert (kwargs['time'][2] in month_dict.keys()) or (kwargs['time'][2] in season_dict.keys())

	    month_selector = kwargs['time'][2]
	    date_selector = kwargs['time'][0:2]
	    del kwargs['time']

	    #make the month/season selection
            months = (month_selector,) if month_selector in month_dict.keys() else season_dict[month_selector]
            datetimes = infile.getAxis('time').asComponentTime()
            years_all = []
	    for datetime in datetimes:
        	years_all.append(int(str(datetime).split('-')[0]))
            years_unique = list(set(years_all))

            extracts = []
            for year in years_unique:
        	for month in months: 
                    start_date = str(year)+'-'+str(month_dict[month])+'-1 00:00:0.0'
                    end_date = str(year)+'-'+str(month_dict[month])+'-'+str(calendar.monthrange(year, month_dict[month])[-1])+' 23:59:0.0'
                    kwargs['time'] = (start_date, end_date)
                    try:
                	extracts.append(infile(var_id, **kwargs))
                    except cdms2.error.CDMSError:
                	continue

            data = MV2.concatenate(extracts, axis=0) if len(extracts) > 1 else extracts[0]      

	    #make the date range selection
	    if valid_trange:
		data = data(time=date_selector)

	elif valid_trange:
	    kwargs['time'] = kwargs['time'][0:2]
	    data = infile(var_id, **kwargs)

	else:
	    del kwargs['time']
	    data = infile(var_id, **kwargs)
    else:            	         
	data = infile(var_id, **kwargs)

    return data


def temporal_aggregation(data, output_timescale, output_quantity, time_period=None):
    """Create a temporal aggregate of the input data, or further process it
    to produce a climatology or anomaly timeseries.

    Arguments:
    output_timescale options: 
    - DAILY
    - SEASONALCYCLE (i.e. DJF/MAM/JJA/SON)
    - ANNUALCYCLE (i.e. JAN/FEB/MAR/.../DEC)
    - YEAR
    - DJF,MAM,JJA,SON
    - JAN,FEB,MAR,...,DEC
    - Any custom season (e.g. MJJASO, DJFM)

    output_product options: 
    - 'raw', 'climatology' or 'anomaly'
    
    time_period (for climatology used in calculating the anomaly)
    - ['lower_bound', 'upper_bound']
    e.g. ['1979-01-01', '1980-12-31']

    Reference:
    http://www2-pcmdi.llnl.gov/cdat/source/api-reference/cdutil.times.html
    """

    assert isinstance(data, cdms2.tvariable.TransientVariable)
    assert output_quantity in ['raw', 'climatology', 'anomaly']

    accepted_timescales = ['SEASONALCYCLE', 'ANNUALCYCLE', 'YEAR',
	                   'DJF', 'MAM', 'JJA', 'SON',
			   'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                           'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    double_alphabet = 'JFMAMJJASONDJFMAMJJASOND'
    assert (output_timescale in accepted_timescales) or \
           (output_timescale in double_alphabet) or \
	   (output_timescale.lower() == 'input')
   
    if time_period:
        assert len(time_period) == 2, \
        """time_period should be a list or tuple of length 2. e.g. ('1979-01-01', '1980-12-31')"""

    time_axis = data.getTime().asComponentTime()
    input_timescale = _get_timescale(get_datetime(time_axis[0:2]))
    
    if output_timescale.lower() == 'daily':
        assert output_timescale == input_timescale, \
        "For the daily output timescale, the input data must also be daily"

        outdata = _daily_aggregation(data, output_quantity, time_period)
    
    else:
	# Set time bounds #
	daily_freq = {'hourly': 24, '6hourly': 4, '12hourly': 2, 'daily': 1}
	if input_timescale in daily_freq.keys():
            cdutil.setTimeBoundsDaily(data, frequency=daily_freq[input_timescale])
	elif input_timescale == 'monthly':
            cdutil.setTimeBoundsMonthly(data)
	elif input_timescale == 'yearly':
            cdutil.setTimeBoundsYearly(data)
	else:
            print 'Unrecognised input timescale.'
            print 'Must be daily, monthly or yearly.'
            sys.exit(1)

	# Extract subset of interest #
	if output_timescale in accepted_timescales:
            season = eval('cdutil.' + output_timescale)
	elif output_timescale in double_alphabet:
            season = cdutil.times.Seasons(output_timescale)

	if output_quantity == 'raw':
            outdata = season(data)
	elif output_quantity == 'climatology':
            outdata = season.climatology(data)
	elif output_quantity == 'anomaly':
            clim = season.climatology(data(time=time_period)) if time_period else season.climatology(data)
	    assert type(clim) != type(None), \
	    'Input data are of insufficient temporal extent to calculate climatology'	
            outdata = season.departures(data, ref=clim)

	assert type(outdata) != type(None), \
	'Input data are of insufficient temporal extent to calculate the requested temporal aggregation (%s)' %(output_quantity)

    return outdata


def _daily_aggregation(data, output_quantity, time_period):
    """Create a temporal aggregate for daily data (cdat doesn't offer this
    functionality)"""

    order = data.getOrder()
    assert order == 'tyx' 

    if output_quantity == 'raw':
        return data

    # Remove Feb 29 from time axis 
    
    input_time_axis = map(str, data.getTime().asComponentTime())
    feb29_dates = [s for s in input_time_axis if '-2-29' in s]
 
    feb29_indexes = []
    for date in feb29_dates:
        feb29_indexes.append(input_time_axis.index(date))

    data_no26Feb = numpy.delete(data, feb29_indexes, axis=0)

    # Re-shape the data so the time axis is split into two (year, day)
    ntimes, nlats, nlons = data.shape
    nyears = int(math.ceil(ntimes / 365.0) * 365.0)
    days_remainder = ntimes % 365
      
    extended_data = numpy.ones([nyears, 365, nlats, nlons) * data.missing_value
    for i in range(0, nyears-1):
        start = i*nyears
        end = start + 365
        extended_data[i, :, :, :] = data[start:end, :, :] 
    extended_data[-1, 0:days_remainder, :, :] = data[end:, :, :]

    extended_data = numpy.ma.masked_values(extended_data, data.missing_value)

    # Calculate the climatology and anomaly

    daily_clim = numpy.ma.average(extended_data, axis=0)
    if output_quantity == 'climatology':
        output = daily_clim
    elif output_quantity == 'anomaly':
        
        daily_anom = numpy.ma.resize(
	    
    clim = MV2.average(data(time=time_period), axis=0) if time_period else MV2.average(data, axis=0)
    
        output = clim
    elif output_quantity == 'anomaly':
        output = data - clim

    return output
   

def temporal_extract(data, indices):
    """Extract the data corresponding to a list of time
    axis indices."""
    
    assert isinstance(data, cdms2.tvariable.TransientVariable)
    
    times = numpy.take(data.getTime().asComponentTime(), indices)
    times_str = str(times).strip('[').strip(']').split()
        
    dt_list = []
    for i in range(0, len(times_str), 2):            
        dt_list.append(times_str[i]+' '+times_str[i+1])

    pick = genutil.picker(time=dt_list)
    
    return data(pick)


def time_axis_check(axis1, axis2):
    """Checks whether the time axes of the input files are the same"""
    
    start_time1 = axis1.asComponentTime()[0]
    start_time1 = str(start_time1)
    start_year1 = start_time1.split('-')[0]
    
    end_time1 = axis1.asComponentTime()[-1]
    end_time1 = str(end_time1)
    end_year1 = end_time1.split('-')[0]
    
    start_time2 = axis2.asComponentTime()[0]
    start_time2 = str(start_time2)
    start_year2 = start_time2.split('-')[0]
    
    end_time2 = axis2.asComponentTime()[-1]
    end_time2 = str(end_time2)
    end_year2 = end_time2.split('-')[0]

    if (start_year1 != start_year2 or len(axis1) != len(axis2)):
        sys.exit('Input files do not all have the same time axis')


def write_netcdf(outfile_name, out_quantity, indata, 
                 outdata, outvar_atts, outvar_axes, 
                 clear_history=False, extra_history=' '):
    """Write an output netCDF file.
    
    Intended for use with a calculated quantity.
    Many attributes and axes are copied from the
    existing input files.
    
    All output variables must have the axes.
    
    Positional arguments (incl. type/description):
      outfile_name  -- string
      out_quantity  -- e.g. variable or statistic name
      indata        -- List or tuple of InputData instances
      outdata       -- List or tuple of numpy arrays, containing 
                       the data for each output variable
      outvar_atts   -- List or tuple of dictionaries, containing 
                       the attriubtes for each output variable
                       Suggested minumum attributes include: id, 
                       long_name, missing_value, units, history
      outvar_axes   -- List or tuple of axis lists or tuples for 
                       each outdata element (must be in order tyx)
	  	       Should be generated using the cdat getTime(),
                       getLatitude() or getLongitude() methods
                    
    Keyword arguments:
      clear_history -- True = do not append the global 'history' attribute 
                       to the corresponding attribute in the output file
      extra_history -- string of extra info to be added to the standard
                       global 'history' attribute output     

    """

    assert isinstance(indata, (list, tuple)) and isinstance(indata[0], InputData), \
    '3rd argument (indata) must be a list or tuple of InputData instances, e.g. (data,)'
    
    assert isinstance(outdata, (list, tuple)), \
    '4th argument (outdata) must be a list or tuple of data arrays, e.g. (data,)'
    
    assert isinstance(outvar_atts, (list, tuple)) and type(outvar_atts[0]) == dict, \
    '5th argument (outvar_atts) must be a list or tuple of dictionaries, e.g. (atts,)'
    
    assert isinstance(outvar_axes, (list, tuple)), \
    '6th argument (outvar_axes) must be a list or tuple of axis lists or tuples, e.g. (data.getTime(),)'
    
    for axes in outvar_axes:
	index = 0
	for axis in axes:
            test = (axis.isTime(), axis.isLatitude(), axis.isLongitude())
            assert sum(test) == 1 and test.index(1) >= index, \
            '6th argument (outvar_axes) elements must a time, latitude or longitude axis, in that order'
            index = test.index(1)
    

    outfile = cdms2.open(outfile_name, 'w')
    
    # Global attributes #
    
    infile_global_atts = indata[0].global_atts
    
    for att_name in infile_global_atts.keys():
        if att_name != "history":
            setattr(outfile, att_name, infile_global_atts[att_name])
    
    if not clear_history:
        old_history = infile_global_atts['history'] if ('history' in \
                      infile_global_atts.keys()) else ''
    else:
        old_history = ''
    
    infile_names = []
    for item in indata:
        infile_names.append(item.fname)
    
    infile_names_unique = str(set(infile_names)).strip('set([').strip('])')
        
    setattr(outfile, 'history', 
    """%s: %s calculated from %s using %s (Git hash: %s), format=NETCDF3_CLASSIC. %s\n%s""" %(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
    out_quantity, infile_names_unique, sys.argv[0], MODULE_HASH, extra_history, old_history))

    # Variables #

    nvars = len(outdata)
    for index in range(0, nvars):

        outvar_axis_list = []
        for axis in outvar_axes[index]:
            outvar_axis_list.append(outfile.copyAxis(axis))

	var = cdms2.MV2.array(outdata[index])
        var = var.astype(numpy.float32)
	var.setAxisList(outvar_axis_list)

	for key, value in outvar_atts[index].iteritems():
            setattr(var, key, value)

	outfile.write(var)  

    outfile.close()


def xy_axis_check(axis1, axis2):
    """Checks whether the lat or lon axes of the input files are the same""" 
   
    if (len(axis1) != len(axis2)):
        sys.exit('Input files do not all have the same %s axis' %(axis1.id))
