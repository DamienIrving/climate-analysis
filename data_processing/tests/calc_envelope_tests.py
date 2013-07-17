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




def test_dataset(plot=False):
    """Create the data for testing. It is a spatial field with 
    grid point values equal to the latitude"""

    grid = cdms2.createUniformGrid(-90.0, 73, 2.5, 0.0, 144, 2.5)
    data = numpy.zeros([73, 144])
    lats = numpy.arange(-90, 92.5, 2.5)
    for index in range(0,73):
        data[index, :] = lats[index]

    test_data = cdms2.createVariable(data[:], grid=grid)

    if plot:
        plot_map.multiplot([test_data,],
                           ofile='before.png', 
                           draw_axis=True, delat=15, delon=30, equator=True,
                           contour=True)
    
    return test_data


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



def test_axis_switch(data, np):
    """Test the switch_axes function"""

    new_data = calc_envelope.switch_axes(data, np)

    plot_map.multiplot([new_data,],
                       ofile='rotated.png', 
                       draw_axis=True, delat=15, delon=30, equator=True,
                       contour=True)






if __name__ == '__main__':

#    test_data = test_dataset()
#    np = [90.0, 0.0]


    lats = numpy.array([-90, 45])
    lons = numpy.array([240, 270])
    #lats = numpy.arange(-90, 100, 10)
    #lons = numpy.arange(0, 420, 60)
    
    print lats, lons
    x_me, y_me, z_me, x_css, y_css, z_css = test_spherical_to_cartesian(lats, lons)
    
    print 'my x, y, z'
    test_cartesian_to_spherical(x_me, y_me, z_me)
    
    print 'css x, y ,z'
    test_cartesian_to_spherical(x_css, y_css, z_css)



#    test_rotate_spherical(lats, lons, np)
#    test_axis_switch(test_data, np)
