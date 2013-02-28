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
temproal_aggregation -- Create a temporal aggregate of 
                        the input data
write_netcdf         -- Write an output netCDF file

Included classes:
InputData            -- Extract and subset data

"""

__author__ = 'Damien Irving'


import sys

import inspect
import datetime
from dateutil.parser import *

import numpy

import cdutil
import genutil
import cdms2
#if hasattr(cdms2, 'setNetcdfDeflateFlag'):
cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)


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

    def __init__(self, fname, var_id, **kwargs):
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
	
        note that the temporal aggregation will happen 
        before the running average

        self.data has all the attributes and methods
	of a typical cdms2 variable. For instance:
        - self.data.getLatitude()
	- self.data.getLatitude()
	- self.data.getTime()
	- self.data.attributes (dictionary incl. _FillValue, units etc)       
	
        """
        
        # Read the input data to set order & check missing value #

        infile = cdms2.open(fname)
        temp_data = infile(var_id)

        input_order = temp_data.getOrder()
        
        assert hasattr(temp_data, 'missing_value'), \
        'Input variable must have missing_value attribute'

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

        self.data = data
	self.fname = fname
	self.id = var_id
	self.global_atts = infile.attributes
	
	infile.close()
    

    def datetime_axis(self):
        """Return the time axis, expressed asa list of datetime objects."""
     
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


#    def eddy
#    def mask


def get_datetime(datetime_list):
    """Return a datetime instance for a given list of dates/times.
    
    Arguments:

    times -- List values must be expressed in component time, 
             consistent with the cdat asComponentTime() method
             e.g. 1979-01-01 12:00:0.0  

    """

    assert isinstance(datetime_list, (list, tuple)), \
    'input argument must be a list or tuple of datetimes'

    datetime_object_list = []
    for item in datetime_list:
        print item
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
        newdata = numpy.ma.multiply(data, 86400.0)
        newdata.units = 'mm d-1'
    
    elif data.units[0] == 'K':
        newdata = numpy.ma.subtract(data, 273.16)
        newdata.units = 'Celsius'
    
    else:
        print 'Original units not recognised.'
        print 'Units have not been converted.'

        newdata = data


    return newdata 


def dict_filter(indict, key_list):
    """Filter dictionary according to specified keys."""
    
    return dict((key, value) for key, value in indict.iteritems() if key in key_list)


def hi_lo(data_series, current_max, current_min):
    """Determines the new highest and lowest value"""
    
    if isinstance(data_series, (numpy.ndarray)):
        find_max = numpy.max
        find_min = numpy.min
    else:
        find_max = max
        find_min = min
    
    highest = find_max(data_series)
    if highest > current_max:
        new_max = highest
    else:
        new_max = current_max
        
    lowest = find_min(data_series)
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
    
    
def scale_offset(data, scale=1.0, offset=0.0):
    """Apply scaling and offset factors.
    
    new_data = (old_data*scale) + offset

    """
    
    return numpy.ma.add(numpy.ma.multiply(data, float(scale)),
                        float(offset))


def running_average(data, window):
    """Calculate running average with desired window."""

    return genutil.filters.runningaverage(data, window) 


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


def write_netcdf(outfile_name, out_quantity, indata, 
                 outdata, outvar_atts, outvar_axes, 
                 clear_history=False):
    """Write an output netCDF file.
    
    Intended for use with a calculated quantity.
    Many attributes and axes are copied from the
    existing input files.
    
    All output variables must have the axes.
    
    Arguments (incl. type/description):
    outfile_name -- string
    out_quantity -- e.g. variable or statistic name
    indata       -- List or tuple of InputData instances
    outdata      -- List or tuple of numpy arrays, containing 
                    the data for each output variable
    outvar_atts  -- List or tuple of dictionaries, containing 
                    the attriubtes for each output variable
                    Suggested minumum attributes include: id, 
                    long_name, missing_value, units, history
    outvar_axes  -- List or tuple of axis lists or tuples for 
                    each outdata element (must be in order tyx)
		    Should be generated using the cdat getTime(),
                    getLatitude() or getLongitude() methods
                    
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
    """%s: %s calculated from %s using %s, format=NETCDF3_CLASSIC\n%s""" %(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
    out_quantity, infile_names_unique, sys.argv[0], old_history))

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
