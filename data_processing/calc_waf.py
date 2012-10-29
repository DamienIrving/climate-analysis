#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:     calc_waf.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates the wave activity flux (waf)
Reference:    Takaya, K., Nakamura, H., 2001
              A formulation of a phase-independent wave-activity flux
	      for stationary and migratory quasi-geostrophic eddies
	      on zonally-varying basic flow. J. Atmos. Sci., 58, 608--627 

Input:        u wind, u wind climatology 
              v wind, v wind climatology
	      geopotential height, geopotential height climatology
Output:       waf x component, waf y component


Updates | By | Description
--------+----+------------
12 October 2012 | Damien Irving | Initial version.

"""

__version__= '$Revision$'     ## Change this for git (this is a svn relevant command)


### Import required modules ###

import optparse
from optparse import OptionParser
import sys
from datetime import datetime
import os

import cdms2 
from cdms2 import MV2
import numpy
from numpy import *

import netCDF4
from scipy.io.numpyio import fwrite, fread

import regrid2
from regrid2 import Regridder



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


def read_climatology(fname,vname,nlat,nlon):
    """Reads the climatology data, assuming a certain file format"""
    
    infile = cdms2.open(fname)
    months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    monthly_climatology = numpy.zeros([12,nlat,nlon])
    for i in range(0,12):
        data = infile(vname+'_'+months[i],order='yx')
	monthly_climatology[i,:,:] = data
    
    infile.close()
    
    return monthly_climatology


def write_binary(data,outfile):
    """Takes a numpy data array and writes a corresponding binary data file"""
    
    fileobj = open(outfile, mode='wb')
    fwrite(fileobj, data.size, data)
    
    fileobj.close()


def read_binary(infile,dims):
    """Reads a binary data file and puts data in a numpy array"""

    fileobj = open(infile, mode='rb')
    
    datatype = 'f'
    size = dims[0] * dims[1] * dims[2]
    
    read_data = fread(fileobj, size, datatype)
    read_data = read_data.reshape(dims)
    
    fileobj.close()
    
    return read_data


def regrid(data,oldgrid):
    """Takes input data and regrids to a 2.5 degree global grid"""
    
    latitude = cdms2.createAxis(numpy.arange(-90,92.5,2.5,'f'),id='latitude')
    latitude.designateLatitude()
    latitude.units = 'degrees_north'
    latitude.long_name = 'Latitude'
    latitude.standard_name ='latitude'
    latitude.axis = 'Y'

    longitude = cdms2.createAxis(numpy.arange(0,360,2.5,'f'),id='longitude')
    longitude.designateLongitude()
    longitude.units = 'degrees_east'
    longitude.long_name = 'Longitude'
    longitude.standard_name = 'longitude'
    longitude.axis = 'X'
    longitude.modulo = 360.
    longitude.topology = 'circular'

    newgrid = cdms2.createRectGrid(latitude,longitude)                                                     

    regridfunc = Regridder(oldgrid, newgrid)                                
    new_data = regridfunc(data)
    
    return new_data,latitude,longitude
    

def write_netcdf(fname_out,waf_data,time_axis,lat_axis,lon_axis,sourcefile_text,outvar):
    """Writes the output netcdf file"""
    
    outfile = netCDF4.Dataset(fname_out, 'w', format='NETCDF3_CLASSIC')   ## Found error using cdo on abyss with format='NETCDF4' 

    # Global attributes #

    setattr(outfile,'Title','Wave activity flux')
    setattr(outfile,'Contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(outfile,'History','Calculated wave activity flux from U wind, V wind and geopotential height')
    setattr(outfile,'Reference','Takaya & Nakamura (2001) J. Atmos. Sci., 58, 608-627')
    setattr(outfile,'Sourcefiles',sourcefile_text)
    creation_text = 'Created %s using %s' %(datetime.utcnow().isoformat(), sys.argv[0])
    setattr(outfile,'created',creation_text)
    setattr(outfile,'Format','NETCDF3_CLASSIC')

    # Dimensions #

    outfile.createDimension('time',None)
    outfile.createDimension('latitude',len(lat_axis))
    outfile.createDimension('longitude',len(lon_axis))

    times = outfile.createVariable('time',dtype('float32').char,('time',))
    lats = outfile.createVariable('latitude',dtype('float32').char,('latitude',))
    lons = outfile.createVariable('longitude',dtype('float32').char,('longitude',))

    for att_name in time_axis.attributes.keys():
        setattr(times, att_name, time_axis.attributes[att_name])
    for att_name in lat_axis.attributes.keys():
        setattr(lats, att_name, lat_axis.attributes[att_name])
    for att_name in lon_axis.attributes.keys():
        setattr(lons, att_name, lon_axis.attributes[att_name])

    times[:] = time_axis         
    lats[:] = lat_axis           
    lons[:] = lon_axis            

    # Variable #

    out_data = outfile.createVariable(outvar,dtype('float32').char,('time','latitude','longitude'),fill_value=9.999e+20)
    out_data.units = 'm2 s-2'
    out_data.name = 'Wave activity flux, %s component'  %(outvar[-1])
    out_data.history = 'Calculated wave activity flux from U wind, V wind and geopotential height'
    out_data.standard_name = outvar

    waf_data = waf_data.astype(numpy.float32)
    out_data[:] = waf_data


    outfile.close()


def main(fname_u, fname_uclim, vname_u, fname_v, fname_vclim, vname_v, fname_zg, fname_zgclim, vname_zg, fname_wafx, fname_wafy):
    """Run the program"""

    ### Read the raw input data ###

    ## u wind ##
    infile_u = cdms2.open(fname_u)
    u_data = infile_u(vname_u,order='tyx')
    
    ## v wind ##
    infile_v = cdms2.open(fname_v)
    v_data = infile_v(vname_v,order='tyx')

    ## zg ##
    infile_zg = cdms2.open(fname_zg)
    zg_data = infile_zg(vname_zg,order='tyx')
    

    ### Check that the input data are all on the same coordinate axes ###

    ## Time ##

    time_u = u_data.getTime()
    time_v = v_data.getTime()
    time_zg = zg_data.getTime()
    
    time_axis_check(time_u, time_v)
    time_axis_check(time_u, time_zg)
    
    ## Latitude ##
    
    lat_u = u_data.getLatitude()
    lat_v = v_data.getLatitude()
    lat_zg = zg_data.getLatitude()

    xy_axis_check(lat_u, lat_v)
    xy_axis_check(lat_u, lat_zg)

    ## Longitude ##
    
    lon_u = u_data.getLongitude()
    lon_v = v_data.getLongitude()
    lon_zg = zg_data.getLongitude()

    xy_axis_check(lon_u, lon_v)
    xy_axis_check(lon_u, lon_zg)

    ## Find grid characteristics ##

    ntime, nlat, nlon = numpy.shape(u_data)
    input_grid = u_data.getGrid() 
    
    
    ### Read the climatology data ###
    
    uclim_data = read_climatology(fname_uclim,vname_u,nlat,nlon)
    vclim_data = read_climatology(fname_vclim,vname_v,nlat,nlon)
    zgclim_data = read_climatology(fname_zgclim,vname_zg,nlat,nlon)
    
    
    ### Regrid the data ###
    
    u_data_regrid, lat_regrid, lon_regrid = regrid(u_data,input_grid)
    uclim_data_regrid, lat_regrid, lon_regrid = regrid(uclim_data,input_grid)
    
    v_data_regrid, lat_regrid, lon_regrid = regrid(v_data,input_grid)
    vclim_data_regrid, lat_regrid, lon_regrid = regrid(vclim_data,input_grid)
    
    zg_data_regrid, lat_regrid, lon_regrid = regrid(zg_data,input_grid)
    zgclim_data_regrid, lat_regrid, lon_regrid = regrid(zgclim_data,input_grid)
   
    
    ### Create the binary data files for input into the Fortran wap script ### 
    
    write_binary(u_data_regrid,'u.bin')
    write_binary(uclim_data_regrid,'uclim.bin')
    write_binary(v_data_regrid,'v.bin')
    write_binary(vclim_data_regrid,'vclim.bin')
    write_binary(zg_data_regrid,'zg.bin')
    write_binary(zgclim_data_regrid,'zgclim.bin')

    
    ### Calculate the wave activity flux ###
    
    fout = open('answers.txt','w')
    print >>fout, '250'
    print >>fout, 'zg.bin'
    print >>fout, 'zgclim.bin'
    print >>fout, 'u.bin'
    print >>fout, 'uclim.bin'
    print >>fout, 'v.bin'
    print >>fout, 'vclim.bin'
    print >>fout, 'wafx.bin'
    print >>fout, 'wafy.bin'

    fout.close()
    
    os.system("/home/dbirving/data_processing/WAF/tnf_xy_onelevel.run < answers.txt")
    
    
    ### Write the output netCDF file ###
    
    wafx_data = read_binary('wafx.bin',[ntime,73,144])
    wafy_data = read_binary('wafy.bin',[ntime,73,144])
    
    sourcefile_text = '%s, %s, %s, %s, %s, %s' %(fname_u, fname_uclim, fname_v, fname_vclim, fname_zg, fname_zgclim)
    
    write_netcdf(fname_wafx,wafx_data,time_u,lat_regrid,lon_regrid,sourcefile_text,'wafx')
    write_netcdf(fname_wafy,wafy_data,time_u,lat_regrid,lon_regrid,sourcefile_text,'wafy')

    
    ### Clean up ###
    
    os.system("rm answers.txt zg.bin zgclim.bin u.bin uclim.bin v.bin vclim.bin wafx.bin wafy.bin")

    infile_u.close()
    infile_v.close()
    infile_zg.close()


if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {u_file} {u_name} {v_file} {v_name} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")

    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            calc_waf.py [-M] [-h] {u_file} {u_clim_file} {u_name} 
	    {v_file} {v_clim_file} {v_name} {zg_file} {zg_clim_file} {zg_name}
	    {output_wafx_file} {output_wafy_file}

	Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit

	Description
            Takes as input the u wind, v wind, geopotential height (zg)  
	    and their climatologies and outputs the x and y 
	    components of the wave activity flux.
	
	Assumptions (i.e. hard wired elements) 
	    The WAF Fortran code is hard wired to produce output on a 
	    global 2.5 by 2.5 deg grid (i.e. 73 lats, 144 lons)
	    It is hard wired that the input data is from the 250 hPa level 
	
	Reference
	    Takaya, K., Nakamura, H., 2001.
            A formulation of a phase-independent wave-activity flux
	    for stationary and migratory quasi-geostrophic eddies
	    on zonally-varying basic flow. J. Atmos. Sci., 58, 608-627    

	Environment
            Need to load cdat

        Example (abyss.earthsci.unimelb.edu.au)
	    /opt/cdat/bin/cdat calc_waf.py 
	    /work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc
	    /work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-clim-1981-2010_native.nc
	    ua
	    /work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc
	    /work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-clim-1981-2010_native.nc
	    va
	    /work/dbirving/datasets/Merra/data/zg_Merra_250hPa_monthly_native.nc
	    /work/dbirving/datasets/Merra/data/processed/zg_Merra_250hPa_monthly-clim-1981-2010_native.nc
	    zg
            /work/dbirving/datasets/Merra/data/processed/wafx_Merra_250hPa_monthly_native.nc
	    /work/dbirving/datasets/Merra/data/processed/wafy_Merra_250hPa_monthly_native.nc
	    
	Author
            Damien Irving, 12 Oct 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)

    else:

        # Repeat the command line arguments #

	print 'Input u wind: ', args[0]
	print 'Input u wind climatology: ', args[1]
	print 'Input v wind: ', args[3]
	print 'Input v wind climatology: ', args[4]
	print 'Input zg: ', args[6]
	print 'Input zg climatology: ', args[7]
	print 'Ouput wafx: ', args[9]
	print 'Ouput wafx: ', args[10]

    fname_u, fname_uclim, vname_u, fname_v, fname_vclim, vname_v, fname_zg, fname_zgclim, vname_zg, fname_wafx, fname_wafy = args  
    
    main(fname_u,fname_uclim,vname_u,fname_v,fname_vclim,vname_v,fname_zg,fname_zgclim,vname_zg,fname_wafx,fname_wafy)