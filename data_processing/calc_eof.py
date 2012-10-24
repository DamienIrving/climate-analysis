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
import os

import numpy
import math

import cdms2
import netCDF4

import pyclimate.svdeofs
import pyclimate.ncstruct


### Define functions ###


def extract_region(infile_name,region):
    """Creates a new file with the region of interest extracted"""
    
    ### Write a check for legitimate region name ###
    
    if region == 'entire':
        regional_infile_name = infile_name
    else:
	function = '/home/dbirving/data_processing/named_region.sh'
	regional_infile_name = infile_name.replace('.nc','.%s.nc' %(region))
	os.system("%s %s %s %s" %(function,region,infile_name,regional_infile_name)) 
        
    return regional_infile_name 


def deg2rad(d):
    """Converts from degrees to radians"""
    
    return d*math.acos(-1.)/180.


def calc_EOF(regional_infile_name,var_id,lat_id):
    """Calculates the EOF using pyclimate - uses outdated modules because pyclimate is old"""
    # http://fisica.ehu.es/pyclimate/ExampleEOF
    
    import Numeric
    import Scientific.IO.NetCDF
    
    fin = Scientific.IO.NetCDF.NetCDFFile(regional_infile_name)
    in_data = fin.variables[var_id]
    areafactor = numpy.sqrt(numpy.cos(deg2rad(fin.variables[lat_id][:])))
    data = in_data[:,:,:,:] * areafactor[numpy.newaxis,numpy.newaxis,:,numpy.newaxis]
    oldshape = data.shape
    data.shape = (oldshape[0], oldshape[1]*oldshape[2]*oldshape[3])

    pcs, lambdas, eofs = pyclimate.svdeofs.svdeofs(data)

    fin.close()

    return areafactor, pcs, lambdas, eofs


def write_eof(outfile_eof_name,neofs,in_lat,in_lon,eof_output,lambdas,infile_name,outfile_pc_name,region):
    """Writes output netCDF file with EOFs in it"""
    
    # Global attributes #

    fout = netCDF4.Dataset(outfile_eof_name,'w',format='NETCDF3_CLASSIC')

    setattr(fout,'Title','Empirical Orthogonal Function analysis over %s region' %(region))
    setattr(fout,'Contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(fout,'History','EOF calculated using PyClimate software')
    setattr(fout,'Reference','http://www.pyclimate.org/')
    setattr(fout,'SourceFile',infile_name)
    setattr(fout,'CompanionFiles',outfile_pc_name)
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


def write_pcs(outfile_pc_name,neofs,pcs,years,months,infile_name,outfile_eof_name,region):
    """Writes an output text file for each of the Principle Components (pcs)"""
    
    for i in range(0,neofs):
        
	# File name #
    
        new_name = outfile_pc_name.replace('PC','PC'+str(i+1))
        fout = open(new_name,'w')   
	        
	# Global attributes #
	
	fout.write('Title: Principle Component %s from EOF analysis over %s region \n' %(i+1,region))
        fout.write('Contact: Damien Irving (d.irving@student.unimelb.edu.au) \n')
        fout.write('History: EOF calculated using PyClimate software \n')
        fout.write('Reference: http://www.pyclimate.org/ \n')
        fout.write('Sourcefile: %s \n' %(infile_name))
	fout.write('Companion EOF file: %s \n' %(outfile_eof_name))
        creation_text = 'Created %s using %s \n' %(datetime.utcnow().isoformat(), sys.argv[0])
        fout.write(creation_text)
	
	# Data #
	
	fout.write(' YR   MON  PC%s \n' %(i+1)) 
        ntime = numpy.shape(pcs)[0]
	for t in range(0,ntime):
            print >> fout, '%4i %3i %7.2f' %(years[t],months[t],pcs[t,i])


def main(infile_name,var_id,outfile_eof_name,outfile_pc_name,neofs,region):
    """Run the program"""
    
    ## Create a new file with the region of interest, if necessary ##
    
    regional_infile_name = extract_region(infile_name,region)
    
    ## Get input data details ##

    fin = cdms2.open(regional_infile_name)
    
    in_data = fin(var_id)   # order='tzyx'
    
    # Lat/lon info #
    
    in_lat = in_data.getLatitude()
    in_lon = in_data.getLongitude()
    
    lat_id = in_lat.id
    
    # Time axis info #
    
    in_time = fin.getAxis('time').asComponentTime()
    years = []
    months = []
    
    for ii in range(0,len(in_time)):
        years.append(int(str(in_time[ii]).split('-')[0]))
        months.append(int(str(in_time[ii]).split('-')[1]))
    
    fin.close()
    
    ## Calculate the EOF using outdated pyclimate routine ##
    
    areafactor, pcs, lambdas, eofs = calc_EOF(regional_infile_name,var_id,lat_id)

    # Prepate output data #
    
    eof_output = numpy.zeros([neofs,len(in_lat),len(in_lon)])
    for i in range(0,neofs):
        eof_output[i,:,:] = (numpy.reshape(eofs[:,i],(len(in_lat),len(in_lon))) / areafactor[:,numpy.newaxis]).astype(numpy.float32)

    ## Write the output files ##
    
    write_eof(outfile_eof_name,neofs,in_lat,in_lon,eof_output,lambdas,infile_name,outfile_pc_name,region)
    write_pcs(outfile_pc_name,neofs,pcs,years,months,infile_name,outfile_eof_name,region)


if __name__ == '__main__':

    ## Help and manual information ##

    usage = "usage: %prog [options] {input_file} {input_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-n", "--neofs",dest="neofs",type='int',default=5,help="Number of EOFs for output [default=5]")
    parser.add_option("-r", "--region",dest="region",type='string',default='entire',help="Regional over which to calculate EOF [default=entire]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            calc_eof.py [-M] [-h] [-n] [-r] {input_file} {input_variable} {output_eof_file} {output_pc_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -n -> Number of EOFs that are output [default = 5]
	    -r -> Region over which to calculate the EOF [default = entire; i.e whole input region]

        Note
	    The output PC files will take the user supplied file name 
	    and replace the string PC with PC1, PC2 etc 

        Description

        
        Assumptions (i.e. hard wired elements) 
        
        Reference

        Environment
            Need to load cdat

        Example (abyss.earthsci.unimelb.edu.au)
	    /opt/cdat/bin/cdat calc_eof.py /work/dbirving/test_data/ncepslp.djf.nc djfslp test_EOF.nc test_PC.txt
	    
        Author
            Damien Irving, 12 Oct 2012.

        Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
        """
        sys.exit(0)

    else:

        # Repeat the command line arguments #

        print 'Input file: ', args[0]
        print 'Output EOF file: ', args[2]
	print 'Output PC file:', args[3]
	print 'Region:', options.region
        
        infile_name, var_id, outfile_eof_name, outfile_pc_name = args  
    
        main(infile_name, var_id, outfile_eof_name, outfile_pc_name, options.neofs, options.region)
