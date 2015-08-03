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


def regrid(data, old_lats, old_lons, new_lats, new_lons):
    """FIXME"""

    new_lons_flat = new_lons.flatten()
    new_lats_flat = new_lats.flatten()
    grid_lons, grid_lats = numpy.meshgrid(old_lons, old_lats)

    points = numpy.column_stack((new_lons_flat, new_lats_flat))  
    values = data.flatten()

    regridded_data = scipy.interpolate.griddata(points, values, (grid_lons, grid_lats), 
                                                method='linear', fill_value=0)

    regridded_data_clean = numpy.where(regridded_data < values.min(), values.min(), regridded_data) 
    regridded_data_clean = numpy.where(regridded_data_clean > values.max(), values.max(), regridded_data_clean)

    return regridded_data_clean


def set_dim_atts(dset_out, time_coord, latitude_coord, longitude_coord):
    """Set dimension attributes."""
    
    dset_out['time'].attrs = {'calendar': 'standard', 
                              'long_name': 'time',
                              'units': str(time_coord.units),
                              'axis': 'T'}
    dset_out['latitude'].attrs = {'standard_name': 'latitude',
                                  'long_name': 'latitude',
                                  'units': 'degrees_north',
                                  'axis': 'Y'}
    dset_out['longitude'].attrs = {'standard_name': 'longitude',
                                  'long_name': 'longitude',
                                  'units': 'degrees_east',
                                  'axis': 'X'}

#    for dim in ['time', 'latitude', 'longitude']:
#        for att in ['standard_name', 'units', 'long_name']:
#            try: 
#                dset_out[dim].attrs[att] = str(eval(dim+'_coord.'+att))
#            except AttributeError:
#                pass
    
    return dset_out


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
    x_values = vrot_cube.coord('projection_x_coordinate').points
    y_values = vrot_cube.coord('projection_y_coordinate').points
    lats = lat_coord.points
    lons = lon_coord.points
    
    x_values = numpy.where(x_values < 0, x_values + 360, x_values)
    lons = numpy.where(lons < 0, lons + 360, lons)

    vrot_regridded = numpy.zeros(vrot_cube.data.shape)
    for tstep in range(0, len(time_coord.points)):
        vrot_regridded[tstep, :, :] = regrid(vrot_cube.data[tstep, :, :], lats, lons, y_values, x_values) 
    
    # Write to file
    d = {}
    d['time'] = ('time', time_coord.points)
    d['latitude'] = ('latitude', lat_coord.points)
    d['longitude'] = ('longitude', lon_coord.points)
    d['vrot'] = (['time', 'latitude', 'longitude'], vrot_regridded)

    dset_out = xray.Dataset(d)
    dset_out['vrot'].attrs =  {'standard_name': 'rotated_northward_wind',
                               'long_name': 'rotated_northward_wind',
                               'units': str(v_cube.units),
                               'notes': 'North Pole at %s, %s. Data defined on rotated grid.' %(np_lat, np_lon)}
    set_dim_atts(dset_out, time_coord, lat_coord, lon_coord)

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
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period [default = entire]")

    args = parser.parse_args()            
    main(args)
