"""
Filename:     calc_extent.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calcuates the extent of a wave

"""

import sys
import os

import argparse
import numpy
import csv

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def find_longest_extent(data, threshold, outfile):
    """Return details on the longest extent at each timestep"""
    
    # Check inputs #
    
    assert data.getOrder() == 'tx', \
    'Data must be time, longitude'
    
    times = data.getTime().asComponentTime()
    lons = data.getLongitude()[:]
    lon_spacing = numpy.unique(numpy.diff(lons))
    assert len(lon_spacing) == 1, \
    'Must be a uniformly spaced longitude axis' 
    
    # Duplicate input data to cater for extents that straddle the Greenwich meridian #
    
    data_double = numpy.append(data, data, axis=1)
    lons_double = numpy.append(lons, lons)
    
    # Loop through every timestep # 
    
    ntime = data.shape[0] 
    with open(outfile, 'wb') as ofile:
        output = csv.writer(ofile, delimiter=',')
	output.writerow(['date', 'start-lon', 'end-lon', 'extent'])
    
        for i in range(0, ntime):
            lons_filtered = lons_double[data_double[i, :] > threshold]
	
	    # Find largest extent
	    if len(lons_filtered) == 0:
		start_lon, end_lon, extent = 0.0, 0.0, 0.0
	    elif len(lons_filtered) == len(lons_double):
	        start_lon, end_lon, extent = 0.0, lons[-1], len(lons)
	    else: 
		diffs = numpy.diff(lons_filtered)
        	diffs_corrected = numpy.where(diffs < 0, diffs + 360, diffs)
		extent_list = numpy.split(lons_filtered, numpy.where(diffs_corrected > lon_spacing)[0] + 1)
		lengths = map(len, extent_list)
        	max_length = max(lengths)
        	max_index = lengths.index(max_length)
		result = extent_list[max_index]
		start_lon = result[0]
		end_lon = result[-1]
		extent = len(result) * lon_spacing[0]

	    # Write result to file
	    date = str(times[i]).split(' ')[0]
            output.writerow([date, start_lon, end_lon, extent])
    
    
	    
	
def main(inargs):
    """Run the program."""

    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time',]))
 
    find_longest_extent(indata.data, inargs.threshold, inargs.outfile)
 
    

if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Calculate extent of waves from a hovmoller diagram'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("threshold", type=float, help="Threshold for inclusion as a wave")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")
    
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  
    
    main(args)    
