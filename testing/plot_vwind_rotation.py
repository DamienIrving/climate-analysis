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


def main(new_np, res):
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
                       title='Original wsp data',
                       ofile='vrot_original_wsp.png',
		       units='$m s^{-1}$',
		       uwnd_data=[dataU,], vwnd_data=[dataV,],
		       quiver_thin=8, key_value=10,
                       draw_axis=True, delat=15, delon=30, equator=True,
		       image_size=10)

    # Plot the rotated vwind #

    vwind_rot = vrot.calc_vwind(dataU, dataV, lat_axis, lon_axis, new_np)
    vwind_rot_cdms = cdms2.createVariable(vwind_rot, grid=grid_orig, axes=[lat_axis, lon_axis])

    title = 'New meridional wind, original coordinate axes, for NP %sN, %sE' %(str(new_np[0]), str(new_np[1]))
    ofile = 'vrot_newv_origaxes_%sN_%sE.png' %(str(new_np[0]), str(new_np[1]))
    plot_map.multiplot([vwind_rot_cdms,],
                       dimensions=(1, 1),  
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
    ofile = 'vrot_newv_rotaxes_%sN_%sE.png' %(str(new_np[0]), str(new_np[1]))
    plot_map.multiplot([vwind_rot_switch_cdms,],
                       dimensions=(1, 1), nocoast=True,  
                       title=title,
                       ofile=ofile,
		       units='$m s^{-1}$',
		       draw_axis=True, delat=15, delon=30, equator=True,
		       image_size=10)


if __name__ == '__main__':
    
    description='Visualise the various components of meridional wind rotation'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("north_pole_lat", type=float, help="Latitude of north pole")
    parser.add_argument("north_pole_lon", type=float, help="Longitude of north pole")
    parser.add_argument("res", type=float,  
                        help="Resolution of final rotated data")
    
    args = parser.parse_args()            

    new_np = [args.north_pole_lat, args.north_pole_lon]

    main(new_np, args.res)    
