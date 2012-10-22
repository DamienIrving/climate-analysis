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



def deg2rad(d):
    """Converts from degrees to radians"""
    
    return d*math.acos(-1.)/180.


def calc_EOF(infile_name,var_name):
    """Calculates the EOF using pyclimate - uses outdated modules because pyclimate is old"""
    # http://fisica.ehu.es/pyclimate/ExampleEOF
    
    import Numeric
    import Scientific.IO.NetCDF
    
    inc = Scientific.IO.NetCDF.NetCDFFile(infile_name)
    slp = inc.variables[var_name]
    areafactor = numpy.sqrt(numpy.cos(deg2rad(inc.variables["lat"][:])))
    slpdata = slp[:,:,:,:] * areafactor[numpy.newaxis,numpy.newaxis,:,numpy.newaxis]
    oldshape = slpdata.shape
    slpdata.shape = (oldshape[0], oldshape[1]*oldshape[2]*oldshape[3])

    pcs, lambdas, eofs = pyclimate.svdeofs.svdeofs(slpdata)

    print numpy.shape(pcs)
    print numpy.shape(eofs)

    inc.close()

    return areafactor, pcs, lambdas, eofs


def main(infile_name,var_name,outfile_name):
    """Run the program"""
    
    ## Calculate the EOF using outdated pyclimate routine ##
    
    areafactor, pcs, lambdas, eofs = calc_EOF(infile_name,var_name)

    ## Write the output file ##

    # Get input data details #

    fin = cdms2.open(infile_name)
    slp = fin(var_name)   # order='tzyx'

    ntime,nlat,nlon = numpy.shape(numpy.squeeze(slp))

    # Global attributes #

    fout = netCDF4.Dataset(outfile_name,'w',format='NETCDF3_CLASSIC')

    setattr(fout,'Title','Empirical Orthogonal Function analysis')
    setattr(fout,'Contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(fout,'History','EOF calculated using PyClimate software')
    setattr(fout,'Reference','http://www.pyclimate.org/')
    setattr(fout,'Sourcefile',infile_name)
    creation_text = 'Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0])
    setattr(fout,'created',creation_text)
    setattr(fout,'Format','NETCDF3_CLASSIC')

    # Axes #

    fout.createDimension('latitude',nlat)
    fout.createDimension('longitude',nlon)

    lats = fout.createVariable('latitude',numpy.dtype('float32').char,('latitude',))
    lons = fout.createVariable('longitude',numpy.dtype('float32').char,('longitude',))

    # Copy values from input file
    
    lats[:] = fin['lat']
    lons[:] = fin['lon']

    # Copy attributes from input file
    
    in_lat = slp.getLatitude()
    in_lon = slp.getLongitude()
    for att_name in in_lat.attributes.keys():
        setattr(lats, att_name, in_lat.attributes[att_name])
    for att_name in in_lon.attributes.keys():
        setattr(lons, att_name, in_lon.attributes[att_name])

    # Output data #

    out_data = fout.createVariable('eof1',numpy.dtype('float32').char,('latitude','longitude'))    #,fill_value=9.999e+20)
    
    out_data.standard_name = 'eof1'
    out_data.history = "First EOF accounting for %f %% of the variance"%(100*pyclimate.svdeofs.getvariancefraction(lambdas)[0],)

    eof1_data = (numpy.reshape(eofs[:,0],(nlat,nlon)) / areafactor[:,numpy.newaxis])
    eof1_data = eof1_data.astype(numpy.float32)

    out_data[:] = eof1_data

    fin.close()
    fout.close()


if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {input_file} {input_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            calc_eof.py [-M] [-h] {input_file} {input_variable} {output_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit

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
        
    infile_name, var_name, outfile_name = args  
    
    main(infile_name, var_name, outfile_name)
