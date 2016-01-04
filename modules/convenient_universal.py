"""Collection of convenient functions that will work with my anaconda or uvcdat install.

Functions:
  adjust_lon_range   -- Express longitude values in desired 360 degree interval
  apply_lon_filter   -- Set values outside of specified longitude range to zero
  calc_significance  -- 
  coordinate_paris   -- Generate lat/lon pairs
  dict_filter        -- Filter dictionary according to specified keys
  find_nearest       -- Find the closest array item to value
  find_duplicates    -- Return list of duplicates in a list
  fix_label          -- Fix formatting of an axis label taken from the command line
  get_threshold      -- Turn the user input threshold into a numeric threshold
  hi_lo              -- Determine the new highest and lowest value.
  list_kwargs        -- List keyword arguments of a function
  match_dates        -- Take list of dates and match with the corresponding times 
                        in a detailed time axis
  single2list        -- Check if item is a list, then convert if not

"""

import numpy
from scipy import stats
import pdb, re
import inspect


def adjust_lon_range(lons, radians=True, start=0.0):
    """Express longitude values in a 360 degree (or 2*pi radians) interval.

    Args:
      lons (list/tuple): Longitude axis values (monotonically increasing)
      radians (bool): Specify whether input data are in radians (True) or
        degrees (False). Output will be the same units.
      start (float, optional): Start value for the output interval (add 360 degrees or 2*pi
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


def apply_lon_filter(data, lon_bounds):
    """Set values outside of specified longitude range to zero.

    Args:
      data (numpy.ndarray): Array of longitude values.
      lon_bounds (list/tuple): Specified longitude range (min, max)

    """
    
    # Convert to common bounds (0, 360)
    lon_min = adjust_lon_range(lon_bounds[0], radians=False, start=0.0)
    lon_max = adjust_lon_range(lon_bounds[1], radians=False, start=0.0)
    lon_axis = adjust_lon_range(data.getLongitude()[:], radians=False, start=0.0)

    # Make required values zero
    ntimes, nlats, nlons = data.shape
    lon_axis_tiled = numpy.tile(lon_axis, (ntimes, nlats, 1))
    
    new_data = numpy.where(lon_axis_tiled < lon_min, 0.0, data)
    
    return numpy.where(lon_axis_tiled > lon_max, 0.0, new_data)


def calc_significance(data_subset, data_all, standard_name):
    """Perform significance test.

    The approach for the significance test is to compare the mean of the subsetted
    data with that of the entire data sample via an independent, two-sample,
    parametric t-test (for details, see Wilks textbook). 
    
    POSSIBLE ENHANCEMENT: If equal_var=False perform a Welch t-test, which is for samples
    with unequal variance (early versions of scipy do not have this option). To test whether
    the variances are equal or not you use an F-test (i.e. do the test at each grid point and
    then assign equal_var accordingly). If your data is close to normally distributed you can 
    use the Barlett test (scipy.stats.bartlett), otherwise the Levene test (scipy.stats.levene).
    http://stackoverflow.com/questions/21494141/how-do-i-do-a-f-test-in-python
    
    POSSIBLE ENHANCEMENT: Account for autocorrelation in the data by calculating an effective
    sample size (see Wilkes, p 147). I can get the autocorrelation using either
    genutil.autocorrelation or the acf function in the statsmodels time series analysis
    python library, however I cannot see how to alter the sample size in stats.ttest_ind.

    POSSIBLE ENHANCEMENT: Consider whether a parametric t-test is appropriate. One of my samples
    might be very non-normally distributed, which means a non-parametric test might be better. 
    
    """

#    alpha = 0.05 
#    w, p_value = scipy.stats.levene(data_included, data_excluded)
#    if p_value > alpha:
#        equal_var = False# Reject the null hypothesis that Var(X) == Var(Y)
#    else:
#        equal_var = True

    t, pvals = stats.mstats.ttest_ind(data_subset, data_all, axis=0) # stats.ttest_ind has an equal_var option that mstats does not
    print 'WARNING: Significance test assumed equal variances'

    size_subset = data_subset.shape[0]
    size_all = data_all.shape[0]
    notes = "Two-tailed p-value from standard independent two sample t-test comparing the subsetted data (size=%s) to a sample containing all the data (size=%s)" %(str(size_subset), str(size_all))
    pval_atts = {'standard_name': standard_name,
                 'long_name': standard_name,
                 'units': ' ',
                 'notes': notes,}

    return pvals, pval_atts


def coordinate_pairs(lat_axis, lon_axis):
    """Take the latitude and longitude values from given grid axes
    and produce a flattened lat and lon array, with element-wise pairs 
    corresponding to every grid point."""
    
    lon_mesh, lat_mesh = numpy.meshgrid(lon_axis, lat_axis)  # This is the correct order
    
    return lat_mesh.flatten(), lon_mesh.flatten()


def dict_filter(indict, key_list):
    """Filter dictionary according to specified keys."""
    
    return dict((key, value) for key, value in indict.iteritems() if key in key_list)


def find_duplicates(inlist):
    """Return list of duplicates in a list."""
    
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    D = {k:v for k,v in D.items() if len(v)>1}
    
    return D


def find_nearest(array, value):
    """Find the closest array item to value."""
    
    idx = (numpy.abs(numpy.array(array) - value)).argmin()
    return array[idx]


def fix_label(label):
    """Fix axis label taken from the command line."""

    label = label.replace('_', ' ')
    label = label.replace('degE', '$^{\circ}$E')

    return label 


def get_threshold(data, threshold_str, axis=None):
    """Turn the user input threshold into a numeric threshold."""
    
    if 'pct' in threshold_str:
        value = float(re.sub('pct', '', threshold_str))
        threshold_float = numpy.percentile(data, value, axis=axis)
    else:
        threshold_float = float(threshold_str)
    
    return threshold_float


def hi_lo(data_series, current_max, current_min):
    """Determine the new highest and lowest value."""
    
    try:
        highest = numpy.max(data_series)
    except:
        highest = max(data_series)
    
    if highest > current_max:
        new_max = highest
    else:
        new_max = current_max
    
    try:    
        lowest = numpy.min(data_series)
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


def split_dt(dt):
    """Split a numpy.datetime64 value so as to just keep the date part."""

    return str(dt).split('T')[0]


def match_dates(datetimes, datetime_axis):
    """Take list of datetimes and match with the corresponding datetimes in a time axis.
 
    Args:   
      datetimes (list/tuple)
      datetime_axis (list/tuple)
        
    """

    dates = map(split_dt, datetimes)
    date_axis = map(split_dt, datetime_axis[:]) 
    
    match_datetimes = []
    miss_datetimes = [] 

    for i in range(0, len(datetime_axis)):
        if date_axis[i] in dates:
            match_datetimes.append(datetime_axis[i])
        else:
            miss_datetimes.append(datetime_axis[i])    

    return match_datetimes, miss_datetimes


def single2list(item, numpy_array=False):
    """Check if item is a list, then convert if not."""
    
    if type(item) == list or type(item) == tuple or type(item) == numpy.ndarray:
        output = item 
    elif type(item) == str:
        output = [item,]
    else:
        try:
            test = len(item)
        except TypeError:
            output = [item,]

    if numpy_array and not isinstance(output, numpy.ndarray):
        return numpy.array(output)
    else:
        return output
