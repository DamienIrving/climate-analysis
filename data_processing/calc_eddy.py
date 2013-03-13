"""
GIT INFO: $Id$
Filename:     calc_eddy.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  


Updates | By | Description
--------+----+------------
13 March 2013 | Damien Irving | Initial version.

"""

import os
import sys

import argparse

import cdms2
import cdutil
import MV2

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def calc_eddy_component(input_data):
    """Remove zonal mean."""
    
    assert isinstance(input_data, nio.InputData)
    assert 'x' == input_data.data.getOrder()[-1], \
    """Input data must have a longitude axis as the final axis."""
    
    data = input_data.data
    zonal_mean = cdutil.averager(data, axis='x', weights='equal')

    shape = list(zonal_mean.shape)
    shape.append(1)
    zonal_mean_reshaped = MV2.reshape(zonal_mean, shape)
    

    return data - zonal_mean_reshaped  



def main(inargs):
    """Run the program"""
    
    # Open the input file #

    indata = nio.InputData(inargs.infile, inargs.variable)
      
    # Calculate the monthly climatology and anomaly #
    
    eddy_data = calc_eddy_component(indata)

    # Write output file #

    attributes = {'id': 'e'+inargs.variable,
                 'long_name': 'Eddy component of '+indata.data.long_name,
                 'units': indata.data.units,
                 'history': 'Eddy component means zonal average removed.'}

    indata_list = [indata,]
    outdata_list = [eddy_data,]
    outvar_atts_list = [attributes,]
    outvar_axes_list = [indata.data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, 'eddy component (zonal mean removed)', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)

   
if __name__ == '__main__':

    extra_info = """
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_eddy.py 
  /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly_native.nc sf
  /work/dbirving/datasets/Merra/data/processed/esf_Merra_250hPa_monthly_native.nc
"""    	

    description = 'Calculate the eddy component of a given field (i.e. remove the zonal mean).'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)	
