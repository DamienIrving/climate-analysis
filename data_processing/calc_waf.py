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

import netCDF4
from scipy.io.numpyio import fwrite, fread
# note that in later versions of scipy numpyio this has been replaced.
# For a work around, see http://stackoverflow.com/questions/10637376/import-error-no-module-named-numpyio 

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
    """Reads the climatology data, assuming a 12 step monthly file format"""
    
    infile = cdms2.open(fname)
    
    months = ['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec']
    monthly_climatology = numpy.zeros([len(months),nlat,nlon])
    for i in range(0,len(months)):
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
    """Reads a binary data file and puts data in an array"""

    fileobj = open(infile, mode='rb')
    
    datatype = 'f'
    size = dims[0] * dims[1] * dims[2]
    
    read_data = fread(fileobj, size, datatype)
    read_data = read_data.reshape(dims)
    
    fileobj.close()
    
    return read_data


def regrid(data,in_lat,in_lon,oldgrid):
    """Takes input data and regrids to a 2.5 degree global grid"""
    
#    len_test_lat = (len(in_lat) == 73)
#    len_test_lon = (len(in_lon) == 144)
#    start_test_lat = (in_lat[0] > in_lat[-1])
#    
#    if len_test_lat and len_test_lon and start_test_lat:  # no change - correct input
#        print 'no regridding...'
#	new_data = data
#	latitude = in_lat
#	longitude = in_lon
#	
#    elif len_test_lat and len_test_lon:  # flip latitude axis only
#        print 'flip latitude axis...'
#        new_data = data[:,::-1,:]
#	latitude = in_lat[::-1]
#	longitude = in_lon
#    
#    else:
#        print 'regridding...'
    
    #tnf_xy_onelevel.run requires North to South latitude axis
    latitude = cdms2.createAxis(numpy.arange(90,-92.5,-2.5,'f'),id='latitude') #-90,92.5,2.5

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
    

def write_netcdf(fname_out,waf_data_ns,time_axis,lat_axis,lon_axis,sourcefile_text,outvar):
    """Writes the output netcdf file"""
    
    outfile = netCDF4.Dataset(fname_out, 'w', format='NETCDF3_CLASSIC')   ## Found error using cdo on abyss with format='NETCDF4' 
    
    # Global attributes #

    setattr(outfile,'Title','Calculated wave activity flux from U wind, V wind and geopotential height')
    setattr(outfile,'Contact','Damien Irving (d.irving@student.unimelb.edu.au)')
    setattr(outfile,'Reference','Takaya & Nakamura (2001) J. Atmos. Sci., 58, 608-627')
    setattr(outfile,'Sourcefiles',sourcefile_text)
    setattr(outfile,'history','%s: Created using %s, format=NETCDF3_CLASSIC' %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), sys.argv[0])) 

    # Dimensions #

    outfile.createDimension('time',None)
    outfile.createDimension('latitude',len(lat_axis))
    outfile.createDimension('longitude',len(lon_axis))

    times = outfile.createVariable('time','f4',('time',))
    lats = outfile.createVariable('latitude','f4',('latitude',))
    lons = outfile.createVariable('longitude','f4',('longitude',))

    for att_name in time_axis.attributes.keys():
        setattr(times, att_name, time_axis.attributes[att_name])
    for att_name in lat_axis.attributes.keys():
        setattr(lats, att_name, lat_axis.attributes[att_name])
    for att_name in lon_axis.attributes.keys():
        setattr(lons, att_name, lon_axis.attributes[att_name])           

    # Variable #

    out_data = outfile.createVariable(outvar,'f4',('time','latitude','longitude',),fill_value=9.999e+20)
    setattr(out_data, 'standard_name', outvar)
    setattr(out_data, 'units', 'm2 s-2')
    setattr(out_data, 'name', 'Wave activity flux, %s component' %(outvar[-1]))
    setattr(out_data, 'missing_value', 9.999e+20) 
    setattr(out_data, 'history', 'Calculated wave activity flux from U wind, V wind and geopotential height')
    
    waf_data_ns = waf_data_ns.astype(numpy.float32)
    
    #reshape output data so latitude axis is south to north
    times[:] = time_axis         
    lats[:] = lat_axis[::-1]           
    lons[:] = lon_axis 
    out_data[:] = waf_data_ns[:,::-1,:]
    
    outfile.close()
    

def apply_mask(input_data,input_clim_u,time_axis):
    """Apply mask, because WAF only valid where the climatological mean flow is westerly"""  
    
    # Get the time axis info #

    time_data = time_axis.asComponentTime()
    months = []
    for ii in range(0,len(time_data)):
	months.append(int(str(time_data[ii]).split('-')[1]))
    
    # Expand input climatology to match size of input data (with correct month matching) #

    ntime,nlat,nlon = numpy.shape(input_data)
    input_clim_u_expanded = numpy.ma.ones([ntime,nlat,nlon]) * 9.999e+20
    for i in range(0,ntime):
	month_index = months[i]
	input_clim_u_expanded[i,:,:] = input_clim_u[month_index-1,:,:]
    
    # Define the mask #
    
    mask_u = numpy.where(input_clim_u_expanded > 1.0, 0, 1)   # exclude points where climtological wind has easterly component
    mask_inf = numpy.isinf(input_data)                        # exclude infinity values
    mask_nan = numpy.isnan(input_data)                        # exclude NaN values
    
    mask = numpy.sum([mask_u,mask_inf,mask_nan],axis=0)
    
    # Apply the mask #
    
    input_data_masked = MV2.array(numpy.ma.masked_array(input_data, mask=mask))
    
    return input_data_masked


def read_data(fname,vname):
    """Reads the data from a typical input file"""
    
    infile = cdms2.open(fname)
    
    data = infile(vname,order='tyx')  
    time = data.getTime()
    lat = data.getLatitude()
    lon = data.getLongitude()

    infile.close()

    return data,time,lat,lon
    

def main(fname_u, fname_uclim, vname_u, fname_v, fname_vclim, vname_v, fname_zg, fname_zgclim, vname_zg, fname_wafx, fname_wafy):
    """Run the program"""

    ### Read the input data ###

    ## u wind, v wind, zg ##
    
    data_u,time_u,lat_u,lon_u = read_data(fname_u,vname_u)
    data_v,time_v,lat_v,lon_v = read_data(fname_v,vname_v)
    data_zg,time_zg,lat_zg,lon_zg = read_data(fname_zg,vname_zg)

    ### Check that the input data are all on the same coordinate axes ###

    ## Time ##

    time_axis_check(time_u, time_v)
    time_axis_check(time_u, time_zg)
    
    ## Latitude ##
        
    xy_axis_check(lat_u, lat_v)
    xy_axis_check(lat_u, lat_zg)

    ## Longitude ##
    
    xy_axis_check(lon_u, lon_v)
    xy_axis_check(lon_u, lon_zg)

    ## Find grid characteristics ##

    ntime, nlat, nlon = numpy.shape(data_u)
    input_grid = data_u.getGrid() 
    
    ## u wind, v wind, zg climatology ##
    
    data_uclim = read_climatology(fname_uclim,vname_u,nlat,nlon)  
    data_vclim = read_climatology(fname_vclim,vname_v,nlat,nlon)
    data_zgclim = read_climatology(fname_zgclim,vname_zg,nlat,nlon)
    
    
    ### Regrid the data ###
    
    data_u_regrid, lat_regrid, lon_regrid = regrid(data_u,lat_u,lon_u,input_grid)
    data_uclim_regrid, lat_regrid, lon_regrid = regrid(data_uclim,lat_u,lon_u,input_grid)
    
    data_v_regrid, lat_regrid, lon_regrid = regrid(data_v,lat_u,lon_u,input_grid)
    data_vclim_regrid, lat_regrid, lon_regrid = regrid(data_vclim,lat_u,lon_u,input_grid)
    
    data_zg_regrid, lat_regrid, lon_regrid = regrid(data_zg,lat_u,lon_u,input_grid)
    data_zgclim_regrid, lat_regrid, lon_regrid = regrid(data_zgclim,lat_u,lon_u,input_grid)
   
    
    ### Create the binary data files for input into the Fortran wap script ### 
    
    write_binary(data_u_regrid,'u.bin')
    write_binary(data_uclim_regrid,'uclim.bin')
    write_binary(data_v_regrid,'v.bin')
    write_binary(data_vclim_regrid,'vclim.bin')
    write_binary(data_zg_regrid,'zg.bin')
    write_binary(data_zgclim_regrid,'zgclim.bin')

    
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
    
    wafx_data_ns = read_binary('wafx.bin',[ntime,73,144])
    wafy_data_ns = read_binary('wafy.bin',[ntime,73,144])    
        
    wafx_data_ns_masked = apply_mask(wafx_data_ns,data_uclim_regrid,time_u)
    wafy_data_ns_masked = apply_mask(wafy_data_ns,data_uclim_regrid,time_u)
  
    sourcefile_text = '%s, %s, %s, %s, %s, %s' %(fname_u, fname_uclim, fname_v, fname_vclim, fname_zg, fname_zgclim)
    
    write_netcdf(fname_wafx,wafx_data_ns_masked,time_u,lat_regrid,lon_regrid,sourcefile_text,'wafx')
    write_netcdf(fname_wafy,wafy_data_ns_masked,time_u,lat_regrid,lon_regrid,sourcefile_text,'wafy')

    
    ### Clean up ###
    
    os.system("rm answers.txt zg.bin zgclim.bin u.bin uclim.bin v.bin vclim.bin wafx.bin wafy.bin")


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
	    global 2.5 by 2.5 deg grid (i.e. 73 lats, 144 lons).
	    It is hard wired that the input data is from the 250 hPa level.
	    It is assumed that the input data is three dimensional (time, lat, lon). 
	
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
	print 'Ouput wafy: ', args[10]

    fname_u, fname_uclim, vname_u, fname_v, fname_vclim, vname_v, fname_zg, fname_zgclim, vname_zg, fname_wafx, fname_wafy = args  
    
    main(fname_u,fname_uclim,vname_u,fname_v,fname_vclim,vname_v,fname_zg,fname_zgclim,vname_zg,fname_wafx,fname_wafy)
