"""
A unit testing module for climate indices.

Functions/methods tested:
  calc_climate_index.calc_zw3  

"""

# Import general Python modules

import sys, os
import unittest
import pdb

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

module_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(module_dir)

try:
    import calc_climate_index as cci
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')




##########################
## unittest test clases ##
##########################

class testzw3(unittest.TestCase):
    """Test class for testing the ZW3 index"""
    
    def setUp(self):
        """Define the defaults"""        

        self.index = 'zw3'
        self.ifile_monthly = '/mnt/meteo0/data/simmonds/dbirving/Merra/data/zg_Merra_500hPa_monthly_native.nc'
	self.var_monthly = 'zg'
	self.ifile_daily = '' 
	self.var_daily = ''
        self.base_period = '' # not actually used
    
    def test_monthly(self):
        """Test for monthly input data [test for success]"""

        result, var_atts, global_atts, time_axis = cci.calc_zw3(self.index, self.ifile_monthly, self.var_monthly, self.base_period)
        
