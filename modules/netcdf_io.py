"""
Collection of commonly used classes, functions and global variables
for reading/writing variables to a netCDF file

To import:

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)

Included functions:
convert_units        -- Convert units
scale_offset         -- Apply scaling and offset factors
temproal_aggregation -- Create a temporal aggregate of 
                        the input data
write_netcdf         -- Write an output netCDF file

Included classes:
InputData            -- Extract and subset data

"""

__author__ = 'Damien Irving'


import sys
import datetime

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


def scale_offset(data, scale=1.0, offset=0.0):
    """Apply scaling and offset factors.
    
    new_data = (old_data*scale) + offset

    """
    
    return numpy.ma.add(numpy.ma.multiply(data, float(scale)),
                        float(offset))


def _get_datetime(times):
    """Return a datetime instance for a given list dates/times.
    
    Arguments:

    times -- List values must be expressed in component time, 
             consistent with the cdat asComponentTime() method
             e.g. 1979-01-01 12:00:0.0  

    """

    datetimes = ['','']
    for index, item in enumerate(times):
	year, month, day = str(item).split(' ')[0].split('-')
        hour, minute, second = str(item).split(' ')[1].split(':')
        
        datetimes[index] = datetime.datetime(int(year), int(month), int(day), 
	                                     int(hour), int(minute), int(float(second)))

    return datetimes


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
	             (2nd element of the tuple indicates 
                      whether the climatology is desired)
	
        self.data has all the attributes and methods
	of a typical cdms2 variable. For instance:
        - self.data.getLatitude()
	- self.data.getLatitude()
	- self.data.getTime()
	- self.data.attributes (dictionary incl. _FillValue, units etc)       
	
        """
        
        ## Read the input data to set order & check missing value ##

        infile = cdms2.open(fname)
        temp_data = infile(var_id)

        input_order = temp_data.getOrder()
        
        assert hasattr(temp_data, 'missing_value'), \
        'Input variable must have missing_value attribute'

        del temp_data
       

        ## Prepare kwargs ## 

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

        # Prepare kwargs #

        for key in kwargs:  #remove None values
            if not kwargs[key]:
	        del kwargs[key]
        
	if kwargs.has_key('agg'):
	    aggregate = kwargs['agg']
	    del kwargs['agg']
	else:
	    aggregate = False
	    

	## Set object attributes ##
	
        data = infile(var_id, **kwargs)

        if aggregate:
	    self.data = temporal_aggregation(data, aggregate[0], climatology=aggregate[1])
	else:
            self.data = data
        
	self.fname = fname
	self.id = var_id
	self.global_atts = infile.attributes
	
	infile.close()

     
    def months(self):
        """Return array containing the months"""        
 
        time = self.data.getTime().asComponentTime()
        
        months = []
	for i in range(0, len(time)):
	    months.append(int(str(time[i]).split('-')[1]))    

        return months


    def years(self):
        """Return array containing the years"""        
 
        time = self.data.getTime().asComponentTime()
        
        years = []
	for i in range(0, len(time)):
            years.append(int(str(time[i]).split('-')[0]))
	        
        return years


#    def smooth
#    def eddy


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

    # Find input timescale #
    
    time_axis = data.getTime().asComponentTime()
    input_timescale = _get_timescale(_get_datetime(time_axis[0:2]))

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
                 outdata, outvar_atts, out_axes, clear_history=False):
    """Write an output netCDF file.
    
    Intended for use with a calculated quantity.
    Many attributes and axes are copied from the
    existing input files.
    
    All output variables must have the axes.
    
    Arguments (incl. type/description):
    outfile_name -- string
    out_quantity -- e.g. variable or statistic name
    indata       -- Tuple of InputData instances
    outdata      -- Tuple of numpy arrays, containing the 
                    data for each output variable
    outvar_atts  -- Tuple of dictionaries, containing the 
                    attriubtes for each output variable.
                    Suggested minumum attributes include: id, 
                    long_name, missing_value, units, history
    out_axes     -- Tuple of the output variable axes (must 
                    be in order tyx)
                    Should get generated using the cdat getTime() 
                    getLatitide() or getLongitude() methods.
    
    """

    assert isinstance(indata, (list, tuple)) and isinstance(indata[0], InputData), \
    '3rd argument (indata) must be a list or tuple of InputData instances, e.g. (data,)'
    
    assert isinstance(outdata, (list, tuple)), \
    '4th argument (outdata) must be a list or tuple of data arrays, e.g. (data,)'
    
    assert isinstance(outvar_atts, (list, tuple)) and type(outvar_atts[0]) == dict, \
    '5th argument (outvar_atts) must be a list or tuple of dictionaries, e.g. (atts,)'
    
    assert isinstance(out_axes, (list, tuple)), \
    '6th argument (out_axes) must be a list or tuple of axis lists or tuples, e.g. (atts,)'
    
    for axes in out_axes:
        index = 0
        for axis in axes:
            test = (axis.isTime(), axis.isLatitude(), axis.isLongitude())
            assert sum(test) == 1 and test.index(1) >= index, \
            '6th argument (out_axes) elements must a time, latitude or longitude axis, in that order'
            index = index + 1
            

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
    
    infile_names = ''
    for item in indata:
        infile_names = infile_names + item.fname +', '
        
    setattr(outfile, 'history', """%s: %s calculated from %s using %s, 
            format=NETCDF3_CLASSIC\n%s""" %(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
            out_quantity, infile_names, sys.argv[0], old_history))

    # Variables #

    nvars = len(outdata)
    for index in range(0, nvars):

	axis_list = []
	for axis in out_axes[index]:
            axis_list.append(outfile.copyAxis(axis))

	var = cdms2.MV2.array(outdata[index])
	var = var.astype(numpy.float32)
	var.setAxisList(axis_list)

	for key, value in outvar_atts[index].iteritems():
            setattr(var, key, value)

	outfile.write(var)  

    outfile.close()
