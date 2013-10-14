"""
A unit testing module for the ROIM method (which identifies Rossby
wave trains from Hovmoller diagrams).

Functions/methods tested:
    calc_rwt.find_new_objects

"""

import unittest
import numpy

import os
import sys

module_dir = os.path.join(os.environ['HOME'], 'data_processing', 'roim')
sys.path.insert(0, module_dir)
import calc_rwt

import pdb

class testNewObject(unittest.TestCase):
    """Test class for testing new Rossby wave objects"""

    def test_simple_case(self):
        """Test for simple case where there is no object that staddles
	the 0/360 longitude [test for success]"""
		
	data = [0, 1, 2, 3, 0, 0, 3, 4, 0, 0, 0, 2]
	result = calc_rwt.find_new_objects(data)
        answer = [[1, 2, 3], [6, 7], 11]	
        
	numpy.testing.assert_equal(result, answer)

    def test_periodical(self):
        """Test for object that straddles the 0/360 longitude
	[test for success]"""
	
	data = [5, 1, 2, 3, 0, 0, 3, 4, 0, 0, 0, 2]
	result = calc_rwt.find_new_objects(data)
        answer = [[11, 12, 13, 14, 15], [6, 7]]	
        
	numpy.testing.assert_equal(result, answer)
	


if __name__ == '__main__':
    unittest.main()
