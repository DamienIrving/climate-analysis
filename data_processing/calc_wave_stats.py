"""
Filename:     calc_wave_stats.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calcuates statistics for wave envelope data 
              presented in Hovmoller format (time, longitude)

"""

import sys
import os

import argparse
import numpy
import csv

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio
    

def extent_stats(data_double, lons_double, threshold, lon_spacing):
    """Return key statistics regarding the extent"""
    
    lons_filtered = lons_double[data_double > threshold]
    if len(lons_filtered) == 0:
        start_lon, end_lon, extent = 0.0, 0.0, 0.0
    elif len(lons_filtered) == len(lons_double):
        start_lon, end_lon, extent = 0.0, lons_double[-1], len(lons_double) / 2
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
    
    return start_lon, end_lon, extent


def amp_stats(data_double, lons_double, start_lon, end_lon):
    """Return key statistics regarding the amplitude"""
    
    if start_lon == end_lon:
        amp_mean, amp_max, amp_max_lon = 0.0, 0.0, 0.0
    else:
	start_index = numpy.where(lons_double == start_lon)[0][0]
	end_indexes = numpy.where(lons_double == end_lon)[0]
	assert len(end_indexes) == 2, \
	'There should be two matches in lons_double'
	if end_indexes[0] > start_index:
	    end_index = end_indexes[0]
	else:
	    end_index = end_indexes[1]

	data_selection = data_double[start_index: end_index + 1]

	amp_mean = numpy.mean(data_selection)
	amp_max = numpy.max(data_selection)
	amp_max_index = numpy.where(data_double == amp_max)[0][0]
	amp_max_lon = lons_double[amp_max_index]
    
    return amp_mean, amp_max, amp_max_lon

	
def main(inargs):
    """Run the program."""

    # Read data and check inputs #

    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time',]))
    
    assert indata.data.getOrder() == 'tx', \
    'Data must be time, longitude'
    
    times = indata.data.getTime().asComponentTime()
    lons = indata.data.getLongitude()[:]
    lon_spacing = numpy.unique(numpy.diff(lons))
    
    assert len(lon_spacing) == 1, \
    'Must be a uniformly spaced longitude axis' 
    
    # Duplicate input data to cater for extents that straddle the Greenwich meridian #
    
    data_double = numpy.append(indata.data, indata.data, axis=1)
    lons_double = numpy.append(lons, lons)
    
    # Loop through every timestep, writing the statistics to file # 
    
    time_stamp = gio.get_timestamp()
    ntime = indata.data.shape[0] 
    with open(inargs.outfile, 'wb') as ofile:
        output = csv.writer(ofile, delimiter=',')
	output.writerow([time_stamp])
        output.writerow(['date', 'start-lon', 'end-lon', 'extent', 'amp-mean', 'amp-max', 'amp-max-lon'])
        for i in range(0, ntime):
            start_lon, end_lon, extent = extent_stats(data_double[i, :], lons_double, inargs.threshold, lon_spacing)
            amp_mean, amp_max, amp_max_lon = amp_stats(data_double[i, :], lons_double, start_lon, end_lon)
            
	    # Write result to file
	    date = str(times[i]).split(' ')[0]
            output.writerow([date, start_lon, end_lon, extent, amp_mean, amp_max, amp_max_lon])
 

if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.3.0/bin/cdat calc_wave_stats.py 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/env-w234-va_Merra_250hPa_30day-runmean_r360x181-hov-lat70S40S.nc 
  env 7 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/zw3-stats_Merra_250hPa_30day-runmean_r360x181-hov-lat70S40S_env-w234-va-threshold7.csv

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Calculate statistics for wave envelope data presented in Hovmoller format (time, longitude)'
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
