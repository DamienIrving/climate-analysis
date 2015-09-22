"""
Filename:     calc_vrot.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculate the meridional wind for a rotated coordinate system

"""

# Import general Python modules

import sys, os, re, pdb
import argparse
import numpy, math
import scipy.interpolate
import xray
import iris


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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def clean_data(cube, max_value, min_value):
    """Make sure cube values lie between min_value and max_value.
    
    (The regridding produces spurious large and small values.)
    
    """

    data_clean = numpy.where(cube.data < min_value, min_value, cube.data) 
    data_clean = numpy.where(data_clean > max_value, max_value, data_clean)
    
    return data_clean


def make_grid(lat_values, lon_values, np_lat, np_lon):
    """Make a dummy cube with desired grid."""
    
    coordsys = iris.coord_systems.RotatedGeogCS(np_lat, np_lon)
    
    latitude = iris.coords.DimCoord(lat_values,
                                    standard_name='latitude',
                                    units='degrees_north',
                                    coord_system=coordsys)
    longitude = iris.coords.DimCoord(lon_values,                     
                                     standard_name='longitude',
                                     units='degrees_east',
                                     coord_system=coordsys)

    dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
    new_cube = iris.cube.Cube(dummy_data, dim_coords_and_dims=[(latitude, 0), (longitude, 1)])
    
    return new_cube


def main(inargs):
    """Run the program."""
    
    # Read data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint() 

    with iris.FUTURE.context(cell_datetime_objects=True):
        u_cube = iris.load_cube(inargs.infileU, inargs.longnameU & time_constraint)  
        v_cube = iris.load_cube(inargs.infileV, inargs.longnameV & time_constraint) 

    for coords in [u_cube.coords(), v_cube.coords()]:
        coord_names = [coord.name() for coord in coords]
        assert coord_names == ['time', 'latitude', 'longitude']

    time_coord = v_cube.coord('time')
    lat_coord = v_cube.coord('latitude')
    lon_coord = v_cube.coord('longitude')

    # Rotate wind
    np_lat, np_lon = inargs.north_pole
    rotated_cs = iris.coord_systems.RotatedGeogCS(np_lat, np_lon)
    urot_cube, vrot_cube = iris.analysis.cartography.rotate_winds(u_cube, v_cube, rotated_cs)

    # Regrid
    target_grid_cube = make_grid(lat_coord.points, lon_coord.points, np_lat, np_lon)
    scheme = iris.analysis.Linear()
    vrot_cube.coords('latitude')[0].coord_system = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    vrot_cube.coords('longitude')[0].coord_system = iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
    vrot_regridded = vrot_cube.regrid(target_grid_cube, scheme)
    #could use clean_data here to remove spurious large values that regirdding produces

    # Write to file
    d = {}
    d['time'] = ('time', time_coord.points)
    d['latitude'] = ('latitude', lat_coord.points)
    d['longitude'] = ('longitude', lon_coord.points)
    d['vrot'] = (['time', 'latitude', 'longitude'], vrot_regridded.data)

    dset_out = xray.Dataset(d)
    dset_out['vrot'].attrs =  {'standard_name': 'rotated_northward_wind',
                               'long_name': 'rotated_northward_wind',
                               'units': str(v_cube.units),
                               'notes': 'North Pole at lat=%s, lon=%s. Data defined on rotated grid.' %(np_lat, np_lon)}
    gio.set_dim_atts(dset_out, time_coord, lat_coord, lon_coord)

    outfile_metadata = {inargs.infileU: u_cube.attributes['history'],
                        inargs.infileV: v_cube.attributes['history']}

    gio.set_global_atts(dset_out, v_cube.attributes, outfile_metadata)
    dset_out.to_netcdf(inargs.outfile,) #format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au
    
"""

    description='Calculate the meridional wind in a new rotated coordinate system'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infileU", type=str, help="Zonal wind input file name")
    parser.add_argument("longnameU", type=str, help="Long name for zonal wind variable")
    parser.add_argument("infileV", type=str, help="Meridional wind input file name")
    parser.add_argument("longnameV", type=str, help="Long name for meridional wind variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--north_pole", type=float, nargs=2, metavar=('LAT', 'LON'), default=[20.0, 260.0],
                        help="Location of north pole [default = (20, 260)]")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            
    main(args)
