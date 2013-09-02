"""
A unit testing module for the rotation of the meridional wind.

Functions/methods tested:
  calc_vwind_rotation.

"""

import unittest

from math import pi, sqrt
import numpy

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

    def setUp(self):
        """Define the lat/lon data to be tested, ensuring all quadrants are 
        covered."""        

        self.lats = numpy.arange(-90.0, 120.0, 30.0)
        self.lons = numpy.arange(0.0, 390.0, 30.0)

    def test_invalid_input(self):
        """[test for failure]"""
 
        pass                                       
        #self.assertRaises(AssertionError, rot.rotation_matrix, 0.0, pi, 6.5)

    def test_zero_distance(self):
        """Test for the special case of no distance [test for success]"""
	
        for combo in itertools.product(self.lats, self.lons):
            self.assertEqual(rot.angular_distance(combo[0], combo[1], combo[0], combo[1]), 0.0)	

    def test_known_distances_along_equator(self):
        """Test for known distances along the equator [test for success]"""
        
        for lon1 in self.lons:
            for lon2 in self.lons:
                lon_diff = numpy.abs(numpy.rad2deg(lon1 - lon2))
                dist = rot.angular_distance(0.0, lon1, 0.0, lon2)               
                self.assertEqual(dist, lon_diff)	

    def test_known_distances_along_meridians(self):
        """Test for known distances along meridians [test for success]"""
        
        for lon in self.lons:
            for lat1 in self.lats:
                for lat2 in self.lats:
                    lat_diff = numpy.abs(numpy.rad2deg(lat1 - lat2))
                    dist = rot.angular_distance(lat1, lon, lat2, lon)               
                    self.assertEqual(dist, lon_diff)	


class testRotationAngle(unittest.TestCase):
    """Test class for testing the angle associated with rotating 
    the meridional wind. Tests focus on the original pole at 90N 0E.    
    """

    def setUp(self):
        """Define data to be tested."""

        pass


    def test_np_equal_sp(self):
        """Test for the special case where the pole hasn't moved [test for success]"""

        angles = rot.rotation_angle(90, 0, 90, 0, [-40, 90], [260, 0])
        numpy.testing.assert_allclose(angles, [0., 0.], rtol=1e-07, atol=1e-07)


    def test_plus90deg(self):
        """Test for the special case of a +90 agree angle change [test for success]"""
        
        angles = rot.rotation_angle(90, 0, 0, 0, 0, 140)
        numpy.testing.assert_allclose(angles, 90., rtol=1e-07, atol=1e-07)

            
    def test_minus90deg(self):
        """Test for the special case of a -90 agree angle change [test for success]"""
        
        angles = rot.rotation_angle(90, 0, 0, 270, 0, 190)
        numpy.testing.assert_allclose(angles, -90., rtol=1e-07, atol=1e-07)


if __name__ == '__main__':
    unittest.main()
