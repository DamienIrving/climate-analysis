"""
GIT INFO: $Id$
Filename:     calc_monthly_anomaly.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  


Updates | By | Description
--------+----+------------
23 August 2012 | Damien Irving | Initial version.

"""

import os
import sys

import argparse

import cdutil
import MV2

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def calc_zonal_anomaly(indata):
    """Calculate monthly anomaly."""  
    
    # Calculate the zonal mean climatology #
    
    zonal_mean = cdutil.averager(indata, axis='x')
    
    # Broadcast to same shape and subract from data #
    
    

    return zonal_anomaly


def main(inargs):
    """Run the program"""
    
    # Open the input file #

    indata = nio.InputData(inargs.infile, inargs.variable)
      
    # Calculate the zonal anomaly #
    
    zonal_anomaly = calc_zonal_anomaly(indata.data)

    # Write output file #

    attributes = {'id': inargs.variable,
                 'long_name': full_data.data.long_name,
                 'units': full_data.data.units,
                 'history': 'The zonal mean has been subtracted at each time step.'}

    outdata_list = [monthly_anomaly,]
    outvar_atts_list = [attributes,]
    outvar_axes_list = [indata.data.getAxisList(),]
 
    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     indata.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)
   
   
if __name__ == '__main__':

    extra_info = """
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_zonal_anomaly.py 
  zg_Merra_250hPa_monthly_native.nc zg_Merra_250hPa_monthly-zonal-anom_native.nc
"""    	

    description = 'Calculate the zonal anomaly (i.e. subtract the zonal mean at each timestep).'
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
