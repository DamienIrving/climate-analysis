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
        plot_map.multiplot([test_data,],
                           ofile='before_cyl_'+text+'.png', 
                           draw_axis=True, delat=15, delon=30, equator=True,
                           contour=False)
    
        plot_map.multiplot([test_data,],
                           ofile='before_nsper_'+text+'.png',
			   projection='nsper', 
                           draw_axis=True, delat=15, delon=30, equator=True,
                           contour=False)
    
    return test_data, text


def test_cartesian_to_spherical(x, y, z):
    print 'me method'
    print rot.cartesian_to_spherical(x, y, z)
    
    print 'css method'
    print css.cssgridmodule.csc2s(x, y, z)


def test_spherical_to_cartesian(lats, lons):
    x_me, y_me, z_me = rot.spherical_to_cartesian(lats, lons)
    print 'me cartesian'
    print x_me, y_me, z_me
    
    x_css, y_css, z_css = css.cssgridmodule.css2c(lats, lons) 
    print 'css cartesian'
    print x_css, y_css, z_css
    
    return x_me, y_me, z_me, x_css, y_css, z_css
    




def test_rotate_spherical(lats, lons, np):

    print lats
    print lons

    psi = 0.0
    phi, theta = rot.north_pole_to_rotation_angles(np[0], np[1])
    print phi, theta, psi  

    latrot, lonrot = rot.rotate_spherical(lats, lons, phi, theta, psi)

    print latrot, lonrot



def test_axis_switch(data, np, stripe, pm_point=None):
    """Test the switch_axes function"""

    lat_axis = data.getLatitude()
    lon_axis = data.getLongitude()
    rotated_data = calc_envelope.switch_axes(data, lat_axis[:], lon_axis[:], np, pm_point=pm_point)

    plot_rotated_data = cdms2.createVariable(rotated_data[:], axes=[lat_axis, lon_axis])

    plot_map.multiplot([plot_rotated_data,],
                       ofile='rotated_cyl_'+stripe+'.png', 
                       draw_axis=True, delat=15, delon=30, equator=True,
                       contour=False)

    plot_map.multiplot([plot_rotated_data,],
                       ofile='rotated_nsper_'+stripe+'.png',
		       projection='nsper', 
                       draw_axis=True, delat=15, delon=30, equator=True,
                       contour=False)

    returned_data = calc_envelope.reset_axes(rotated_data, lat_axis[:], lon_axis[:], np)
    
    plot_returned_data = cdms2.createVariable(returned_data[:], axes=[lat_axis, lon_axis])
    
    plot_map.multiplot([plot_returned_data,],
                       ofile='returned_cyl_'+stripe+'.png', 
                       draw_axis=True, delat=15, delon=30, equator=True,
                       contour=False)

    plot_map.multiplot([plot_returned_data,],
                       ofile='returned_nsper_'+stripe+'.png',
		       projection='nsper', 
                       draw_axis=True, delat=15, delon=30, equator=True,
                       contour=False)





if __name__ == '__main__':

    test_data, stripe = test_dataset(lat=True, plot=True)
    np = [30.0, 270]

#    lats = numpy.array([-90, 45])
#    lons = numpy.array([240, 270])
#    #lats = numpy.arange(-90, 100, 10)
#    #lons = numpy.arange(0, 420, 60)
#    
#    print lats, lons
#    x_me, y_me, z_me, x_css, y_css, z_css = test_spherical_to_cartesian(lats, lons)
#    
#    print 'my x, y, z'
#    test_cartesian_to_spherical(x_me, y_me, z_me)
#    
#    print 'css x, y ,z'
#    test_cartesian_to_spherical(x_css, y_css, z_css)



#    test_rotate_spherical(lats, lons, np)
    test_axis_switch(test_data, np, stripe)

   
