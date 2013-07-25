"""Tests for the calc_envelope.py and associated calc_rotation.py
scripts.

Required improvements:
1. Incorporate the unittest module
2. test_axis_switch() needs to get a little more detailed. There
   is a 'dip' in the switched latitude field that needs to be looked
   at. It might be useful to plot the difference in the before and
   after fields.

"""



import os, sys
import pdb

import numpy
import cdms2
import css

#module_dir = os.path.join(os.environ['HOME'], 'modules')
#sys.path.insert(0, module_dir)
#import netcdf_io as nio

module_dir2 = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir2)
import plot_map

module_dir = os.path.join(os.environ['HOME'], 'data_processing')
sys.path.insert(0, module_dir)
import calc_envelope
import calc_rotation as rot


#########################
## Test switching axis ##
#########################

def quick_plot(data, outfile_name, projection='cyl', contour=False, ticks=None):
    """Quickly plot data"""
    
    plot_map.multiplot(data,
                       ofile=outfile_name, 
		       projection=projection,
                       ticks=ticks,
                       draw_axis=True, delat=15, delon=30, equator=True,
                       contour=contour)


def test_dataset(lat=True, plot=False):
    """Create the data for testing. It is a spatial field with 
    grid point values equal to the latitude (lat=True) or 
    longitude (lat=False)"""

    grid = cdms2.createUniformGrid(-90.0, 73, 2.5, 0.0, 144, 2.5)
    data = numpy.zeros([73, 144])
    if lat:
        text = 'lat'
        lats = numpy.arange(-90, 92.5, 2.5)
        for index in range(0, len(lats)):
            data[index, :] = lats[index]
    else:
        text = 'lon'
	lons1 = numpy.arange(0, 182.5, 2.5)
	lons2 = numpy.arange(177.5, 0, -2.5)
	for index in range(0, len(lons1)):
	    data[:, index] = lons1[index]
        for index in range(0, len(lons2)):
	    data[:, index+len(lons1)] = lons2[index]

    test_data = cdms2.createVariable(data[:], grid=grid)

    if plot:
        quick_plot([test_data,], 'before_cyl_'+text+'.png')
    
    return test_data, text


def test_rotate_spherical(lats, lons, np):

    print lats
    print lons

    phi, theta, psi = rot.north_pole_to_rotation_angles(np[0], np[1])
    print phi, theta, psi  

    latrot, lonrot = rot.rotate_spherical(lats, lons, phi, theta, psi)

    print latrot, lonrot


def test_axis_switch(np, lat=True, pm_point=None):
    """Test the switch_axes function"""

    data, stripe = test_dataset(lat=lat, plot=True)

    lat_axis = data.getLatitude()
    lon_axis = data.getLongitude()
    
    rotated_data = calc_envelope.switch_axes(data, lat_axis[:], lon_axis[:], np, pm_point=pm_point)
    plot_rotated_data = cdms2.createVariable(rotated_data[:], axes=[lat_axis, lon_axis])
    quick_plot([plot_rotated_data,], 'rotated_cyl_'+stripe+'.png') 

    returned_data = calc_envelope.reset_axes(rotated_data, lat_axis[:], lon_axis[:], np)
    plot_returned_data = cdms2.createVariable(returned_data[:], axes=[lat_axis, lon_axis])
    
    quick_plot([plot_returned_data,], 'returned_cyl_'+stripe+'.png')


############################
## Test rotation of vwind ##
############################

def test_rotation_angles(new_np, old_np=[90.0, 0.0]):
    """Test the rotation_anlges function"""
    
    grid = cdms2.createUniformGrid(-90.0, 73, 2.5, 0.0, 144, 2.5)
    lats = grid.getLatitude()[:]
    lons = grid.getLongitude()[:]

    theta = rot.rotation_angle(old_np[0], old_np[1], new_np[0], new_np[1], lats, lons)
    theta = numpy.rad2deg(theta)

    test_data = cdms2.createVariable(theta[:], grid=grid)
    
    outfile = 'rotation_angle_for_pole_lat%s_lon%s.png' %(str(new_np[0]), str(new_np[1]))
    quick_plot([test_data,], outfile)


############################
## Test the final product ##
############################

def test_final_env():
    """Plot the final wave envelope, together with anomalous wind
    and streamfunction anomaly"""
    
    env_file = '/work/dbirving/test_data/env_Merra_250hPa_monthly-anom_y73x144_np30-270.nc'
    uwnd_file = '/work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc'
    vwnd_file = '/work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc'
    contour_file = '/work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc'
    

    for year in range(1979, 2012):
        for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
            
            date = '%s-%s-01' %(str(year), str(month))	    
            out_file = '/work/dbirving/test_data/plots/test_env_'+date+'.png'

	    env_info = [env_file, 'env', date, date, 'None']
	    uwnd_info = [uwnd_file, 'ua', date, date, 'None']
	    vwnd_info = [vwnd_file, 'va', date, date, 'None']
	    contour_info = [contour_file, 'sf', date, date, 'None']

	    env_data = plot_map.extract_data([env_info,])
	    uwnd_data = plot_map.extract_data([uwnd_info,])
	    vwnd_data = plot_map.extract_data([vwnd_info,])
	    contour_data = plot_map.extract_data([contour_info,])

	    title = 'Wave envelope, 250hPa wind & sf anomaly, %s' %(date)

	    plot_map.multiplot(env_data,
        		       ofile=out_file,
        		       title=title,
        		       projection='cyl',
                               colourbar_colour='OrRd',
                               ticks=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                               extend='both',
        		       units='$m s^{-1}$',
        		       contour_data=contour_data, 
        		       uwnd_data=uwnd_data,
        		       vwnd_data=vwnd_data,
                	       quiver_thin=7,
                	       key_value=5,
                               contour=True,
                	       #quiver_scale=220, quiver_width=0.002,
        		       image_size=10)


if __name__ == '__main__':
    
    #test_rotation_angles([30, 270])
    test_final_env()
    

   
