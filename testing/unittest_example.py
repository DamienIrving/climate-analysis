"""
A unit testing module for coordinate system rotation.

Functions/methods tested:
    coordinate_rotation.adjust_lon_range

"""

import unittest
import coordinate_rotation as rot  # a module I once wrote


##########################
## unittest test clases ##
##########################

class testLonAdjust(unittest.TestCase):
    """Test class for testing the adjustment of longitude values."""

    def setUp(self):
        """Define the test data."""        

        self.data_degrees = numpy.array([0., 360., 378., 60., -30., -810.])
        self.data_radians = numpy.array([0., 2*pi, 2.1*pi, pi/3., -pi/6., -4.5*pi])


    def test_degrees_start0(self):
        """Test for data in degrees, start point = 0.0 [test for success]"""
        
        result = rot.adjust_lon_range(self.data_degrees, radians=False, start=0.0)
        answer = [0.0, 0.0, 18.0, 60.0, 330.0, 270.0] 
        numpy.testing.assert_array_equal(result, answer)


    def test_degrees_start180(self):
        """Test for data in degrees, start point = -180 [test for success]"""

        result = rot.adjust_lon_range(self.data_degrees, radians=False, start=-180.0)
        answer = [0., 0., 18., 60., -30., -90.] 
        numpy.testing.assert_array_equal(result, answer)	
    
    
    def test_radians_start0(self):
        """Test for data in radians, start point = 0.0 [test for success]"""

        result = rot.adjust_lon_range(self.data_radians, start=0.0)
        answer = [0., 0., 0.1*pi, pi/3., (11./6.)*pi, 1.5*pi] 
        numpy.testing.assert_array_equal(result, answer)        
        
        
    def test_radians_start180(self):
        """Test for data in radians, start point = -pi [test for success]"""

        result = rot.adjust_lon_range(self.data_radians, start=-pi)
        answer = [0., 0., 0.1*pi, pi/3., -pi/6., -0.5*pi] 
        numpy.testing.assert_array_equal(result, answer)	        


if __name__ == '__main__':
    unittest.main()
    
