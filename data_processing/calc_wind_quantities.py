"""
Filename:     calc_wind_quantities.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Takes the U and V wind and calculates various wind quantities
Reference:    Uses the windspharm package: ajdawson.github.com/windspharm/index.html

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, xray
from windspharm.standard import VectorWind
from windspharm.tools import prep_data, recover_data, order_latdim

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define global variables and functions

var_atts = {'spd': {'standard_name': 'wind_speed',
        'long_name': 'wind_speed',
        'units': 'm s-1'},
    'vrt': {'standard_name': 'relative_vorticity',
        'long_name': 'relative_vorticity',
        'units': 's-1'},
    'div': {'standard_name': 'divergence',
        'long_name': 'divergence',
        'units': '1.e-6 s-1'},
    'avrt': {'standard_name': 'absolute_vorticity',
        'long_name': 'absolute_vorticity',
        'units': '1.e-5 s-1',
        'notes': 'absolute vorticity = sum of relative and planetary vorticity'},
    'avrtgrad': {'standard_name': 'absolute_vorticity_gradient',
        'long_name': 'absolute_vorticity_gradient',
        'units': '1.e-5 s-1',
        'notes': 'absolute vorticity = sum of relative and planetary vorticity'},
    'pvrt': {'standard_name': 'planetary_vorticity',
        'long_name': 'planetary_vorticity',
        'units': 's-1',
        'notes': 'planetary vorticity = Coriolis parameter'},
    'uchi' : {'standard_name': 'irrotational_zonal_wind',
        'long_name': 'irrotational_zonal_wind',
        'units': 'm s-1',
        'notes': 'Zonal irrotational (divergent) component of the vector wind (from Helmholtz decomposition)'},
    'vchi': {'standard_name': 'irrotational_meridional_wind',
        'long_name': 'irrotational_meridional_wind',
        'units': 'm s-1',
        'notes': 'Meridional irrotational (divergent) component of the vector wind (from Helmholtz decomposition)'},
    'upsi': {'standard_name': 'non_divergent_zonal_wind',
        'long_name': 'non_divergent_zonal_wind',
        'units': 'm s-1',
        'notes': 'Zonal non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)'},
    'vpsi': {'standard_name': 'non_divergent_meridional_wind',
        'long_name': 'non_divergent_meridional_wind',
        'units': 'm s-1',
        'notes': 'meridional non-divergent (rotational) component of the vector wind (from Helmholtz decomposition)'},
    'sf': {'standard_name': 'streamfunction',
        'long_name': 'streamfunction',
        'units': '1.e+6 m2 s-1',  
        'notes': 'rotational wind blows along streamfunction contours, speed proportional to gradient'},
    'vp': {'standard_name': 'velocity_potential',
        'long_name': 'velocity_potential',
        'units': '1.e+6 m2 s-1',  
        'notes': 'velocity potential (divergent wind blows along velocity potential contours, speed proportional to gradient)'},
    'rws': {'standard_name': 'rossby_wave_source',
        'long_name': 'rossby_wave_source',
        'units': '1.e-11 s-2'},
    'rws1': {'standard_name': 'rossby_wave_source_vortex',
        'long_name': 'rossby_wave_source_vortex',
        'units': '1.e-11 s-2',  
        'notes': 'Rossby wave source, vortex stretching term'},
    'rws2': {'standard_name': 'rossby_wave_source_advection',
        'long_name': 'rossby_wave_source_advection',
        'units': '1.e-11 s-2',  
        'notes': 'Rossby wave source, advection of absolute vorticity by divergent flow term'}}


def calc_quantity(uwnd, vwnd, quantity, lat_axis, lon_axis, axis_order):
    """Calculate a single wind quantity.

    Args:
      uwnd (numpy.ndarray): Zonal wind
      vwnd (numpy.ndarray): Meridional wind
      quantity (str): Quantity to be calculated
      lat_axis (list): Latitude axis values
      lon_axis (list): Longitude axis values
      axis_order (str): e.g. tyx

    Design:
      windsparm requires the input data to be on a global grid
        (due to the spherical harmonic representation used),
        latitude and longitude to be the leading axes and the
        latitude axis must go from 90 to -90. The cdms2 interface
        is supposed to adjust for these things but I've found that
        things come back upsidedown if the lat axis isn't right, so
        I've just used the standard interface here instead.
       
    Reference: 
        ajdawson.github.io/windspharm

    """
    
    check_global(lat_axis, lon_axis)

    # Make latitude and longitude the leading coordinates
    uwnd, uwnd_info = prep_data(numpy.array(uwnd), axis_order)
    vwnd, vwnd_info = prep_data(numpy.array(vwnd), axis_order)

    # Make sure latitude dimension is north-to-south
    lats, uwnd, vwnd = order_latdim(lat_axis, uwnd, vwnd)
    flip_lat = False if lats[0] == lat_axis[0] else True 
    
    w = VectorWind(uwnd, vwnd)
    data_out = {}
    if quantity == 'rossbywavesource':
        eta = w.absolutevorticity()
        div = w.divergence()
        uchi, vchi = w.irrotationalcomponent()
        etax, etay = w.gradient(eta)

        data_out['rws1'] = (-eta * div) / (1.e-11)
        data_out['rws2'] = (-(uchi * etax + vchi * etay)) / (1.e-11)
        data_out['rws'] = data_out['rws1'] + data_out['rws2']

    elif quantity == 'magnitude':
        data_out['spd'] = w.magnitude()
    
    elif quantity == 'vorticity':
        data_out['vrt'] = w.vorticity()
    
    elif quantity == 'divergence':
        div = w.divergence()
        data_out['div'] = div / (1.e-6)
    
    elif quantity == 'absolutevorticity':
        avrt = w.absolutevorticity()
        data_out['avrt'] = avrt / (1.e-5)
    
    elif quantity == 'absolutevorticitygradient':
        avrt = w.absolutevorticity()
        ugrad, vgrad = w.gradient(avrt)
        avrtgrad = numpy.sqrt(numpy.square(ugrad) + numpy.square(vgrad)) 
        data_out['avrtgrad'] = avrtgrad / (1.e-5)
    
    elif quantity == 'planetaryvorticity':
        data_out['pvrt'] = w.planetaryvorticity()
    
    elif quantity == 'irrotationalcomponent':
        data_out['uchi'], data_out['vchi'] = w.irrotationalcomponent()    
    
    elif quantity == 'nondivergentcomponent':
        data_out['upsi'], data_out['vpsi'] = w.nondivergentcomponent() 
    
    elif quantity == 'streamfunction':
        sf = w.streamfunction()
        data_out['sf'] = sf / (1.e+6)
    
    elif quantity == 'velocitypotential':
        vp = w.velocitypotential()
        data_out['vp'] = vp / (1.e+6)
    
    else:
        sys.exit('Wind quantity not recognised')

    # Return data to its original shape
    for key in data_out.keys():
        data_out[key] = recover_structure(data_out[key], flip_lat, uwnd_info) 

    return data_out


def check_global(lat_axis, lon_axis):
    """Check that the data are on a global grid.

    Windspharm requires a global grid due to the spherical harmonic 
      representation used.

    """

    assert numpy.abs(lat_axis[0] - lat_axis[-1]) > 179, "Data must be on a global grid"
    assert numpy.abs(lon_axis[0] - lon_axis[-1]) > 359, "Data must be on a global grid"


def recover_structure(data, flip_lat, orig_info):
    """Return data to its original structure.

    Args:
      data (numpy.ndarray): Data
      flip_lat (bool): Flag for flipping latitude axis (axis 0)
      orig_info: Obtained from windspharm.tools.prep_data

    """

    if flip_lat:
        data = data[::-1, ...]

    data = recover_data(data, orig_info)

    return data


def axis_letters(dim_list):
    """Convert dimension list to string.
    
    e.g. ['latitude', 'longitude', 'time'] -> 'yxt' 
    
    """
    
    dim_letters = {'latitude': 'y', 'longitude': 'x',
                   'time': 't', 'level': 'z'}
    
    letter_list = []
    for dim in dim_list:
        assert dim in dim_letters.keys()
        letter_list.append(dim_letters[dim])
    
    return "".join(letter_list)
    
    
def main(inargs):
    """Run the program."""

    # Read the data
    dset_in_u = xray.open_dataset(inargs.infileu)
    gio.check_xrayDataset(dset_in_u, inargs.varu)

    dset_in_v = xray.open_dataset(inargs.infilev)
    gio.check_xrayDataset(dset_in_v, inargs.varv)

    subset_dict = gio.get_subset_kwargs(inargs)
       
    darray_u = dset_in_u[inargs.varu].sel(**subset_dict)
    darray_v = dset_in_v[inargs.varv].sel(**subset_dict)

    lat_axis = darray_u['latitude'].values
    lon_axis = darray_u['longitude'].values    
    axis_order = axis_letters(darray_u.dims)
    
    # Calculate the desired quantity
    data_out = calc_quantity(darray_u.values, darray_v.values, inargs.quantity,
                             lat_axis, lon_axis, axis_order)

    # Write the output file
    d = {}
    for dim in darray_u.dims:
        d[dim] = darray_u[dim]

    for var in data_out.keys():
        d[var] = (darray_u.dims, data_out[var])
    
    dset_out = xray.Dataset(d)

    for var in data_out.keys(): 
        dset_out[var].attrs = var_atts[var]

    outfile_metadata = {inargs.infileu: dset_in_u.attrs['history'],
                        inargs.infilev: dset_in_v.attrs['history']}
    gio.set_global_atts(dset_out, dset_in_u.attrs, outfile_metadata)
    dset_out.to_netcdf(inargs.outfile, format='NETCDF3_CLASSIC')
 
    
if __name__ == '__main__':

    extra_info =""" 
wind quantities: 
  magnitude                  ->  Wind speed    
  vorticity                  ->  Relative vorticity
  divergence                 ->  Horizontal divergence
  absolutevorticity          ->  Absolute vorticity (sum of relative and planetary)
  absolutevorticitygradient  ->  Absolute vorticity gradient (sum of relative and planetary)
  irrotationalcomponent      ->  Irrotational (divergent) component of the vector wind 
                                 (from Helmholtz decomposition)
  nondivergentcomponent      ->  Non-divergent (rotational) component of the vector wind 
                                 (from Helmholtz decomposition)
  streamfunction             ->  Streamfunction (the rotational part of the wind blows 
                                 along the streamfunction contours, with speed proportional
                                 to the gradient)
  velocitypotential          ->  Velocity potential (the divergent part of the wind blows 
                                 along the velocity potential contours, with speed 
                                 proportional to the gradient)
  rossbywavesource           ->  Rossby wave source (includes the vortex stretching and 
                                 advection of absolute vorticity by divergent flow terms)
                    
note:
  The input data can have no missing values

reference:
  Uses the windspharm package: http://ajdawson.github.com/windspharm/intro.html

example (vortex.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.3.0/bin/cdat calc_wind_quantities.py sf  
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
    
    parser.add_argument("--region", type=str, choices=gio.regions.keys(),
                        help="Region [default = entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()  
    
    print 'Quantity:', args.quantity
    print 'Input U file: ', args.infileu
    print 'Input V file: ', args.infilev
    print 'Output file:', args.outfile

    main(args)
