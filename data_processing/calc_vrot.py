"""
Filename:     calc_vrot.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculate the meridional wind for a rotated coordinate system

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, math
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

def get_time_constraint(time_list):
    """Set the time constraint."""
    
    start_date, end_date = time_list

    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    assert re.search(date_pattern, start_date)
    assert re.search(date_pattern, end_date)

    if (start_date == end_date):
        year, month, day = start_date.split('-')    
        time_constraint = iris.Constraint(time=iris.time.PartialDateTime(year=int(year), month=int(month), day=int(day)))
    else:  
        start_year, start_month, start_day = start_date.split('-') 
        end_year, end_month, end_day = end_date.split('-')
        time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=int(start_year), month=int(start_month), day=int(start_day)) <= t <= iris.time.PartialDateTime(year=int(end_year), month=int(end_month), day=int(end_day)))

    return time_constraint


def regrid(cube):
    """ """

    # Get axis info
    x_values = cube.coord('projection_x_coordinate').points
    y_values = cube.coord('projection_y_coordinate').points
    lats = cube.coord('latitude').points
    lons = cube.coord('longitude').points
    
    # Make sure longitude range is 0 to 360
    x_values = numpy.where(x_values < 0, x_values + 360, x_values)
    lons = numpy.where(lons < 0, lons + 360, lons)

    # Interpolate
    x_flat = x_values.flatten()
    y_flat = y_values.flatten()
    points = numpy.column_stack((x_flat, y_flat))

    values = cube.data.flatten()  
    grid_lons, grid_lats = numpy.meshgrid(lons, lats)

    regridded_data = scipy.interpolate.griddata(points, values, (grid_lons, grid_lats), 
                                                method='linear', fill_value=0)
    regridded_data = regridded_data.T

    # Get rid of spurious values
    regridded_data_clean = numpy.where(regridded_data < values.min(), values.min(), regridded_data) 
    regridded_data_clean = numpy.where(regridded_data_clean > values.max(), values.max(), regridded_data_clean)

    return regridded_data_clean


def main(inargs):
    """Run the program."""
    
    # Read data
    try:
        time_constraint = get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint() 

    with iris.FUTURE.context(cell_datetime_objects=True):
        u_cube = iris.load_cube(inargs.infileU, inargs.longnameU & time_constraint)  
        v_cube = iris.load_cube(inargs.infileV, inargs.longnameV & time_constraint) 

    # Rotate wind
    np_lat, np_lon = inargs.north_pole
    rotated_cs = iris.coord_systems.RotatedGeogCS(np_lat, np_lon)
    urot_cube, vrot_cube = iris.analysis.cartography.rotate_winds(u_cube, v_cube, rotated_cs)

    # Regrid
    coord_names = [coord.name() for coord in vrot_cube.coords()]
    assert coord_names == ['time', 'latitude', 'longitude']
    vrot_data = numpy.apply_along_axis(regrid, 0, vrot_cube) 
    
    # Write to file
    time_coord = v_cube.coord('time')
    lat_coord = v_cube.coord('latitude')
    lon_coord = v_cube.coord('longitude')

    d = {}
    d['time'] = ('time', time_coord.points)
    d['latitude'] = ('latitude', lat_coord.points)
    d['longitude'] = ('longitude', lon_coord.points)
    d['vrot'] = (['time', 'latitude', 'longitude'], vrot_data)

    dset_out = xray.Dataset(d)
    dset_out['vrot'].attrs =  {'standard_name': 'rotated_meridional_wind',
                               'long_name': 'rotated_meridional_wind',
                               'units': v_cube.units,
                               'notes': 'North Pole at %s, %s. Data defined on rotated grid.' %(np_lat, np_lon)}
    dset_out['time'].attrs = time_coord.attributes
    dset_out['latitude'].attrs = lat_coord.attributes
    dset_out['longitude'].attrs = lon_coord.attributes 

    outfile_metadata = {inargs.infileU: u_cube.attributes['history'],
                        inargs.infileV: v_cube.attributes['history']}
    gio.set_global_atts(dset_out, v_cube.attributes['history'], outfile_metadata)
    dset_out.to_netcdf(inargs.outfile, format='NETCDF3_CLASSIC')


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
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
