"""
A unit testing module for the rotation of the meridional wind.

Functions/methods tested:
  coordinate_rotation.angular_distance
  coordinate_rotation.rotation_angle
  calc_vwind_rotation.vwind_trig

"""

import unittest

from math import pi, sqrt
import numpy

import itertools

import os
import sys

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import coordinate_rotation as rot
import netcdf_io as nio

module_dir = os.path.join(os.environ['HOME'], 'data_processing')
sys.path.insert(0, module_dir)
import calc_vwind_rotation as vrot

import pdb


class testAngularDistance(unittest.TestCase):
    """Test class for testing the angular distance calculation associated
    with rotating the meridional wind."""

    def test_zero_distance(self):
        """Test for the special case of no distance [test for success]"""
	
        lats1 = [40., -50., 5.]
        lons1 = [70., 190., 380.]
        lats2 = [40., -50., 5.]
        lons2 = [70., -170., -340.]
        answers = [0., 0., 0.]
        results = rot.angular_distance(lats1, lons1, lats2, lons2)	
        numpy.testing.assert_array_equal(results, answers)


    def test_known_distances_along_equator(self):
        """Test for known distances along the equator [test for success]"""
        
        lon1 = [40., 40., 40., 260., 260., 260.]
        lon2 = [-10., 130., 250., 230., 410., 50.]
        answers = numpy.deg2rad([50., 90., 150., 30., 150., 150.])
        results = rot.angular_distance(0.0, lon1, 0.0, lon2)      
         
        numpy.testing.assert_allclose(results, answers, rtol=1e-07, atol=1e-07)	


    def test_known_distances_along_meridians(self):
        """Test for known distances along meridians [test for success]"""
        
        lons = [40., 40., 290., -190.]
        lats1 = [-50., 45., -20., 90.]
        lats2 = [45., -50., -10., -90.] 
        answers = numpy.deg2rad([95., 95., 10., 180.])
        results = rot.angular_distance(lats1, lons, lats2, lons)             
        
        numpy.testing.assert_allclose(results, answers, rtol=1e-07, atol=1e-07)	

    # sanity test for increasing distance once off a great circle...
 

class testRotationAngle(unittest.TestCase):
    """Test class for testing the angle associated with rotating 
    the meridional wind. Tests focus on the original pole at 90N 0E.    
    """

    def test_np_equal_sp(self):
        """Test for the special case where the pole hasn't moved [test for success]"""

        angles = rot.rotation_angle(90, 0, 90, 0, [-40, 90], [260, 0])
        numpy.testing.assert_allclose(angles, [0., 0.], rtol=1e-07, atol=1e-07)


    def test_plus90deg(self):
        """Test for the special case of a +90 agree angle change [test for success]"""
        
        angles = rot.rotation_angle(90, 0, 0, 0, 0, 140)
        numpy.testing.assert_allclose(angles, pi/2., rtol=1e-07, atol=1e-07)

            
    def test_minus90deg(self):
        """Test for the special case of a -90 agree angle change [test for success]"""
        
        angles = rot.rotation_angle(90, 0, 0, 270, 0, 190)
        numpy.testing.assert_allclose(angles, -pi/2., rtol=1e-07, atol=1e-07)

    # sanity test for the angles increasing as the angle should...


class testVwindTrig(unittest.TestCase):
    """Test class for testing the trigonometry associated with rotating 
    the meridional wind.
    
    In practice, theta can vary between [-180, 180]
        
    """

    def test_zero_rotation(self):
        """Test for no rotation of the coordinate axes [test for success]"""
	
	u = [1.2, 0.2, -0.4, -1.4]
	v = [0.5, -2.0, 0.2, -1.3]
	theta = [0., 0., 0., 0.]
	
	answers = v
        results = vrot.vwind_trig(u, v, theta)
	
	numpy.testing.assert_allclose(results, answers, rtol=1e-07, atol=1e-07)
	
	
    def test_90deg_rotations(self):
        """[test for success]"""
	
	u = [1.2, 1.2, 1.2]
	v = [0.7, 0.7, 0.7]
	theta = [pi/2., pi, -pi/2.]
	
	answers = [-u[0], -v[1], u[2]]
	results = vrot.vwind_trig(u, v, theta)
	
	numpy.testing.assert_allclose(results, answers, rtol=1e-07, atol=1e-07)
	

    def test_known_values(self):
        """Test for known values derived by hand [test for success]"""

        pass


class testRotateVwind(unittest.TestCase):
    """Test rotate_vwind, which is the function that ultimately performs the 
    rotation of the vwind, calling other functions like vwind_trig as required
    [test for success]
    
    """
    
    def test_no_rotation(self):
        """Test for leaving the north pole at 90N, 0E"""

        new_np = [90, 0]
        dataU = nio.InputData()

        vrot.rotate_vwind(dataU, dataV, new_np, anomaly=None):






       
    
    


if __name__ == '__main__':
    unittest.main()
