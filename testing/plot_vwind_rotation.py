"""
A testing module for visualising vwind rotation.

Functions/methods tested:
  

"""
import os, sys

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import matplotlib

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import coordinate_rotation as rot
import netcdf_io as nio

module_dir2 = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir2)
import plot_map

module_dir3 = os.path.join(os.environ['HOME'], 'data_processing')
sys.path.insert(0, module_dir3)
import calc_vwind_rotation as vrot

import numpy
import cdms2
import MV2

import argparse

import pdb


def plot_data(new_np, res, proj):
    """Create the various plots"""
    
    # Get input data #

    fin = cdms2.open('/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc')
    dataU = fin('ua', time=('1979-01-01', '1979-01-29'), squeeze=1)
    fin.close()

    fin = cdms2.open('/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc')
    dataV = fin('va', time=('1979-01-01', '1979-01-29'), squeeze=1)
    fin.close()

    lat_axis = dataU.getLatitude()
    lon_axis = dataU.getLongitude()
    lats, lons = nio.coordinate_pairs(lat_axis, lon_axis)
    grid_orig = dataU.getGrid()

    # Plot wind vectors with wsp underneath #

    wsp = MV2.sqrt(dataU**2 + dataV**2)

    plot_map.multiplot([wsp,],
                       dimensions=(1, 1),  
		       centre=(new_np[0], new_np[1]), projection=proj,
                       title='Original wsp data',
                       ofile='vrot_original_wsp_%s.png' %(proj),
		       units='$m s^{-1}$',
		       uwnd_data=[dataU,], vwnd_data=[dataV,],
		       quiver_thin=8, key_value=10,
                       draw_axis=True, delat=15, delon=30, equator=True,
		       image_size=10)

    # Plot the rotated vwind #

    vwind_rot = vrot.calc_vwind(dataU, dataV, lat_axis, lon_axis, new_np)
    vwind_rot_cdms = cdms2.createVariable(vwind_rot, grid=grid_orig, axes=[lat_axis, lon_axis])

    title = 'New meridional wind, original coordinate axes, for NP %sN, %sE' %(str(new_np[0]), str(new_np[1]))
    ofile = 'vrot_newv_origaxes_%sN_%sE_%s.png' %(str(new_np[0]), str(new_np[1]), proj)
    plot_map.multiplot([vwind_rot_cdms,],
                       dimensions=(1, 1),  
		       centre=(new_np[0], new_np[1]), projection=proj,
                       title=title,
                       ofile=ofile,
		       units='$m s^{-1}$',
		       uwnd_data=[dataU,], vwnd_data=[dataV,],
		       quiver_thin=8, key_value=10,
                       draw_axis=True, delat=15, delon=30, equator=True,
		       image_size=10)

    # Plot the rotated vwind on the new coordinate system #

    nlats = int((180.0 / res) + 1)
    nlons = int(360.0 / res)
    grid_rot = cdms2.createUniformGrid(-90.0, nlats, res, 0.0, nlons, res)
    lat_axis_rot = grid_rot.getLatitude()
    lon_axis_rot = grid_rot.getLongitude()

    vwind_rot_switch = rot.switch_regular_axes(vwind_rot, lats, lons, lat_axis_rot[:], lon_axis_rot[:], new_np)
    vwind_rot_switch_cdms = cdms2.createVariable(vwind_rot_switch, grid=grid_rot, axes=[lat_axis_rot, lon_axis_rot])

    title = 'New meridional wind, rotated coordinate axes, for NP %sN, %sE' %(str(new_np[0]), str(new_np[1]))
    ofile = 'vrot_newv_rotaxes_%sN_%sE_%s.png' %(str(new_np[0]), str(new_np[1]), proj)
    plot_map.multiplot([vwind_rot_switch_cdms,],
                       dimensions=(1, 1), nocoast=True,
		       centre=(new_np[0], new_np[1]), projection=proj,  
                       title=title,
                       ofile=ofile,
		       units='$m s^{-1}$',
		       draw_axis=True, delat=15, delon=30, equator=True,
		       image_size=10)


def plot_angles(new_np, proj):
    """Test the rotation_anlges function, just as it is implemented in calc_vwind"""

    fin = cdms2.open('/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc')
    dataV = fin('va', time=('1979-01-01', '1979-01-29'), squeeze=1)
    fin.close()

    grid = dataV.getGrid()
    lat_axis = dataV.getLatitude()[:]
    lon_axis = dataV.getLongitude()[:]
    lons, lats = nio.coordinate_pairs(lon_axis, lat_axis)
 
    theta = rot.rotation_angle(90.0, 0.0, new_np[0], new_np[1], 
                               lats, lons, reshape=[len(lat_axis), len(lon_axis)])
    theta = numpy.resize(theta, numpy.shape(dataV))
    theta = numpy.rad2deg(theta)

    theta_cdms = cdms2.createVariable(theta[:], grid=grid)
    
    title = 'Rotation angle for pole %sN %sE' %(str(new_np[0]), str(new_np[1]))
    outfile = 'rotation_angle_for_pole_%sN_%sE_%s.png' %(str(new_np[0]), str(new_np[1]), proj)
    
    plot_map.multiplot([theta_cdms,],
                       dimensions=(1, 1),
		       centre=(new_np[0], new_np[1]), projection=proj,  
                       title=title,
                       ofile=outfile, 
                       draw_axis=True, delat=15, delon=30)


if __name__ == '__main__':
    
    description='Visualise the various components of meridional wind rotation'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("north_pole_lat", type=float, help="Latitude of north pole")
    parser.add_argument("north_pole_lon", type=float, help="Longitude of north pole")
    parser.add_argument("plot_type", type=str, choices=('data', 'angle'),  
                        help="Type of plot")
    parser.add_argument("--res", type=float, default=1.0, 
                        help="Resolution of final rotated data")
    parser.add_argument("--projection", type=str, choices=('cyl', 'nsper'), default='cyl',
                        help="map projection [default: cyl]")

    args = parser.parse_args()            

    new_np = [args.north_pole_lat, args.north_pole_lon]

    if args.plot_type == 'angle':
        plot_angles(new_np, args.projection)
    else:
        plot_data(new_np, args.res, args.projection)    
