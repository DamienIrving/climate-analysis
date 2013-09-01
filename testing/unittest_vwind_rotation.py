"""
A unit testing module for the rotation of the meridional wind.

Functions/methods tested:
  calc_vwind_rotation.

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
    """Test class for testing the rotation angle associated
    with rotating the meridional wind."""

    def setUp(self):
        """Define the lat/lon data to be tested, ensuring all quadrants are 
        covered."""

        pass  

    def test_np_equal_sp(self):
        """Test for the special case where the pole hasn't moved [test for success]"""
            
        lat_axis = numpy.arange(-90, 95, 5)
        lon_axis = numpy.arange(0, 365, 5)
        lats, lons = nio.coordinate_pairs(lat_axis, lon_axis)
	
        for comboAB in itertools.product(lats, lons):	
            angles = rot.rotation_angle(comboAB[0], comboAB[1], comboAB[0], comboAB[1], lats, lons, reshape=[len(lat_axis), len(lon_axis)])
            self.assertIsNone(numpy.testing.assert_allclose(angles, numpy.zeros([len(lat_axis), len(lon_axis)]), rtol=1e-07, atol=1e-07))














 #   def setUp(self):
#        """Define the sets of Euler angles (phi, theta, psi) to be tested"""
#
#        self.angles = [[0.0, 0.0, 0.0],
#                       [2 * pi, 2 * pi, 2 * pi],
#                       [pi, pi, pi],
#                       [0.0, 0.5 * pi, 0.3*pi],
#                       [0.4 * pi, 1.2 * pi, 1.7 * pi]]
#
#                        
#    def test_no_rotation(self):
#        """Test no rotation for psi = theta = psi = 0.0 [test for success]"""
#
#        for phi, theta, psi in self.angles[0:2]:
#            for inv in [True, False]:
#                result = rot.rotation_matrix(phi, theta, psi, inverse=inv)
#                self.assertIsNone(numpy.testing.assert_allclose(result, numpy.identity(3), rtol=1e-07, atol=1e-07)) 
#                # an alternative is numpy.testing.assert_array_almost_equal()
#
#
#    def test_known_value(self):
#        """Test the rotation matrix for a known answer (derived by hand) [test for success]"""
#        
#	phi, theta, psi = [pi / 4, pi / 3, pi / 6]
#        result = rot.rotation_matrix(phi, theta, psi, inverse=False)
#        
#	a = sqrt(3.0) / 2
#	b = 0.5
#	c = 1 / sqrt(2.0)
#	answer = numpy.empty([3,3])
#	answer[0, 0] = (a * c) - (b * c * b)
#	answer[0, 1] = (a * c) + (b * c * b)
#	answer[0, 2] = b * a
#	answer[1, 0] = -(b * c) - (b * c * a)
#	answer[1, 1] = -(b * c) + (b * c * a)
#	answer[1, 2] = a * a
#	answer[2, 0] = a * c
#	answer[2, 1] = -(a * c)
#	answer[2, 2] = b
#
#        self.assertIsNone(numpy.testing.assert_allclose(result, answer, rtol=1e-07, atol=1e-07)) 
#
#
#    def test_known_inverse(self):
#        """Test the inverse rotation matrix for a known answer (derived by hand) [test for success]"""
#        
#	phi, theta, psi = [pi / 4, pi / 3, pi / 6]
#        result = rot.rotation_matrix(phi, theta, psi, inverse=True)
#        
#	a = sqrt(3.0) / 2
#	b = 0.5
#	c = 1 / sqrt(2.0)
#	answer = numpy.empty([3,3])
#	answer[0, 0] = (a * c) - (b * c * b)
#	answer[0, 1] = -(b * c) - (b * c * a)
#	answer[0, 2] = a * c
#	answer[1, 0] = (a * c) + (b * c * b)
#	answer[1, 1] = -(b * c) + (b * c * a)
#	answer[1, 2] = -(a * c)
#	answer[2, 0] = a * b
#	answer[2, 1] = a * a
#	answer[2, 2] = b
#
#        self.assertIsNone(numpy.testing.assert_allclose(result, answer, rtol=1e-07, atol=1e-07)) 
#
#
#    def test_invalid_input(self):
#        """Test input angles outside of [0, 2*pi] [test for failure]"""
#
#        self.assertRaises(AssertionError, rot.rotation_matrix, 0.0, pi, 6.5)
#
#
#    def test_identity(self):
#        """The transformation matrix, multiplied by its inverse, 
#        should return the identity matrix [test for sanity]"""
#
#        for phi, theta, psi in self.angles:
#            A = rot.rotation_matrix(phi, theta, psi, inverse=False)
#            Ainv = rot.rotation_matrix(phi, theta, psi, inverse=True)
#            product = numpy.dot(A, Ainv)
#
#            self.assertIsNone(numpy.testing.assert_allclose(product, numpy.identity(3), rtol=1e-07, atol=1e-07))
#


if __name__ == '__main__':
    unittest.main()
