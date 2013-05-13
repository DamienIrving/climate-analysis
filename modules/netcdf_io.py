"""
Collection of commonly used classes, functions and global variables
for reading/writing variables to a netCDF file

To import:
module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)

Included functions:
convert_units        -- Convert units
dict_filter          -- Filter dictionary 
get_datetime         -- Return datetime instances for list of dates/times
hi_lo                -- Update highest and lowest value
list_kwargs          -- List keyword arguments of a function
running_average      -- Calculate running average
scale_offset         -- Apply scaling and offset factors
temporal_aggregation -- Create a temporal aggregate of 
                        the input data
time_axis_check      -- Check whether 2 time axes are the same
write_netcdf         -- Write an output netCDF file
xy_axis_check        -- Check whether 2 lat or lon axes are the same

Included classes:
InputData            -- Extract and subset data

"""

__author__ = 'Damien Irving'

import os
import sys

import inspect
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
           'dateline': [(-90, 90, 'cc'), (0, 360, 'cc')]
           }


## Classes/functions ##

class InputData:
    """Extract and subset data."""

    def __init__(self, fname, var_id, convert=False, **kwargs):
	"""Extract desired data from an input file.
	
	Keyword arguments (with examples):
	grid      -- 
        latitude  -- (-30, 30)
        level     -- (1000.)
        longitude -- (120, 165)
        region    -- aus
        time      -- ('1979-01-01', '2000-12-31'), or 
                     slice(index1,index2,step)
	agg       -- ('DJF', False)
	             (i.e. aggregates the data into 
                      a timeseries of DJF values)
	             (2nd element of the tuple is 
                      optional & indicates whether the 
                      climatology is desired)
        runave    -- window size for the running average 
	convert   -- True or False (for converting units)
	
        note that the temporal aggregation will happen 
        before the running average

        self.data has all the attributes and methods
	of a typical cdms2 variable. For instance:
        - self.data.getLatitude()
	- self.data.getLatitude()
	- self.data.getTime()
	- self.data.attributes (dictionary incl. _FillValue, units etc)       
	
        """
        
        # Read the input data to set order & check critical attributes #

        infile = cdms2.open(fname)
        temp_data = infile(var_id)

        input_order = temp_data.getOrder()
        
	assert hasattr(infile, 'history'), \
        'Input file must have history global attribute'
        assert hasattr(temp_data, 'missing_value'), \
        'Input variable must have missing_value attribute'
	assert hasattr(temp_data, 'long_name'), \
        'Input variable must have long_name attribute'
	assert hasattr(temp_data, 'units'), \
        'Input variable must have units attribute'

        del temp_data

        # Sort out the order #

        order = 'tyxz'
        for item in 'tyxz':
            if not item in input_order:
                order = order.replace(item, '')
        
        kwargs['order'] = order

        # Convert region to lat/lon #

        if kwargs.has_key('region'):   
            try:
                kwargs['latitude'], kwargs['longitude'] = regions[kwargs['region']]
                self.minlat, self.maxlat = kwargs['latitude'][0:2]
                self.minlon, self.maxlon = kwargs['longitude'][0:2]
                self.region = kwargs['region']
	    except KeyError:
                print 'region not defined - using all spatial data...'
	    
	    del kwargs['region']

        # Remove None values #

        for key in kwargs:
            if not kwargs[key]:
	        del kwargs[key]
        
        # Determine aggregation method #

	if kwargs.has_key('agg'):
	    if isinstance(kwargs['agg'], (list, tuple)):
                assert len(kwargs['agg']) == 2 
                assert type(kwargs['agg'][0]) == str
                assert type(kwargs['agg'][1]) == bool
                agg, clim = kwargs['agg']    
	    else:
	        agg = str(kwargs['agg'])
                clim = False
            del kwargs['agg']
	else:
            agg = False

        # Determine the running average #

        if kwargs.has_key('runave'):
            assert type(kwargs['runave']) == int, \
            'Window for running average must be an integer'
            window = kwargs['runave']
            del kwargs['runave']
        else:
            window = None

	# Set object attributes #
	
        data = infile(var_id, **kwargs)
        
        data = temporal_aggregation(data, agg, climatology=clim) if agg else data
        data = running_average(data, window) if window > 1 else data

        if convert:
	    data = convert_units(data)

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


def running_average(data, window):
    """Calculate running average with desired window."""

    return genutil.filters.runningaverage(data, window) 
    

def scale_offset(data, scale=1.0, offset=0.0):
    """Apply scaling and offset factors.
    
    new_data = (old_data*scale) + offset

    """
    
    return numpy.ma.add(numpy.ma.multiply(data, float(scale)),
                        float(offset))


def temporal_aggregation(data, output_timescale, climatology=False):
    """Create a temporal aggregate of the input data.
    (e.g. turn a monthly timeseries into a seasonal timeseries)

    Arguments:
    output_timescale can be: 
    - SEASONALCYCLE (i.e. DJF/MAM/JJA/SON)
    - ANNUALCYCLE (i.e. JAN/FEB/MAR/.../DEC)
    - YEAR
    - DJF,MAM,JJA,SON
    - JAN,FEB,MAR,...,DEC
    - Any custom season (e.g. MJJASO, DJFM)

    Reference:
    http://www2-pcmdi.llnl.gov/cdat/source/api-reference/cdutil.times.html

    """

    ######
    #does it need to be cdutil.times?????
    #####

    # Find input timescale #
    
    time_axis = data.getTime().asComponentTime()
    input_timescale = _get_timescale(get_datetimeget(time_axis[0:2]))

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

    accepted_timescales = ['SEASONALCYCLE', 'ANNUALCYCLE', 'YEAR',
	                   'DJF', 'MAM', 'JJA', 'SON',
			   'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
                           'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    end = '.climatology(data)' if climatology else '(data)'
    if output_timescale in accepted_timescales:
	function = 'cdutil.' + output_timescale + end
        outdata = eval(function)

    elif output_timescale in 'JFMAMJJASONDJFMAMJJASOND':
        custom = cdutil.Seasons(output_timescale)
        outdata = custom(data)

    else:
        print 'Unrecognised temporal subset.'
        sys.exit(1)

    return outdata


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
    """%s: %s calculated from %s using %s (%s), format=NETCDF3_CLASSIC. %s\n%s""" %(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
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
