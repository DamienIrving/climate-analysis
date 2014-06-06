"""
Filename:     calc_wind_quantities.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Takes the U and V wind and calculates various wind quantities
Reference:    Uses the windspharm package: ajdawson.github.com/windspharm/index.html

"""

# Import general Python modules #

import sys, os
import argparse
import numpy
from windspharm.cdms import VectorWind

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import netcdf_io as nio
    import coordinate_rotation as rot
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')



var_atts = {}

var_atts['magnitude'] = {'id': 'spd',
    'standard_name': 'wind_speed',
    'long_name': 'Wind Speed',
    'units': 'm s-1',
    'history': 'windspharm magnitude() function - http://ajdawson.github.com/windspharm/index.html'}

var_atts['vorticity'] = {'id': 'vrt',
    'standard_name': 'relative_vorticity',
    'long_name': 'Relative Vorticity',
    'units': 's-1',   
    'history': 'windspharm vorticity(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['divergence'] = {'id': 'div',
    'standard_name': 'divergence',
    'long_name': 'Divergence',
    'units': '1.e-6 s-1',   
    'history': 'windspharm divergence(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['absolutevorticity'] = {'id': 'avrt',
    'standard_name': 'absolute_vorticity',
    'long_name': 'Absolute Vorticity (sum of relative and planetary)',
    'units': '1.e-5 s-1',
    'history': 'windspharm absolutevorticity(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['planetaryvorticity'] = {'id': 'pvrt',
    'standard_name': 'planetary_vorticity',
    'long_name': 'Planetary Vorticity (Coriolis parameter)',
    'units': 's-1',
    'history': 'windspharm planetaryvorticity(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['irrotationalcomponent','u'] = {'id': 'uchi',
    'standard_name': 'irrotational_zonal_wind',
    'long_name': 'Zonal irrotational (divergent) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['irrotationalcomponent','v'] = {'id': 'vchi',
    'standard_name': 'irrotational_meridional_wind',
    'long_name': 'Meridional irrotational (divergent) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent() - http://ajdawson.github.com/windspharm/index.html'}

var_atts['nondivergentcomponent','u'] = {'id': 'upsi',
    'standard_name': 'non_divergent_zonal_wind',
    'long_name': 'Zonal non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['nondivergentcomponent','v'] = {'id': 'vpsi',
    'standard_name': 'non-divergent meridional wind',
    'long_name': 'meridional non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)',
    'units': 'm s-1',
    'history': 'windspharm irrotationalcomponent(), http://ajdawson.github.com/windspharm/index.html'}

var_atts['streamfunction'] = {'id': 'sf',
    'standard_name': 'streamfunction',
    'long_name': 'Streamfunction (rotational wind blows along streamfunction contours, speed proportional to gradient)',
    'units': '1.e+6 m2 s-1',  
    'history': 'windspharm streamfunction() - http://ajdawson.github.com/windspharm/index.html'}

var_atts['velocitypotential'] = {'id':'vp',
    'standard_name': 'velocity_potential',
    'long_name': 'Velocity Potential (divergent wind blows along velocity potential contours, speed proportional to gradient)',
    'units': '1.e+6 m2 s-1',  
    'history': 'windspharm velocitypotential() - http://ajdawson.github.com/windspharm/index.html'}

var_atts['rossbywavesource'] = {'id': 'rws',
    'standard_name': 'rossby_wave_source',
    'long_name': 'Rossby Wave Source',
    'units': '1.e-11 s-2',  
    'history': 'calculated using windspharm - http://ajdawson.github.com/windspharm/index.html'}

var_atts['rossbywavesource1'] = {'id': 'rws1',
    'standard_name': 'rossby_wave_source_vortex',
    'long_name': 'Rossby wave source, vortex stretching term',
    'units': '1.e-11 s-2',  
    'history': 'calculated using windspharm - http://ajdawson.github.com/windspharm/index.html'}

var_atts['rossbywavesource2'] = {'id': 'rws2',
    'standard_name': 'rossby_wave_source_advection',
    'long_name': 'Rossby wave source, advection of absolute vorticity by divergent flow term',
    'units': '1.e-11 s-2',  
    'history': 'calculated using windspharm - http://ajdawson.github.com/windspharm/index.html'}


def calc_quantity(uwnd, vwnd, quantity):
    """Calculates a single wind quantity using windspharm (ajdawson.github.com/windspharm/index.html)"""
    
    uwnd = uwnd.squeeze()
    vwnd = vwnd.squeeze()
    w = VectorWind(uwnd, vwnd)

    # Compute the desired quantity. Also use the bundled tools to re-shape the 
    # outputs to the 4D shape of the wind components as they were read off files.
    
    if quantity == 'rossbywavesource':
	# Compute components of rossby wave source: absolute vorticity, divergence,
	# irrotational (divergent) wind components, gradients of absolute vorticity.
	
	eta = w.absolutevorticity()
	div = w.divergence()
	uchi, vchi = w.irrotationalcomponent()
	etax, etay = w.gradient(eta)

	# Combine the components to form the Rossby wave source term
        data_out = {}
	data_out['rws1'] = (-eta * div) / (1.e-11)
        data_out['rws2'] = (-(uchi * etax + vchi * etay)) / (1.e-11)
        data_out['rws'] = data_out['rws1'] + data_out['rws2']

    elif quantity == 'magnitude':
        data_out = w.magnitude()
    
    elif quantity == 'vorticity':
        data_out = w.vorticity()
    
    elif quantity == 'divergence':
        data_out = w.divergence()
	data_out = data_out / (1.e-6)
    
    elif quantity == 'absolutevorticity':
        data_out = w.absolutevorticity()
	data_out = data_out / (1.e-5)
    
    elif quantity == 'absolutevorticitygradient':
        avrt = w.absolutevorticity()
	ugrad, vgrad = w.gradient(avrt)
	data_out = numpy.sqrt(numpy.square(ugrad) + numpy.square(vgrad)) 
	data_out = data_out / (1.e-5)
    
    elif quantity == 'planetaryvorticity':
        data_out = w.planetaryvorticity()
    
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


    return data_out

    
def main(inargs):
    """Run the program"""

    # Read the input data #

    data_u = nio.InputData(inargs.infileu, inargs.varu, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude']))
    data_v = nio.InputData(inargs.infilev, inargs.varv, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude']))

    # Check that the input data are all on the same coordinate axes #

    nio.xy_axis_check(data_u.data.getLatitude(), data_v.data.getLatitude())
    nio.xy_axis_check(data_u.data.getLongitude(), data_v.data.getLongitude())
    if 't' in data_u.data.getOrder():
        nio.time_axis_check(data_u.data.getTime(), data_v.data.getTime())
    
    # Calculate the desired quantity #
    
    data_out = calc_quantity(data_u.data, data_v.data, inargs.quantity)

    # Write output file #

    indata_list = [data_u, data_v,]
    if (type(data_out) == dict) and ('u' in data_out.keys()):
        outdata_list = [data_out['u'], data_out['v'],]
        outvar_atts_list = [var_atts[inargs.quantity, 'u'], var_atts[inargs.quantity, 'v'],]
	outvar_axes_list = [data_u.data.getAxisList()] * 2
    elif (type(data_out) == dict) and ('rws' in data_out.keys()):
        outdata_list = [data_out['rws'], data_out['rws1'], data_out['rws2']]
        outvar_atts_list = [var_atts['rossbywavesource'], 
	                    var_atts['rossbywavesource1'],
			    var_atts['rossbywavesource2']]
	outvar_axes_list = [data_u.data.getAxisList()] * 3
    else:
        outdata_list = [data_out,]
        outvar_atts_list = [var_atts[inargs.quantity],]
        outvar_axes_list = [data_u.data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     data_u.global_atts, 
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
  rossbywavesource      ->  Rossby wave source (includes the vortex stretching and advection of absolute vorticity by divergent flow terms)
  		      	    
	    
note:
  The input data can have no missing values

reference:
  Uses the windspharm package: http://ajdawson.github.com/windspharm/intro.html

example (vortex.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.3.0/bin/cdat calc_wind_quantities.py streamfunction  
  ua_Merra_250hPa_monthly_native.nc ua
  va_Merra_250hPa_monthly_native.nc va
  sf_Merra_250hPa_monthly_native.nc

author:
  Damien Irving, d.irving@student.unimelb.edu.au

    
"""

    description='Calculate wind derived quanitity.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("quantity", type=str, help="Quantity to calculate",
                        choices=['magnitude', 'vorticity', 'divergence', 'absolutevorticity', 
			         'absolutevorticitygradient', 'planetaryvorticity',
                                 'irrotationalcomponent', 'nondivergentcomponent', 
				 'streamfunction', 'velocitypotential', 'rossbywavesource'])
    parser.add_argument("infileu", type=str, help="Input U-wind file name")
    parser.add_argument("varu", type=str, help="Input U-wind variable")
    parser.add_argument("infilev", type=str, help="Input V-wind file name")
    parser.add_argument("varv", type=str, help="Input V-wind variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region [default = entire]")
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Longitude range [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    args = parser.parse_args()  
    
    print 'Quantity:', args.quantity
    print 'Input U file: ', args.infileu
    print 'Input V file: ', args.infilev
    print 'Output file:', args.outfile

    main(args)
