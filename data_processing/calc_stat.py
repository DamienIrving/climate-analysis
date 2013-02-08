#!/usr/bin/env cdat

"""
SVN INFO: $Id$
Filename:     calc_stat.py
Author:       Damien Irving
Description:  Calculates a number of commonly used statistics
              in climate science

Input:        List of two files to compare
Output:       File containing the statistic of interest


Updates | By | Description
--------+----+------------
30 Jan 2013 | Damien Irving | Initial version.


"""

__version__= '$Revision$'


### Import required modules ###

import sys
import os

from optparse import OptionParser
from datetime import datetime

import numpy
import genutil

module_dir = os.path.join(os.environ['HOME'],'modules')
sys.path.insert(0,module_dir)
import netcdf_io


def temporal_axis_check(data1, data2):
    """Check whether the input data are on the same axis"""
    
    # Ensure that both data have the same time axis #

    assert len(data1.getTime()) > 1.0
    assert len(data1.getTime()) == len(data2.getTime())    

    data1_hasspatial = 'yx' in data1.getOrder()
    data2_hasspatial = 'yx' in data2.getOrder()

    if data1_hasspatial and 'yx' in data2_hasspatial:
        assert len(data1.getLatitude()) == len(data2.getLatitude())
        assert len(data1.getLongitude()) == len(data2.getLongitude())

    return data1_hasspatial, data2_hasspatial


def temporal_corr(data1, data2):
    """Temporal correlation.
    
    Comparison can be between data of order:
    * tyx vs. tyx
    * tyx vs. t
    * t vs. tyx

    """
    
    data1_hasspat, data2_hasspat = temporal_axis_check(data1, data2)

    primary_data, secondary_data = data2, data1 if (data2_hasspat 
                                   and not data1_hasspat) else data1, data2

    if (data1_hasspat + data2_hasspat) >= 1:
        output_axes = (primary_data.getTime(),
                       primary_data.getLatitude(),
                       primary_Data.getLongitude(),)
        nlats = len(primary_data.getLatitude())
        nlons = len(primary_data.getLongitude())
        tempcorr = numpy.zeros((nlats,nlons))
    
	for y in range(0,nlats):
	    for x in range(0,nlons):	
		input1 = primary_data[:, y, x].compressed()
                input2 = secondary_data[:, y, x].compressed() if (data1_hasspat 
                         + data2_hasspat) == 2 else secondary_data[:]
                
                if len(input1) == 0.0 or len(input2) == 0.0:
	            tempcorr[ii,hh] = 1e20
		else:
	            tempcorr[ii,hh] = genutil.statistics.correlation(input1,
                                      input2, centered=1, biased=1)

    else:
        output_axes = primary_data.getTime()       
        tempcorr = genutil.statistics.correlation(primary_data, 
                   secondary_data, centered=1, biased=1)
    
    attributes = {'id': 'tempcorr',
                  'long_name': 'temporal correlation',
                  'units': '',
                  'missing_value': 1e20, 
                  'history': 'genutil.statistics.correlation(centered=1, biased=1)'
                 }
                  

    return tempcorr, output_axes, attributes
    

def main(metric, infile1, var1, infile2, var2, outfile, **selection):
    """Run the program."""
    
    ## Read input data from both input files ##

    indata1 = netcdf_io.InputData(infile1, var1, **selection)
    indata2 = netcdf_io.InputData(infile2, var2, **selection)

    ## Calulcate the statistic

    function_for_metric = {'tempcorr': tempcorr}
    
    calc_stat = function_for_metric[metric]
    stat, axes, atts = calc_stat(indata1, indata2)

    ## Write the output file ##
 
    netcdf_io.write_netcdf(outfile, metric, (indata1, indata2), (stat,), 
                          (atts,), axes, clear_axes=True)   


 
if __name__ == '__main__':
    
    ## Help and manual information ##

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-M","--manual",action="store_true",dest="manual",default=False,
                      help="output a detailed description of the program")
    parser.add_option("-r", "--region",dest='region',default=False,
                      help="spatial region selector")
    parser.add_option("-t", "--time",dest='time',default=False,
                      help="time period selector")
    parser.add_option("-a", "--agg", dest='agg', default=None,
                      help="temporal aggregation selector")


    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 5:
	print """
	Usage:
            temporal_metrics.py [-M] {metric} {input_file1} {variable1} {input_file2} {variable2} {output_file}

	Options:
            -M or --manual      Display this on-line manual page and exit
            -h or --help        Display a help/usage message and exit
	    -r or --region      Spatial region over which to calculate statistic [default = entire]
	    -t or --time        Time period selector [default = entire]. Tuple: (start_date, end_date)
            -a or --agg         Temporal aggregation selector [default = None]. Tuple: (season, climatology)
	    
	Input arguments:
	    {metric}            Temporal correlation ('tempcorr')
	    {climatology}       True/False
            {season}            
                    
	Description:
            Python script to calculate a number of commonly used statistics.

	Author:
            Damien Irving, Feb 2013.

	Bugs:
            Please report any problems to: Damien.Irving@csiro.au
	"""
	sys.exit(0)

    else:
    
	##Read the input data and repeat back to user #

	print 'Metric: ', args[0]
	print 'Input file 1: ', args[1]
	print 'Variable: ', args[2]
	print 'Input file 2: ', args[3]
	print 'Variable: ', args[4]
	print 'Output file: ', args[5]

	# Remove empty options #

	for key in options:
            if not options[key]:    
        	del options[key]


	main(args[0], args[1], args[2], args[3], args[4], args[5], options)
