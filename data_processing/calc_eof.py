#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:     calc_eof.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Performs and Empiricial Orthogonal Function (EOF) analysis
Reference:    Uses eof2 package: https://github.com/ajdawson/eof2

Updates | By | Description
--------+----+------------
23 October 2012 | Damien Irving | Initial version.
10 December 2012 | Damien Irving | Switched over to eof2 package

"""

__version__= '$Revision$'     ## Change this for git (this is a svn relevant command)


### Import required modules ###

import optparse
from optparse import OptionParser
import sys
from datetime import datetime
import os

import numpy

import cdms2

## CDAT Version 5.2 File are now written with compression and shuffling ##
#You can query different values of compression using the functions:
#cdms2.getNetcdfShuffleFlag() returning 1 if shuffling is enabled, 0 otherwise
#cdms2.getNetcdfDeflateFlag() returning 1 if deflate is used, 0 otherwise
#cdms2.getNetcdfDeflateLevelFlag() returning the level of compression for the deflate method
#If you want to turn that off or set different values of compression use the functions:
#cdms2.setNetcdfShuffleFlag(value) ## where value is either 0 or 1
#cdms2.setNetcdfDeflateFlag(value) ## where value is either 0 or 1
#cdms2.setNetcdfDeflateLevelFlag(value) ## where value is a integer between 0 and 9 included

cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)

import eof2


### Define globals ###

eqpacific = cdms2.selectors.Selector(latitude=(-30,30,'cc'),longitude=(120,280,'cc'))
tropics = cdms2.selectors.Selector(latitude=(-30,30,'cc'),longitude=(0,360,'cc'))

### Define functions ###

def calc_eofs(data,neofs,eof_scaling,pc_scaling):
    """Calculates the eof2 package: https://github.com/ajdawson/eof2"""
    
    solver = eof2.Eof(data, weights='area')
    
    if eof_scaling == 3:
        eofs = solver.eofsAsCorrelation(neofs=neofs)
	eof_scaling_text = 'EOF scaled as the correlation of the PCs with the original field - used eofsAsCorrelation() function'
	eof_units = ''
    else: 
	eofs = solver.eofs(neofs=neofs,eofscaling=eof_scaling)
        eof_units = ''
	if eof_scaling == 0:
	    eof_scaling_text = 'None'
	elif eof_scaling == 1:
	    eof_scaling_text = 'EOF is divided by the square-root of its eigenvalue'  # gives a larger value in the end
	elif eof_scaling == 2:
	    eof_scaling_text = 'EOF is multiplied by the square-root of its eigenvalue'        
	else:
	    print 'EOF scaling method not recongnised'
	    sys.exit(1)
    
    pcs = solver.pcs(npcs=neofs, pcscaling=pc_scaling)
    pc_units = ''
    if pc_scaling == 0:
        pc_scaling_text = 'None'
    elif pc_scaling == 1:
        pc_scaling_text = 'PC scaled to unit variance (divided by the square-root of its eigenvalue)'
    elif pc_scaling == 2:
        pc_scaling_text = 'PC multiplied by the square-root of its eigenvalue'    
    else:
	print 'PC scaling method not recongnised'
	sys.exit(1)    
    
    varfracs = solver.varianceFraction(neigs=neofs)

    return eofs, eof_scaling_text, eof_units, pcs, pc_scaling_text, pc_units, varfracs


def write_eofs(outfile_eof_name,neofs,eofs,varfracs,infile_name,in_lat,in_lon,in_history,outfile_pc_name,region_name,eof_scaling_text,eof_units):
    """Writes output netCDF file with EOFs in it"""
    
    outfile = cdms2.open(outfile_eof_name,'w')
    
    # Global attributes #

    global_atts = {'title': 'Empirical Orthogonal Function analysis over %s region' %(region_name),
                   'contact': 'Damien Irving (d.irving@student.unimelb.edu.au)',
                   'reference': 'https://github.com/ajdawson/eof2',
		   'history': '%s: Calculated EOF from %s using %s, format=NETCDF3_CLASSIC\n%s' %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
                   infile_name,sys.argv[0],in_history)
                  }
                      
    for key, value in global_atts.iteritems():
        setattr(outfile, key, value)

    # Variables #

    axisInLat = outfile.copyAxis(in_lat)  
    axisInLon = outfile.copyAxis(in_lon)  
    
    for i in range(0,neofs):
	var = eofs[i,:,:]
	var = cdms2.MV2.array(var)
	var = var.astype(numpy.float32)
	var.setAxisList([axisInLat,axisInLon])
	var.id = 'eof'+str(i+1)

	var_atts = {'name': 'eof'+str(i+1),
                    'standard_name': 'eof'+str(i+1),
                    'units': eof_units, 
		    'scaling': eof_scaling_text, 
                    'variance_explained': '%7.4f' %(varfracs[i])
        	   } 

	for key, value in var_atts.iteritems():
            setattr(var, key, value)

        outfile.write(var)  


    outfile.close()


def write_pcs(outfile_pc_name,neofs,pcs,infile_name,in_time,outfile_eof_name,region_name,pc_scaling_text,pc_units):
    """Writes an output text file for each of the Principle Components (pcs)"""
    
    ## Get time axis info ##
    
    times = in_time.asComponentTime()
    years = []
    months = []
    
    for ii in range(0,len(times)):
        years.append(int(str(times[ii]).split('-')[0]))
        months.append(int(str(times[ii]).split('-')[1]))
    
    
    ## Write outfiles ##
    
    for i in range(0,neofs):
        
	# File name #
    
        new_name = outfile_pc_name.replace('PC','PC'+str(i+1))
        fout = open(new_name,'w')   
	        
	# Global attributes #
	
	fout.write('Title: Principle Component %s from EOF analysis over %s region \n' %(i+1,region_name))
        fout.write('Contact: Damien Irving (d.irving@student.unimelb.edu.au) \n')
        fout.write('History: EOF calculated using eof2 cdat module \n')
        fout.write('Reference: https://github.com/ajdawson/eof2 \n')
        fout.write('Sourcefile: %s \n' %(infile_name))
	fout.write('Companion EOF file: %s \n' %(outfile_eof_name))
        fout.write('Created %s using %s \n' %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), sys.argv[0]))
	fout.write('Scaling: %s \n' %(pc_scaling_text))
	fout.write('Units: %s \n' %(pc_units))
	
	# Data #
	
	fout.write(' YR   MON  PC%s \n' %(i+1)) 
        ntime = numpy.shape(pcs)[0]
	for t in range(0,ntime):
            print >> fout, '%4i %3i %7.2f' %(years[t],months[t],pcs[t,i])


def main(infile_name,var_id,outfile_eof_name,outfile_pc_name,neofs,region_name,time_bounds,eof_scaling,pc_scaling):
    """Run the program"""
    
    fin = cdms2.open(infile_name)
    
    ## Get input data ##
    
    if region_name:
        try:
	    region = globals()[region_name]
	except KeyError:
	    print 'region not defined - using all spatial data...'
	    region = None
    else:
        region = None 
    
    if time_bounds and region:
	in_data = fin(var_id,region,time=(time_bounds[0],time_bounds[1]),squeeze=1)
    elif time_bounds: 
        in_data = fin(var_id,time=(time_bounds[0],time_bounds[1]),squeeze=1)
    elif region:
        in_data = fin(var_id,region,squeeze=1)
    else:
	in_data = fin(var_id,squeeze=1)

    in_time = in_data.getTime()
    in_lat = in_data.getLatitude()
    in_lon = in_data.getLongitude()
    in_history = fin.attributes['history'] if ('history' in fin.attributes.keys()) else ''

    
    ## Calculate the EOFs ##
    
    eofs, eof_scaling_text, eof_units, pcs, pc_scaling_text, pc_units, varfracs = calc_eofs(in_data,neofs,eof_scaling,pc_scaling)

    
    ## Write the output files ##
    
    write_eofs(outfile_eof_name,neofs,eofs,varfracs,infile_name,in_lat,in_lon,in_history,outfile_pc_name,region_name,eof_scaling_text,eof_units)
    write_pcs(outfile_pc_name,neofs,pcs,infile_name,in_time,outfile_eof_name,region_name,pc_scaling_text,pc_units)

    ## Clean up ##
        
    fin.close()
    

if __name__ == '__main__':

    ## Help and manual information ##

    usage = "usage: %prog [options] {input_file} {input_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-n", "--neofs",dest="neofs",type='int',default=5,help="Number of EOFs for output [default=5]")
    parser.add_option("-r", "--region",dest="region",type='string',default=None,help="Region over which to calculate EOF [default=entire]")
    parser.add_option("-t", "--time_bounds",dest="time_bounds",default=None,nargs=2,type='str',help="Period over which to calculate time mean [default = entire time period]")
    parser.add_option("-e", "--eof_scaling",dest="eof_scaling",type='int',default=0,help="Scaling method applied to EOF post calculation [default = None]")
    parser.add_option("-p", "--pc_scaling",dest="pc_scaling",type='int',default=0,help="Scaling method applied to EOF post calculation [default = None]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            calc_eof.py [-M] [-h] [-n] [-r] [-t] [-p] [-e] {input_file} {input_variable} {output_eof_file} {output_pc_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -n -> Number of EOFs that are output [default = 5]
	    -r -> Region over which to calculate the EOF [default = entire; i.e whole input region]
            -t -> Time period over which to calculate the EOF (2 args: start_date end_date) [default = entire]
	    -e -> Scaling method applied to EOF post calculation [default = None] 
            -p -> Scaling method applied to PC post calculation [default = None] 
		   
	Note
	    The output PC files will take the user supplied file name and replace the string PC with PC1, PC2 etc 
        
	Options
	    region: eqpacific
	    
	    eof_scaling:      
                0 : Un-scaled EOFs (default).
                1 : EOFs are divided by the square-root of their eigenvalues.
                2 : EOFs are multiplied by the square-root of their eigenvalues.
		3 : EOFs scaled as the correlation of the PCs with the original field. 

	    pc_scaling:
                0 : Un-scaled principal components (default).
                1 : Principal components are scaled to unit variance (divided by the square-root of their eigenvalue).
                2 : Principal components are multiplied by the square-root of their eigenvalue.
       
        Reference
            Uses eof2 package: https://github.com/ajdawson/eof2

        Example (abyss.earthsci.unimelb.edu.au)
	    /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_eof.py -r eqpacific -t 1979-01-01 2011-12-31 
	    /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc ts 
	    /work/dbirving/processed/indices/data/ts_Merra_surface_EOF_monthly-1979-2011_native-ocean-eqpacific.nc
	    /work/dbirving/processed/indices/data/ts_Merra_surface_PC_monthly_native-ocean-eqpacific.txt
	    
        Author
            Damien Irving, 10 Dec 2012.

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
    
        main(infile_name, var_id, outfile_eof_name, outfile_pc_name, options.neofs, options.region, options.time_bounds, 
	options.eof_scaling, options.pc_scaling)
