"""
A unit testing module for coordinate system rotation.

Functions/methods tested:
  coordinate_rotation.rotation_matrix

"""

import unittest

from math import pi, sqrt
import numpy

import os
import sys

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import coordinate_rotation as rot

import pdb


class testTransformationMatrix(unittest.TestCase):
    """Test class for the transformation matrix used
    in coordinate system rotations."""

    def setUp(self):
        """Define the sets of Euler angles (phi, theta, psi) to be tested"""

        self.angles = [[0.0, 0.0, 0.0],
                       [2 * pi, 2 * pi, 2 * pi],
                       [pi, pi, pi],
                       [0.0, 0.5 * pi, 0.3*pi],
                       [0.4 * pi, 1.2 * pi, 1.7 * pi]]

                        
    def test_no_rotation(self):
        """Test no rotation for psi = theta = psi = 0.0 [test for success]"""

        for phi, theta, psi in self.angles[0:2]:
            for inv in [True, False]:
                result = rot.rotation_matrix(phi, theta, psi, inverse=inv)
                self.assertIsNone(numpy.testing.assert_allclose(result, numpy.identity(3), rtol=1e-07, atol=1e-07)) 
                # an alternative is numpy.testing.assert_array_almost_equal()


    def test_known_value(self):
        """Test the rotation matrix for a known answer (derived by hand) [test for success]"""
        
	phi, theta, psi = [pi / 4, pi / 3, pi / 6]
        result = rot.rotation_matrix(phi, theta, psi, inverse=False)
        
	a = sqrt(3.0) / 2
	b = 0.5
	c = 1 / sqrt(2.0)
	answer = numpy.empty([3,3])
	answer[0, 0] = (a * c) - (b * c * b)
	answer[0, 1] = (a * c) + (b * c * b)
	answer[0, 2] = b * a
	answer[1, 0] = -(b * c) - (b * c * a)
	answer[1, 1] = -(b * c) + (b * c * a)
	answer[1, 2] = a * a
	answer[2, 0] = a * c
	answer[2, 1] = -(a * c)
	answer[2, 2] = b

        self.assertIsNone(numpy.testing.assert_allclose(result, answer, rtol=1e-07, atol=1e-07)) 


    def test_known_inverse(self):
        """Test the inverse rotation matrix for a known answer (derived by hand) [test for success]"""
        
	phi, theta, psi = [pi / 4, pi / 3, pi / 6]
        result = rot.rotation_matrix(phi, theta, psi, inverse=True)
        
	a = sqrt(3.0) / 2
	b = 0.5
	c = 1 / sqrt(2.0)
	answer = numpy.empty([3,3])
	answer[0, 0] = (a * c) - (b * c * b)
	answer[0, 1] = -(b * c) - (b * c * a)
	answer[0, 2] = a * c
	answer[1, 0] = (a * c) + (b * c * b)
	answer[1, 1] = -(b * c) + (b * c * a)
	answer[1, 2] = -(a * c)
	answer[2, 0] = a * b
	answer[2, 1] = a * a
	answer[2, 2] = b

        self.assertIsNone(numpy.testing.assert_allclose(result, answer, rtol=1e-07, atol=1e-07)) 


    def test_invalid_input(self):
        """Test input angles outside of [0, 2*pi] [test for failure]"""

        self.assertRaises(AssertionError, rot.rotation_matrix, 0.0, pi, 6.5)


    def test_identity(self):
        """The transformation matrix, multiplied by its inverse, 
        should return the identity matrix [test for sanity]"""

        for phi, theta, psi in self.angles:
            A = rot.rotation_matrix(phi, theta, psi, inverse=False)
            Ainv = rot.rotation_matrix(phi, theta, psi, inverse=True)
            product = numpy.dot(A, Ainv)

            self.assertIsNone(numpy.testing.assert_allclose(product, numpy.identity(3), rtol=1e-07, atol=1e-07))



if __name__ == '__main__':
    unittest.main()
