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
    
    


def unit_convert(data):
    """Convert units to mm/day and Celsius"""
    units = data.units
    if units[0:10] == 'kg m-2 s-1':
	new_data = data*86400
    elif units[0] == 'K':
        new_data = data - 273.16
    else:
        new_data = data
    
    return new_data

    
function_for_metric = {
    'tempcorr':    tempcorr,
    'tempstd':     tempstd,
    'spatcorr':    spatcorr,
    'spatstd':     spatstd,
    'bias':        bias
                      }    
    

def main(metric,var,infile1,infile2,outfile):
    """Run the program.
    """
    
    ## Initialise relevant function ##
    
    calc_stat = function_for_metric[metric]


    ## Read input data from both input files ##

    indata1 = my_modules.InputData(infile1,var)
    indata2 = my_modules.InputData(infile2,var)

    

    
    ## Make necessary modifications to the input data ##
    


    ## Calculate the temporal statistic ##

    stat = calc_stat(indata1, indata2)




    ## Write the output file ##

    fout = cdms2.createDataset(outfile) 

    # Global attributes

    global_atts = {'institution': 'CSIRO Marine and Atmospheric Research, Melbourne, Australia',
		   'contact': 'Damien Irving (irv033), damien.irving@csiro.au',
		   'title': '%s' %(calc_stat.func_doc), 
		   'created': 'Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0])
		  }

    for key, value in global_atts.iteritems():
	setattr(fout, key, value)


    if metric[0:4] == 'temp':

	# Axes

	latitude = fout.copyAxis(fin1['lat'])
	longitude = fout.copyAxis(fin1['lon'])
	axeslist = [latitude,longitude]

	# Variable

	outvar = fout.createVariable(metric,'f',axeslist)

	history = '%s between %s and %s\n' %(calc_stat.func_doc,infile1,infile2)
	history += '%s SVN revision %s and %s\n' %(__file__,
                                        	   __version__,
                                        	   datetime.now().isoformat())

	var_atts = {'long_name': '%s' %(calc_stat.func_doc),
		    'name': '%s' %(metric),
		    'history': '%s' %(history)
		   } 

	for key, value in var_atts.iteritems():
	    setattr(outvar, key, value)

	# Data

	outdata = MV2.array(stat)
	outdata = outdata.astype(numpy.float32)
	outdata.setAxisList([latitude,longitude])
	outdata.id = metric
	
	fout.write(outdata)

    else:

        months = ['january','february','march','april','may','june','july','august','september','october','november','december','djf','mam','jja','son','mjjaso','ndjfma','annual']
	time = fout.copyAxis(fin1['time'])
	axeslist = [time]
	
	for tt in range(0,len(months)):

	    metric_name = var+'_'+months[tt]
	    outvar = fout.createVariable(metric_name,'f',axeslist)

	    history = '%s between %s and %s\n' %(calc_stat.func_doc,infile1,infile2)
	    history += '%s SVN revision %s and %s\n' %(__file__,
                                        	       __version__,
                                        	       datetime.now().isoformat())

	    var_atts = {'long_name': '%s' %(calc_stat.func_doc),
			'name': '%s' %(metric_name),
			'history': '%s' %(history)
		       } 

	    for key, value in var_atts.iteritems():
		setattr(outvar, key, value)

	    # Data

	    outdata = MV2.array(stat[tt])
	    outdata = outdata.astype(numpy.float32)
	    outdata.id = metric_name

            fout.write(outdata)
	    del outdata

            
    fout.close()
    fin1.close()
    fin2.close()
 
 
if __name__ == '__main__':
    
    ## Help and manual information ##

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-M","--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-r", "--raw",action="store_true",dest='raw',default=False,help="output raw results instead of ratio")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 5:
	print """
	Usage:
            temporal_metrics.py [-M] {metric} {variable} {input_file1} {input_file2} {output_file}

	Options:
            -M or --manual      Display this on-line manual page and exit
            -h or --help        Display a help/usage message and exit
	    -r or --raw         Output raw result (for the first input file) instead of a ratio
	    
	Input arguments:
	    {metric}            Temporal correlation ('tempcorr'); temporal standard deviation ratio ('tempstd')
	                        spatial correlation ('spatcorr'); spatial standard deviation ratio ('spatstd')
	    {variable}          File variable names must be the same for both input files
	                        
	Description:
            Python script to calculate a number of commonly used temporal statistics. Assumes that the input netCDF file contains
	    a climatological mean field for each month (e.g. the file variable list might be: pr_january, pr_february, ..., pr_december). 

	Note:
            Need to load the cdat module
	    The temproal standard deviation ratio is {input_file1} / {input_file2}
	    For documentation of the methods used to calculate these metrics, see Section 2.2 of Irving et al (2011). Evaluating global 
	    climate models for the Pacific island region. Climate Research 49, 169-187; doi:10.3354/cr01028 

	Author:
            Damien Irving, Jan 2012.

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

    main(args[0], args[1], args[2], args[3], args[4], options.raw)
