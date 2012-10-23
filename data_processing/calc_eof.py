#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:     calc_eof.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Performs and Empiricial Orthogonal Function (EOF) analysis
Reference:    Uses PyClimate package
              http://fisica.ehu.es/pyclimate/ExampleEOF

Updates | By | Description
--------+----+------------
23 October 2012 | Damien Irving | Initial version.

"""

__version__= '$Revision$'     ## Change this for git (this is a svn relevant command)


### Import required modules ###

import optparse
from optparse import OptionParser
import sys
from datetime import datetime

import numpy
import math

import cdms2
import netCDF4

import pyclimate.svdeofs
import pyclimate.ncstruct


### Define functions ###

def deg2rad(d):
    """Converts from degrees to radians"""
    
    return d*math.acos(-1.)/180.


def calc_EOF(infile_name,var_id,lat_id):
    """Calculates the EOF using pyclimate - uses outdated modules because pyclimate is old"""
    # http://fisica.ehu.es/pyclimate/ExampleEOF
    
    import Numeric
    import Scientific.IO.NetCDF
    
    fin = Scientific.IO.NetCDF.NetCDFFile(infile_name)
    in_data = fin.variables[var_id]
    areafactor = numpy.sqrt(numpy.cos(deg2rad(fin.variables[lat_id][:])))
    data = in_data[:,:,:,:] * areafactor[numpy.newaxis,numpy.newaxis,:,numpy.newaxis]
    oldshape = data.shape
    data.shape = (oldshape[0], oldshape[1]*oldshape[2]*oldshape[3])

    pcs, lambdas, eofs = pyclimate.svdeofs.svdeofs(data)

    fin.close()

    return areafactor, pcs, lambdas, eofs


def write_eof(outfile_name,neofs,in_lat,in_lon,eof_output,lambdas):
    """Writes output netCDF file with EOFs in it"""
    
    # Global attributes #

    fout = netCDF4.Dataset(outfile_name,'w',format='NETCDF3_CLASSIC')

    setattr(fout,'Title','Empirical Orthogonal Function analysis')
    setattr(fout,'Contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(fout,'History','EOF calculated using PyClimate software')
    setattr(fout,'Reference','http://www.pyclimate.org/')
    setattr(fout,'Sourcefile',infile_name)
    creation_text = 'Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0])
    setattr(fout,'Created',creation_text)
    setattr(fout,'Format','NETCDF3_CLASSIC')

    # Axes #

    fout.createDimension('latitude',len(in_lat))
    fout.createDimension('longitude',len(in_lon))

    lats = fout.createVariable('latitude',numpy.dtype('float32').char,('latitude',))
    lons = fout.createVariable('longitude',numpy.dtype('float32').char,('longitude',))

    # Copy values from input file
    
    lats[:] = in_lat
    lons[:] = in_lon

    # Copy attributes from input file
    
    for att_name in in_lat.attributes.keys():
        setattr(lats, att_name, in_lat.attributes[att_name])
    for att_name in in_lon.attributes.keys():
        setattr(lons, att_name, in_lon.attributes[att_name])

    # Output data #
    
    for i in range(0,neofs):
        out_data = fout.createVariable('eof'+str(i+1),numpy.dtype('float32').char,('latitude','longitude'))    #,fill_value=9.999e+20)
	out_data.standard_name = 'eof'+str(i+1)
        out_data.history = "EOF-%s, accounting for %f %% of the variance"%(i+1,100*pyclimate.svdeofs.getvariancefraction(lambdas)[i],)

        out_data[:] = eof_output[i,:,:]

    fout.close()


def main(infile_name,var_id,outfile_name,neofs):
    """Run the program"""
    
    ## Get input data details ##

    fin = cdms2.open(infile_name)
    
    in_data = fin(var_id)   # order='tzyx'
    in_lat = in_data.getLatitude()
    in_lon = in_data.getLongitude()
    
    lat_id = in_lat.id
    
    fin.close()
    
    ## Calculate the EOF using outdated pyclimate routine ##
    
    areafactor, pcs, lambdas, eofs = calc_EOF(infile_name,var_id,lat_id)

    # Prepate output data #
    
    eof_output = numpy.zeros([neofs,len(in_lat),len(in_lon)])
    for i in range(0,neofs):
        eof_output[i,:,:] = (numpy.reshape(eofs[:,i],(len(in_lat),len(in_lon))) / areafactor[:,numpy.newaxis]).astype(numpy.float32)
        #eof1_data = eof1_data.astype(numpy.float32)

    ## Write the output files ##
    
    write_eof(outfile_name,neofs,in_lat,in_lon,eof_output,lambdas)
    #write_pcs()



if __name__ == '__main__':

    ## Help and manual information ##

    usage = "usage: %prog [options] {input_file} {input_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-n", "--neofs",dest="neofs",type='int',default=5,help="Number of EOFs for output [default=5]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            calc_eof.py [-M] [-h] {input_file} {input_variable} {output_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -n -> Number of EOFs that are output [default = 5]

        Description

        
        Assumptions (i.e. hard wired elements) 
        
        Reference

        Environment
            Need to load cdat

        Example (abyss.earthsci.unimelb.edu.au)
	    /opt/cdat/bin/cdat calc_eof.py /work/dbirving/test_data/ncepslp.djf.nc djfslp test_eof.nc
	    
        Author
            Damien Irving, 12 Oct 2012.

        Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
        """
        sys.exit(0)

    else:

        # Repeat the command line arguments #

        print 'Input file: ', args[0]
        print 'output file: ', args[2]
        
        infile_name, var_id, outfile_name = args  
    
        main(infile_name, var_id, outfile_name, options.neofs)
