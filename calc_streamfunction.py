#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:     calc_streamfunction.py
Author:       Damien Irving, irv033, Damien.Irving@csiro.au
Description:  Calculates the streamfunction     

Input:        U and V wind files
Output:       A netCDF file containing the streamfunction


Updates | By | Description
--------+----+------------
17 July 2012 | Damien Irving | Initial version.

"""

__version__= '$Revision$'


### Import required modules ###

import optparse
from optparse import OptionParser
import sys
from datetime import datetime

import cdms2 
from cdms2 import MV2
import numpy
from numpy import *

import sphere


#print cdms2.getNetcdfShuffleFlag()
#print cdms2.setNetcdfDeflateFlag()
#print cdms2.setNetcdfDeflateLevelFlag()
#cdms2.setNetcdfShuffleFlag(1)
#cdms2.setNetcdfDeflateFlag(1)
#cdms2.setNetcdfDeflateLevelFlag(1)


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


def xy_axis_check(axis1, axis2):
    """Checks whether the lat or lon axes of the input files are the same""" 
   
    if (len(axis1) != len(axis2)):
        sys.exit('Input files do not all have the same %s axis' %(axis1.id))

	
def main(fname_u, vname_u, fname_v, vname_v, fname_out):
    """Run the program"""

    ### Read the input data ###

    ## U wind ##
    infile_u = cdms2.open(fname_u)
    u = infile_u(vname_u,order='tyx')

    ## V wind ##
    infile_v = cdms2.open(fname_v)
    v = infile_v(vname_v,order='tyx')


    ### Check that the input data are all on the same coordinate axes ###

    ## Time ##

    time_u = u.getTime()
    time_v = v.getTime()
    
    time_axis_check(time_u, time_v)
    
    
    ## Latitude ##
    
    lat_u = u.getLatitude()
    lat_v = v.getLatitude()

    xy_axis_check(lat_u, lat_v)

    ## Longitude ##
    
    lon_u = u.getLongitude()
    lon_v = v.getLongitude()

    xy_axis_check(lon_u, lon_v)


    ### Calculate the streamfunction (sf) and velocity potential (vp) ###
        
    ntime, nlats, nlons = numpy.shape(u)
    
    sf = numpy.zeros([ntime, nlats, nlons])
    x = sphere.Sphere(lon_u,lat_u)
    
    for t in range(0,ntime):
        sf[t,:,:], vp = x.sfvp(u[t,:,:],v[t,:,:])
    
    
    ### Create output file ###

    global_atts = {'title': 'Streamfunction',
		   'contact': 'Damien Irving (d.irving@student.unimelb.edu.au)',
		   'history': 'Calculated streamfunction from U and V wind',
		   'sourcefiles': '%s, %s' %(fname_u,fname_v),
		   'created': 'Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0])
		  }

    outfile = cdms2.open(fname_out,'w')

    for key, value in global_atts.iteritems():
	setattr(outfile, key, value)

    axisInTime = outfile.copyAxis(u.getTime())
    axisInLat = outfile.copyAxis(u.getLatitude())   # infile_u['latitude']
    axisInLon = outfile.copyAxis(u.getLongitude())  # infile_u['longitude']
    

    var = sf
    var = MV2.array(var)
    var = var.astype(numpy.float32)
    var.setAxisList([axisInTime,axisInLat,axisInLon])
    var.id = 'sf'

    var_atts = {'name': 'Streamfunction',
        	 'standard_name': 'sf',
        	 'original_name': 'sf',
        	 'units': '%',
		 'history': 'Calculated streamfunction from U and V wind'
		} 

    for key, value in var_atts.iteritems():
	setattr(var, key, value)

    
    outfile.write(var)  
    
    outfile.close()
    infile_u.close()
    infile_v.close()


if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {u_file} {u_name} {v_file} {v_name} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            calc_streamfunction.py [-M] [-h] {u_file} {u_name} {v_file} {v_name} {output_file}

	Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit

	Description
            Takes as input the u and v wind and outputs the streamfunction    

	Environment
            Need to load cdat

	Author
            Damien Irving, 17 Jul 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)

    else:

        # Repeat the command line arguments #

	print 'Input U wind file: ', args[0]
	print 'Input V wind file: ', args[2]
	print 'Ouput file: ', args[4]

    fname_u, vname_u, fname_u, vname_u, fname_out = args  
    
    main(fname_u, vname_u, fname_u, vname_u, fname_out)
