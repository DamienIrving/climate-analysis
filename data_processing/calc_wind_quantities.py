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

import sys
import os

import argparse

import numpy

import cdms2
import cdutil

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio

## The current release of UV-CDAT doesn't have the windspharm.cdms module (the latest version does)
#from windspharm.cdms import VectorWind
from windspharm.standard import VectorWind
from windspharm.tools import prep_data, recover_data, order_latdim


var_atts = {}

var_atts['magnitude'] = {'id': 'spd',
    'long_name': 'wind speed',
    'units': 'm s-1',
    'history': 'windspharm magnitude() function - http://ajdawson.github.com/windspharm/index.html'}

var_atts['vorticity'] = {'id': 'vrt',
    'long_name': 'relative vorticity',
    'units': 's-1',   
    'history': 'windspharm vorticity(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['divergence'] = {'id': 'div',
    'long_name': 'divergence',
    'units': 's-1',   
    'history': 'windspharm divergence(), http://ajdawson.github.com/windspharm/index.html'}

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
    'long_name': 'Rossby wave source',
    'units': '1.e-11 s-1',  # I think it should be s-2
    'history': 'calculated using windspharm - http://ajdawson.github.com/windspharm/index.html'}



def calc_quantity(data_u, data_v, quantity):
    """Calculates a single wind quantity using windspharm (ajdawson.github.com/windspharm/index.html)"""
    
    # Do all the data preparation, because I'm using the windspharm.standard instead of
    # windspharm.cdms (when the latter is included in the UV-CDAT release, I should use it
    # because it makes the code much simplier)    

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
    
    assert isinstance(data_u, nio.InputData)
    assert isinstance(data_v, nio.InputData)
    
    uwnd = data_u.data[:]
    vwnd = data_v.data[:]
    
    lons = data_u.data.getLongitude()[:]
    lats = data_u.data.getLatitude()[:]
    
    # The standard interface requires that latitude and longitude be the leading
    # dimensions of the input wind components, and that wind components must be
    # either 2D or 3D arrays. The data read in is 4D and has latitude and
    # longitude as the last dimensions. The bundled tools can make the process of
    # re-shaping the data a lot easier to manage.
    uwnd, uwnd_info = prep_data(uwnd, uwnd.getOrder())  
    vwnd, vwnd_info = prep_data(vwnd, vwnd.getOrder()) 

    # It is also required that the latitude dimension is north-to-south. Again the
    # bundled tools make this easy.
    lats, uwnd, vwnd = order_latdim(lats, uwnd, vwnd)
    flip = False if (lats[0] == data_u.data.getLatitude()[0]) else True   # Flag to see if lats was flipped 

    # Create a VectorWind instance (squeeze works around a bug in the code).
    uwnd = uwnd.squeeze()
    vwnd = vwnd.squeeze()
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
	data_out['u'], data_out['v'] = w.irrotationalcomponent()    
    
    elif quantity == 'nondivergentcomponent':
        data_out = {}
	data_out['u'], data_out['v'] = w.nondivergentcomponent() 
    
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
        for comp in ['u', 'v']:
	    data_out[comp] = recover_data(data_out[comp], uwnd_info)
	    if flip:
	        data_out[comp] = numpy.fliplr(data_out[comp])   #data_out[comp][:, ::-1, :]    
    else:
	data_out = recover_data(data_out, uwnd_info)
	if flip:
	    data_out = numpy.fliplr(data_out)  #data_out[:, ::-1, :]

#    if eddy:
#        data_out_zonal_ave = cdutil.averager(data_out, axis='2')
#	print numpy.shape(data_out_zonal_ave)
#	
#	data_out = numpy.subtract(data_out, numpy.resize(data_out_zonal_ave, numpy.shape(data_out)))

    return data_out

    
def main(inargs):
    """Run the program"""

    # Read the input data #

    data_u = nio.InputData(inargs.infileu, inargs.varu, **nio.dict_filter(vars(inargs), ['time', 'region']))
    data_v = nio.InputData(inargs.infilev, inargs.varv, **nio.dict_filter(vars(inargs), ['time', 'region']))

    # Check that the input data are all on the same coordinate axes #

    nio.xy_axis_check(data_u.data.getLatitude(), data_v.data.getLatitude())
    nio.xy_axis_check(data_u.data.getLongitude(), data_v.data.getLongitude())
    if 't' in data_u.data.getOrder():
        nio.time_axis_check(data_u.data.getTime(), data_v.data.getTime())
    
    # Calculate the desired quantity #
    
    data_out = calc_quantity(data_u, data_v, inargs.quantity)

    # Write output file #

    indata_list = [data_u, data_v,]
    if type(data_out) == dict:
        outdata_list = [data_out['u'], data_out['v'],]
        outvar_atts_list = [var_atts[inargs.quantity, 'u'], var_atts[inargs.quantity, 'v'],]
	outvar_axes_list = [data_u.data.getAxisList(),data_u.data.getAxisList(),]
    else:
        outdata_list = [data_out,]
        outvar_atts_list = [var_atts[inargs.quantity],]
        outvar_axes_list = [data_u.data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, inargs.quantity, 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)

    
if __name__ == '__main__':

    extra_info ="""	
wind quantities: 
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
	    
note:
  The input data can have no missing values

reference:
  Uses the windspharm package: http://ajdawson.github.com/windspharm/intro.html

example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_wind_quantities.py streamfunction  
  /work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc ua
  /work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc va
  /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly_native.nc

  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_wind_quantities.py streamfunction  
  /work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc ua
  /work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc va
  /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc

author:
  Damien Irving, 10 Dec 2012.

bugs:
  Rossby wave source output needs to be checked
  Some of the if statements are fairly ugly - need to clean those up
    
"""

    description='Calculate wind derived quanitity.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("quantity", type=str, help="Quantity to calculate",
                        choices=['magnitude', 'vorticity', 'divergence', 'absolutevorticity',
                                 'irrotationalcomponent', 'nondivergentcomponent', 'streamfunction', 
				 'velocitypotential', 'rossbywavesource'])
    parser.add_argument("infileu", type=str, help="Input U-wind file name")
    parser.add_argument("varu", type=str, help="Input U-wind variable")
    parser.add_argument("infilev", type=str, help="Input V-wind file name")
    parser.add_argument("varv", type=str, help="Input V-wind variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate EOF [default = entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to calculate the EOF [default = entire]")
#    parser.add_argument("--eddy", action="store_true", default=False,
#                        help="return the eddy component of the wind quantity (i.e. remove the zonal mean before calculation)")
    
    args = parser.parse_args()  
    
    print 'Quantity:', args.quantity
    print 'Input U file: ', args.infileu
    print 'Input V file: ', args.infilev
    print 'Output file:', args.outfile

    main(args)
