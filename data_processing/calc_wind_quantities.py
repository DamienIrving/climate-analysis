#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:     calc_wind_quantities.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Takes the U and V wind and calculates various wind quantities
Reference:    Uses the windspharm package: ajdawson.github.com/windspharm/index.html

Updates | By | Description
--------+----+------------
11 December 2012 | Damien Irving | Initial version.

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
import cdutil

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

## The current release of UV-CDAT doesn't have the windspharm.cdms module (the latest version does)
#from windspharm.cdms import VectorWind
from windspharm.standard import VectorWind
from windspharm.tools import prep_data, recover_data, order_latdim



### Define globals ###

var_atts = {}

var_atts['magnitude'] = {'id': 'spd',
    'name': 'wind speed',
    'units': 'm s-1',
    'history': 'windspharm magnitude() function - http://ajdawson.github.com/windspharm/index.html'}

var_atts['vorticity'] = {'id': 'vrt',
    'name': 'relative vorticity',
    'units': 's-1',   
    'history': 'windspharm vorticity(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['absolutevorticity'] = {'id': 'avrt',
    'name': 'absolute vorticity',
    'long_name': 'absolute vorticity (sum of relative and planetary)',
    'units': 's-1',
    'history': 'windspharm absolutevorticity(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['irrotationalcomponent','u'] = {'id': 'uchi',
    'name': 'irrotational zonal wind',
    'long_name': 'zonal irrotational (divergent) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['irrotationalcomponent','v'] = {'id': 'vchi',
    'name': 'irrotational meridional wind',
    'long_name': 'meridional irrotational (divergent) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent() - http://ajdawson.github.com/windspharm/index.html'}

var_atts['nondivergentcomponent','u'] = {'id': 'upsi',
    'name': 'non-divergent zonal wind',
    'long_name': 'zonal non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['nondivergentcomponent','v'] = {'id': 'vpsi',
    'name': 'non-divergent meridional wind',
    'long_name': 'meridional non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['streamfunction'] = {'id': 'sf',
    'name': 'streamfunction',
    'long_name': 'streamfunction (rotational wind blows along streamfunction contours, speed proportional to gradient)',
    'units': '1.e+6 m2 s-1',  #m2 s-1
    'history': 'windspharm streamfunction() - http://ajdawson.github.com/windspharm/index.html'}

var_atts['velocitypotential'] = {'id':'vp',
    'name': 'velocity potential',
    'long_name': 'velocity potential (divergent wind blows along velocity potential contours, speed proportional to gradient)',
    'units': '1.e+6 m2 s-1',  #m2 s-1,
    'history': 'windspharm velocitypotential() - http://ajdawson.github.com/windspharm/index.html'}

var_atts['rossbywavesource'] = {'id': 'rws',
    'name': 'Rossby wave source',
    'units': '1.e-11 s-1',  # I think it should be s-2
    'history': 'calculated using windspharm - http://ajdawson.github.com/windspharm/index.html'}



### Define functions ###


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


def calc_quantity(data_u, data_v, time_u, lat_u, lon_u, quantity, eddy):
    """Calculates a single wind quantity using windspharm (ajdawson.github.com/windspharm/index.html)"""
    
    # Do all the data preparation, because I'm using the windspharm.standard instead of
    # windspharm.cdms (when the latter is included in the UV-CDAT release, I should use it
    # because it makes the code much simplier    

#    if eddy:
#        uwnd_zonal_ave = cdutil.averager(data_u, axis='x')
#        vwnd_zonal_ave = cdutil.averager(data_v, axis='x')
#	
#	print numpy.shape(data_u)
#	print numpy.shape(uwnd_zonal_ave)
#	
#	eddy_uwnd = numpy.subtract(data_u, numpy.resize(uwnd_zonal_ave, numpy.shape(data_u)))
#	eddy_vwnd = numpy.subtract(data_v, numpy.resize(vwnd_zonal_ave, numpy.shape(data_v)))
#	
#	print numpy.shape(eddy_uwnd)
#	
#	uwnd = eddy_uwnd[:]
#	vwnd = eddy_uwnd[:]
#    else:
    
    
    uwnd = data_u[:]
    vwnd = data_v[:]
    
    lons = lon_u[:]
    lats = lat_u[:]
    
    # The standard interface requires that latitude and longitude be the leading
    # dimensions of the input wind components, and that wind components must be
    # either 2D or 3D arrays. The data read in is 4D and has latitude and
    # longitude as the last dimensions. The bundled tools can make the process of
    # re-shaping the data a lot easier to manage.
    uwnd, uwnd_info = prep_data(uwnd, 'tyx')#'tzyx')
    vwnd, vwnd_info = prep_data(vwnd, 'tyx')#'tzyx')

    # It is also required that the latitude dimension is north-to-south. Again the
    # bundled tools make this easy.
    lats, uwnd, vwnd = order_latdim(lats, uwnd, vwnd)
    flip = False if (lats[0] == lat_u[0]) else True   # Flag to see if lats was flipped 

    # Create a VectorWind instance to handle the computation of streamfunction and
    # velocity potential.
    w = VectorWind(uwnd, vwnd)

    # Compute the desired quantity. Also use the bundled tools to re-shape the 
    # outputs to the 4D shape of the wind components as they were read off files.
    
    if quantity == 'rossbywavesource':   ## FIX THIS HUGE IF STATEMENT - A CLASS MIGHT BE THE ANSWER!!!
	# Compute components of rossby wave source: absolute vorticity, divergence,
	# irrotational (divergent) wind components, gradients of absolute vorticity.
	eta = w.absolutevorticity()
	div = w.divergence()
	uchi, vchi = w.irrotationalcomponent()
	etax, etay = w.gradient(eta)

	# Combine the components to form the Rossby wave source term.
	data_out = -eta * div - uchi * etax + vchi * etay	
	data_out = data_out / (1.e-11)

    elif quantity == 'magnitude':
        data_out = w.magnitude()
    
    elif quantity == 'vorticity':
        data_out = w.vorticity()
    
    elif quantity == 'divergence':
        data_out = w.divergence()
    
    elif quantity == 'absolutevorticity':
        data_out = w.absolutevorticity()
    
    elif quantity == 'irrotationalcomponent':
        data_out = {}
	data_out['u'],data_out['v'] = w.irrotationalcomponent()    
    
    elif quantity == 'nondivergentcomponent':
        data_out = {}
	data_out['u'],data_out['v'] = w.nondivergentcomponent() 
    
    elif quantity == 'streamfunction':
        data_out = w.streamfunction()
	data_out = data_out / (1.e+6)
    
    elif quantity == 'velocitypotential':
        data_out = w.velocitypotential()
    	data_out = data_out / (1.e+6)
	
    else:
	sys.exit('Wind quantity not recognised')
    
    # Put the data back together #
   
    if quantity == 'irrotationalcomponent' or quantity == 'nondivergentcomponent':
        for comp in ['u','v']:
	    data_out[comp] = recover_data(data_out[comp], uwnd_info)
	    if flip:
	        data_out[comp] = data_out[comp][:,::-1,:]    
    else:
	data_out = recover_data(data_out, uwnd_info)
	if flip:
	    data_out = data_out[:,::-1,:]

    if eddy:
        data_out_zonal_ave = cdutil.averager(data_out, axis='2')
	print numpy.shape(data_out_zonal_ave)
	
	data_out = numpy.subtract(data_out, numpy.resize(data_out_zonal_ave, numpy.shape(data_out)))


    return data_out



def write_outfile(quantity, fname_u, fname_v, fname_out, infile_u, data_out, data_u, time_u, lat_u, lon_u):
    """Writes output netCDF file"""
    
    outfile = cdms2.open(fname_out,'w')
    
    # Global attributes #
    
    for att_name in infile_u.attributes.keys():
        if att_name != "history":
            setattr(outfile, att_name, infile_u.attributes[att_name])
    
    old_history = infile_u.attributes['history'] if ('history' in infile_u.attributes.keys()) else ''
    
    if quantity == 'irrotationalcomponent' or quantity == 'nondivergentcomponent':
        qname = var_atts[quantity,'u']['name']+' and '+var_atts[quantity,'v']['name']
    else:
        qname = var_atts[quantity]['name']
    
    setattr(outfile, 'history', """%s: %s calculated from %s and %s using %s, format=NETCDF3_CLASSIC\n%s""" %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
            qname,fname_u,fname_v,sys.argv[0],old_history))
    
    
    # Variables #

    axisInTime = outfile.copyAxis(time_u)
    axisInLat = outfile.copyAxis(lat_u)  
    axisInLon = outfile.copyAxis(lon_u)  
    
    if quantity == 'irrotationalcomponent' or quantity == 'nondivergentcomponent':  ## FIX THIS UGLY IF STATEMENT
        for comp in ['u','v']:
	    var = data_out[comp]
	    var = cdms2.MV2.array(var)
	    var = var.astype(numpy.float32)
	    var.setAxisList([axisInTime,axisInLat,axisInLon])

	    for key, value in var_atts[quantity,comp].iteritems():
        	if key == 'history':
		    old_history = data_u.attributes['history'] if ('history' in data_u.attributes.keys()) else ''
		    new_history = value+'. '+old_history
		    setattr(var, key, new_history)
		else:
		    setattr(var, key, value)
	    outfile.write(var)  
    else:
	var = data_out
	var = cdms2.MV2.array(var)
	var = var.astype(numpy.float32)
	var.setAxisList([axisInTime,axisInLat,axisInLon])

	for key, value in var_atts[quantity].iteritems():
            if key == 'history':
		old_history = data_u.attributes['history'] if ('history' in data_u.attributes.keys()) else ''
		new_history = value+'. '+old_history
		setattr(var, key, new_history)
	    else:
		setattr(var, key, value)
	
	outfile.write(var)  

    outfile.close()

    
def main(quantity, fname_u, vname_u, fname_v, vname_v, fname_out, eddy):
    """Run the program"""

    ## Read the input data ##

    # U wind #
    infile_u = cdms2.open(fname_u)
    data_u = infile_u(vname_u,order='tyx')

    # V wind #
    infile_v = cdms2.open(fname_v)
    data_v = infile_v(vname_v,order='tyx')


    ## Check that the input data are all on the same coordinate axes ##

    # Time #
    time_u = data_u.getTime()
    time_v = data_v.getTime()
    
    time_axis_check(time_u, time_v)
    
    # Latitude #
    lat_u = data_u.getLatitude()
    lat_v = data_v.getLatitude()

    xy_axis_check(lat_u, lat_v)

    # Longitude #
    lon_u = data_u.getLongitude()
    lon_v = data_v.getLongitude()

    xy_axis_check(lon_u, lon_v)

    
    ## Calculate the desired quantity ##
    
    data_out = calc_quantity(data_u, data_v, time_u, lat_u, lon_u, quantity, eddy)

    
    ## Write the output file ##
    
    write_outfile(quantity, fname_u, fname_v, fname_out, infile_u, data_out, data_u, time_u, lat_u, lon_u)

    ## Clean up ##
        
    infile_u.close()
    infile_v.close()
    

if __name__ == '__main__':

    ## Help and manual information ##

    usage = "usage: %prog [options] {wind_quantity} {input_U_file} {input_U_variable} {input_V_file} {input_V_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual", action="store_true", dest="manual", default=False,
                      help="output a detailed description of the program")
    parser.add_option("-e", "--eddy", action="store_true", dest="eddy", default=False,
                      help="return the eddy component of the wind quantity (i.e. remove the zonal mean")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            calc_eof.py [-M] [-h] [-e] {wind_quantity} {input_U_file} {input_U_variable} {input_V_file} {input_V_variable} {output_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -e -> Return the eddy component of the wind quantity
	          (i.e. remove the zonal mean from U and V before calculation) 
        
	Wind quantities 
	    magnitude             ->  Wind speed    
	    vorticity             ->  Relative vorticity
	    divergence            ->  Horizontal divergence
	    absolutevorticity     ->  Absolute vorticity (sum of relative and planetary)
	    irrotationalcomponent ->  Irrotational (divergent) component of the vector wind (from Helmholtz decomposition)
	    nondivergentcomponent ->  Non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)
	    streamfunction        ->  Streamfunction (the rotational part of the wind blows along the streamfunction contours, 
	                              with speed proportional to the gradient)
	    velocitypotential     ->  Velocity potential (the divergent part of the wind blows along the velocity potential contours,
	                              with speed proportional to the gradient)
	    rossbywavesource      ->  Rossby wave source			      	    
	    
	Note
	    The input data can have no missing values
	
        Reference
            Uses the windspharm package: http://ajdawson.github.com/windspharm/intro.html

        Example (abyss.earthsci.unimelb.edu.au)
	    /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_wind_quantities.py streamfunction  
	    /work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc ua
	    /work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc va
	    /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly_native.nc
	    
	    /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_wind_quantities.py streamfunction  
	    /work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc ua
	    /work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc va
	    /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc
	    
        Author
            Damien Irving, 10 Dec 2012.

        Bugs
            Rossby wave source output needs to be checked
	    Some of the if statements are fairly ugly - need to clean those up
	    Please report any problems to: d.irving@student.unimelb.edu.au
        """
        sys.exit(0)

    else:

        # Repeat the command line arguments #

        print 'Quantity:', args[0]
	print 'Input U file: ', args[1]
        print 'Input V file: ', args[3]
	print 'Output file:', args[5]
        
        quantity, fname_u, vname_u, fname_v, vname_v, fname_out = args  
    
        main(quantity, fname_u, vname_u, fname_v, vname_v, fname_out, options.eddy)
