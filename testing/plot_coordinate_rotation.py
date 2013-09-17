"""
A testing module for visualising coordinate system rotation.

Functions/methods tested:
  coordinate_rotation.switch_regular_axes

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
import argparse

import pdb


def create_latlon_dataset(res=2.5):
    """Create a dataset corresponding to the latitude (output 1) and
    longitude (output 2) of each grid point"""

    nlats = int((180.0 / res) + 1)
    nlons = int(360.0 / res)
    grid = cdms2.createUniformGrid(-90.0, nlats, res, 0.0, nlons, res)
    
    lat_data = numpy.zeros([nlats, nlons])
    lat_axis = numpy.arange(-90, 90 + res, res)
    for index in range(0, nlats):
        lat_data[index, :] = lat_axis[index]
    lat_data_cdms = cdms2.createVariable(lat_data[:], grid=grid)

    lon_data = numpy.zeros([nlats, nlons])
    lon_axis1 = numpy.arange(0, 180 + res, res)
    lon_axis2 = numpy.arange(180 - res, 0, -res)
    for index in range(0, len(lon_axis1)):
        lon_data[:, index] = lon_axis1[index]
    for index in range(0, len(lon_axis2)):
	lon_data[:, index + len(lon_axis1)] = lon_axis2[index]
    lon_data_cdms = cdms2.createVariable(lon_data[:], grid=grid)

    return lat_data_cdms, lon_data_cdms


def switch_and_restore(data, new_np):
    """Test the switch_axes function"""

    lat_axis = data.getLatitude()
    lon_axis = data.getLongitude()
    lats, lons = nio.coordinate_pairs(lat_axis, lon_axis)
    
    rotated_data = rot.switch_regular_axes(data, lats, lons, lat_axis[:], lon_axis[:], new_np, invert=False)
    cdms_rotated_data = cdms2.createVariable(rotated_data[:], axes=[lat_axis, lon_axis])

    returned_data = rot.switch_regular_axes(rotated_data, lats, lons, lat_axis[:], lon_axis[:], new_np, invert=True)
    cdms_returned_data = cdms2.createVariable(returned_data[:], axes=[lat_axis, lon_axis])

    return cdms_rotated_data, cdms_returned_data
    

def plot_axis_switch(new_np):
    """Plot the original, rotated and returned data"""

    orig_lat_data, orig_lon_data = create_latlon_dataset()
    rotated_lat_data, returned_lat_data = switch_and_restore(orig_lat_data, new_np)
    rotated_lon_data, returned_lon_data = switch_and_restore(orig_lon_data, new_np)

    title = 'Axis switch for NP %sN, %sE' %(str(new_np[0]), str(new_np[1])) 

    plot_search_path(rotated_lat_data, new_np)

    # Latitude plot
    plot_lat_list = [orig_lat_data, rotated_lat_data, returned_lat_data]
    plot_map.multiplot(plot_lat_list,
                       dimensions=(3, 1),  
                       title=title,
                       ofile='axis_switch_lat_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])), 
                       row_headings=['original', 'rotated', 'returned'],
                       draw_axis=True, delat=15, delon=30, equator=True)

    # Longitude plot
    plot_lon_list = [orig_lon_data, rotated_lon_data, returned_lon_data]
    plot_map.multiplot(plot_lon_list,
                       dimensions=(3, 1),  
                       title=title,
                       ofile='axis_switch_lon_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])), 
                       row_headings=['original', 'rotated', 'returned'],
                       draw_axis=True, delat=15, delon=30, equator=True)


def plot_search_path(rotated_lat_data, new_np):
    """Plot the wave extraction search path"""
    
    bmap = Basemap(llcrnrlon=0, llcrnrlat=-90, urcrnrlon=360, urcrnrlat=90, projection='cyl')
    bmap.drawcoastlines()
    bmap.drawparallels(numpy.arange(-90,90,30), labels=[1,0,0,0], color='grey', dashes=[1,3])
    bmap.drawmeridians(numpy.arange(0,360,45), labels=[0,0,0,1], color='grey', dashes=[1,3])
    matplotlib.rcParams['contour.negative_linestyle'] = 'solid'
    
    lons, lats = numpy.meshgrid(rotated_lat_data.getLongitude()[:],
                                rotated_lat_data.getLatitude()[:])
    x, y = bmap(lons, lats)
    im = bmap.contour(x, y, rotated_lat_data, [-20.0, -15.0, -10.0, -5.0, 0, 5.0, 10.0, 15.0, 20.0], colors='k')
    plt.clabel(im, fontsize=5, inline=1, fmt='%.1f')  
    
    plt.savefig('search_paths_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])))


def plot_real_data(new_np):
    """Real data plot
    
    Perhaps I need to test a change in resolution here??
    (like in calc_vwind)
    
    """
    
    fin = cdms2.open('/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc')
    orig_real_data = fin('va', time=('1979-01-01', '1979-01-29'), squeeze=1)
    fin.close()

    rotated_real_data, returned_real_data = switch_and_restore(orig_real_data, new_np)
    
    title = 'Axis switch for NP %sN, %sE' %(str(new_np[0]), str(new_np[1]))
        
    # Plot original data #
    
    plot_map.multiplot([orig_real_data,],
                       dimensions=(1, 1),
		       centre=(90, 0), projection='nsper',  
                       title=title,
                       ofile='axis_switch_orig-real_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])), 
                       draw_axis=True, delat=15, delon=30)

    # Plot rotated data #

    plot_map.multiplot([rotated_real_data,],
                       dimensions=(1, 1),
		       centre=(new_np[0], new_np[1]), projection='nsper',  
                       title=title,
                       ofile='axis_switch_rot-real_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])), 
                       draw_axis=True, delat=15, delon=30)

    # Plot returned data #
    
    plot_map.multiplot([returned_real_data,],
                       dimensions=(1, 1),
		       centre=(90, 0), projection='nsper',  
                       title=title,
                       ofile='axis_switch_returned-real_%sN_%sE.png' %(str(new_np[0]), str(new_np[1])), 
                       draw_axis=True, delat=15, delon=30)


if __name__ == '__main__':
    
    description='Visualise the various components of coordinate rotation'
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("north_pole_lat", type=float, help="Latitude of north pole")
    parser.add_argument("north_pole_lon", type=float, help="Longitude of north pole")
    parser.add_argument("plot_type", type=str, choices=('latlon_switch', 'real_switch'),  
                        help="Type of plot")
    
    args = parser.parse_args()            

    new_np = [args.north_pole_lat, args.north_pole_lon]
    if args.plot_type == 'real_switch':
        plot_real_data(new_np)    
    else:
        plot_axis_switch(new_np)
