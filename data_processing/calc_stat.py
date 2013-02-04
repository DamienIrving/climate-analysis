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
module_dir = os.path.join(os.environ['HOME'],'dbirving','modules')
sys.path.insert(0,module_dir)


from optparse import OptionParser
from datetime import datetime

import cdms2 
if hasattr(cdms2, 'setNetcdfDeflateFlag'):
    cdms2.setNetcdfDeflateFlag(0)
    cdms2.setNetcdfDeflateLevelFlag(0)
    cdms2.setNetcdfShuffleFlag(0)
    
from cdms2 import MV2
import numpy
from numpy import *

import genutil



def axis_check(data1,data2):
    """Check whether the input data are on the same axis"""
    
    dims1 = numpy.shape(numpy.squeeze(data1))
    nlats1 = dims1[0]
    nlons1 = dims1[1]
    
    dims2 = numpy.shape(numpy.squeeze(data2))
    nlats2 = dims2[0]
    nlons2 = dims2[1]
    
    if (nlats1 != nlats2):
        sys.exit('Input data do not all have the same latitude axis')
    elif (nlons1 != nlons2):
        sys.exit('Input data do not all have the same longitude axis')
    else:
        return nlats1,nlons1



def tempcorr(data1_month_ave,data2_month_ave,raw,nlats,nlons):
    """Temporal correlation"""
    
    axis_check() #time axis
    
    tempcorr_data1_data2=numpy.zeros((nlats,nlons))
    for ii in range(0,nlats):
	for hh in range(0,nlons):	
	    data1=data1_month_ave[:,ii,hh]
	    data2=data2_month_ave[:,ii,hh]
	    data1=data1.compressed() 
	    data2=data2.compressed()  
	    if len(data1) == 0.0 or len(data2) == 0.0:
	        tempcorr_data1_data2[ii,hh] = 1e20
	    else:
	        tempcorr_data1_data2[ii,hh]=genutil.statistics.correlation(data1,data2,centered=1,biased=1)
    
    return tempcorr_data1_data2
    
    
    
function_for_metric = {'tempcorr': tempcorr}    
    

def main(metric, infile1, var1, infile2, var2, selection, subset):
    """Run the program.
    
    INCLUDE MORE DETAILS

    """
    
    ## Read input data from both input files ##

    indata1 = my_modules.InputData(infile1, var1, **selection)
    indata2 = my_modules.InputData(infile2, var2, **selection)
    
    if subset:
        data1 = indata1.temporal_subset(subset)
        data2 = indata2.temporal_subset(subset)
    else:
        data1 = indata1
        data2 = indata2

    ## Calulcate the statistic

    calc_stat = function_for_metric[metric]
    stat = calc_stat(data1, data2)

    ## Write the output file ##

    calc_stat.func_doc
 
    fout = cdms2.createDataset(outfile) 


 
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
    parser.add_option("-s", "--subset",dest='subset', default=False,
                      help="temporal subset selector")


    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 5:
	print """
	Usage:
            temporal_metrics.py [-M] {metric} {variable} {input_file1} {input_file2} {output_file}

	Options:
            -M or --manual      Display this on-line manual page and exit
            -h or --help        Display a help/usage message and exit
	    -r or --region      Spatial region over which to calculate statistic [default = entire]
	    -t or --times       Time period (start_date, end_date) [default = entire]
            -s or --subset      Temporal subset of the data (provide in_timescale out_timescale) [default = entire]
	    
	Input arguments:
	    {metric}            Temporal correlation ('tempcorr'); temporal standard deviation ratio ('tempstd')
	                        spatial correlation ('spatcorr'); spatial standard deviation ratio ('spatstd')
	    {in_timescale}      
                    
	Description:
            Python script to calculate a number of commonly used statistics.

	Author:
            Damien Irving, Feb 2013.

	Bugs:
            Please report any problems to: Damien.Irving@csiro.au
	"""
	sys.exit(0)


    ## Read the input data and repeat back to user ##

    print 'Metric: ', args[0]
    print 'Variable: ', args[1]
    print 'Input file 1: ', args[2]
    print 'Input file 2: ', args[3]
    print 'Output_file: ', args[4]

    # Prepare options #
    
    #Remove empty
    for key in options:
        if options[key] == False:    
            del options[key]

    select_opts = ['region', 'time']
    selection = {}
    for item in select_opts:
        if options[item]:
            selection[item] = options[item]

    main(args[0], args[1], args[2], args[3], args[4], selection, options.subset)
