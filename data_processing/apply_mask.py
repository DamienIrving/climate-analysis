#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:      apply_mask.py
Author:        Damien Irving, d.irving@student.unimelb.edu.au
Description:   Applies a given mask to a given datafile. 

Updates | By | Description
--------+----+------------
16 January 2012 | Damien Irving | Initial version.
25 October 2012 | Damien Irving | Significant revision.

"""

__version__= '$Revision$'


### Import required modules ###

import sys
from optparse import OptionParser
from datetime import datetime

import cdms2 
import numpy

import regrid2
from regrid2 import Regridder

import netCDF4

                                             
### Define the relevant functions ###


def list_nobounds(cf, ids=False):
    """Gets the list of file variables"""
    
    bnds = [v.bounds for v in cf.variables.values() if 'bounds' in v.attributes]
    bnds += [a.bounds for a in cf.axes.values() if 'bounds' in a.attributes]
    nodim = [vid for vid in cf.variables.keys() if cf[vid].getOrder() == '']
    nonvar = bnds + nodim
    if ids:
        return [v for v, k in cf.variables.iteritems() if v not in nonvar]
    else:
        return [k for v, k in cf.variables.iteritems() if v not in nonvar]


def create_mask(mask_data,mask_type,hide,threshold):
    """Creates the mask array of 1s and 0s, where 1 = apply mask"""
    
    assert ((mask_type == 'LAF') or (mask_type == 'OAF')), """Unrecognised mask type - must be 'LAF' or 'OAF'"""
    assert ((hide == 'land') or (hide == 'ocean')), """Unrecognised hide selection - must be 'land' or 'ocean'""" 
    
    mask_data = numpy.squeeze(mask_data)   
    if ((mask_type == 'LAF' and hide == 'ocean') or (mask_type == 'OAF' and hide == 'land')):
        mask_data = 1.0 - mask_data

    mask = numpy.where(mask_data > threshold, 1, 0)
    
    return mask


def grid_check(mask_lat, mask_lon, in_lat, in_lon):
    """Checks that the data are on the same grid"""
        
    if len(mask_lat) != len(in_lat) or len(mask_lon) != len(in_lon):
        grid_match = False
	print 'Input data interpolated to mask grid...'
    else:
        grid_match = True

    return grid_match


def create_axis(name,fout,in_axis):
    """Creates a new netCDF axis"""
    
    fout.createDimension(name,len(in_axis))
    axis = fout.createVariable(name,numpy.dtype('float32').char,(name,))
    axis[:] = in_axis
    for att_name in in_axis.attributes.keys():
        setattr(axis, att_name, in_axis.attributes[att_name])


def main(mask_file, mask_var, mask_type, input_file, output_file, hide, threshold):
    """Run the program"""
    
    ## Read mask file ##
    
    mfin = cdms2.open(mask_file)
    mask_data = mfin(mask_var, order='yx')
    mask_lat = mask_data.getLatitude()
    mask_lon = mask_data.getLongitude()
    mask_grid = mask_data.getGrid()
    
    
    ## Read input file ##
    
    fin = cdms2.open(input_file)
    in_vars = list_nobounds(fin, ids=True)
    in_data_var1 = fin(in_vars[0])
    
    in_lat = in_data_var1.getLatitude()
    in_lon = in_data_var1.getLongitude()
    
    if len(numpy.shape(in_data_var1)) > 2:
        is_time = True
	order = 'tyx'
	in_time = fin.getAxis('time')
    else:
        is_time = False
	order = 'yx'
    
    
    ## Create mask ##
    
    mask = create_mask(mask_data,mask_type,hide,threshold)
    
    
    ## Check that mask and input data are on same grid ##
    
    grid_match = grid_check(mask_lat, mask_lon, in_lat, in_lon)
    
    
    ## Create the output file ##
    
    fout = netCDF4.Dataset(output_file,'w',format='NETCDF3_CLASSIC')
    
    # Global attributes #
    
    for att_name in fin.attributes.keys():
        setattr(fout, att_name, fin.attributes[att_name])
    
    setattr(fout,'Mask','%s mask (points with %s fraction > %s hidden) applied to %s on %s using %s' %(hide,hide,threshold,input_file,datetime.utcnow().isoformat(), sys.argv[0]))
    setattr(fout,'Format','NETCDF3_CLASSIC')
    
    # Axes #
    
    create_axis('latitude',fout,in_lat)
    create_axis('longitude',fout,in_lon)
    if is_time:
        create_axis('time',fout,in_time)		
	axis_list = ('time','latitude','longitude')
    else:  
        axis_list = ('latitude','longitude')

    # Write new variables #   
    
    for v in in_vars:
	in_data = fin(v, order=order)
	
	if grid_match == False:
	    oldgrid=in_data.getGrid()                                               
            regridfunc=Regridder(oldgrid, mask_grid)                                
            in_data=regridfunc(in_data)
	
        in_data=numpy.squeeze(in_data)	
	in_data_ma = numpy.where(mask == 1, 9.999e+20, in_data) 
	
	out_var = fout.createVariable(v,numpy.dtype('float32').char,axis_list,fill_value=9.999e+20) 
	for att_name in in_data.attributes.keys():
            setattr(out_var, att_name, in_data.attributes[att_name])
	setattr(out_var, 'mask', 'points with %s fraction > %s hidden' %(hide,threshold))
	out_var[:] = in_data_ma
	
	   
    mfin.close()
    fin.close()
    fout.close()


if __name__ == '__main__':
    
    ## Help and manual information ##

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)

    parser.add_option("-M","--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("--hide",dest="hide",type='string',default='land',help="thing that you want to mask/hide [default = land]")
    parser.add_option("-t", "--threshold",dest="threshold",type='float',default=0.01,help="value of mask threshold [default = 0.01]")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 5:
	print """
	Usage:
            apply_mask.py [-M] [-h] [-t] {mask_file} {mask_variable} {mask_type} {input_file} {output_file}

	Options:
            -M or --manual      Display this on-line manual page and exit
            -h or --help        Display a help/usage message and exit
	    --hide              Thing that you want to hide. Can be 'land' or 'ocean' [default = land]
	    -t or --threshold   Value of mask threshold [default = 0.01]. Will hide the selected medium 
	                        (land or ocean) when its fractional value is greater than this.
	
	Assumptions
	    {mask_file}  Should contain values between 0 and 1
	    {mask_type}  Can be either land area fraction (LAF) or ocean area fraction (OAF)
	                        
	Description:
            Applies a mask to a given netCDF datafile.
	    The data will be interpolated to the same grid as the mask if they aren't already. 

	Environment:
            Need to load the cdat module
	
	Example:
	    <abyss.earthsci.unimelb.edu.au>
	        /opt/cdat/bin/cdat /home/dbirving/data_processing/apply_mask.py 
		/work/dbirving/datasets/Merra/data/sftof_Merra_surface_fixed_native.nc sftof OAF
		/work/dbirving/datasets/Merra/data/ts_Merra_surface_monthly_native.nc
		/work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly_native-ocean.nc
	    
	    <dcc.nci.org.au>
	        cdat apply_mask.py /projects/ua6/CAWCR_CVC_processed/staging/users/dbi599/ua4/AWAP
	        /AWAP/moise/fractional_land.1.5-deg.nc data
	        /projects/ua6/CAWCR_CVC_processed/staging/users/dbi599/IPCC/CMIP5/
	        processed/r240x120/BCC/bcc-csm1-1/historical/seas/atmos/pr/r1i1p1/aggregates/
	        pr_Amon_bcc-csm1-1_historical_r1i1p1_1979-2005-clim_r240x120.nc test.nc
	    
	Author:
            Damien Irving, Feb 2012.

	Bugs:
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)


    ### Read the input data and repeat back to user ###

    print 'Input mask file: ', args[0]
    print 'Input mask variable: ', args[1]
    print 'Input mask type: ', args[2]
    print 'Output masked/hidden element:', options.hide
    print 'Output mask threshold: ', options.threshold
    print 'Input data file: ', args[3]
    print 'Output data file: ', args[4]
    
    mask_file, mask_var, mask_type, input_file, output_file  = args
    
    main(mask_file, mask_var, mask_type, input_file, output_file, options.hide, options.threshold)
