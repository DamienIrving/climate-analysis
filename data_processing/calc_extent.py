
def find_longest_extent(data, threshold):
    """Return details on the longest extent at each timestep"""
    
    assert data.getOrder() == 'tx', \
    'Data must be time, longitude'
    
    # Check that the longitude axis is regular
    lons = data.getLongitude()[:]
    lon_spacing = numpy.unique(numpy.diff(lons))
    assert len(lon_spacing) == 1, \
    'Must be a uniformly spaced longitude axis' 
    
    # Duplicate input data to cater for extents that straddle the Greenwich meridian
    data_double = numpy.append(data, data, axis=1)
    lons_double = numpy.append(lons, lons)
    
    # Loop through every timestep 
    
    ntime = data.shape[0] 
    for i in range(0, ntime):
        lons_filtered = lons_double[data_double[i, :] > threshold]
	diffs = numpy.diff(lons_filtered)
        diffs_corrected = numpy.where(diffs < 0, diffs + 360, diffs)
	
	extent_list = numpy.split(lons_filtered, numpy.where(diffs_corrected > lon_spacing)[0] + 1)
	final_extent = [] 
	for extent in extent_list:
	    
	    
	
    
    
    

    
