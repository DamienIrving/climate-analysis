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

import MV2

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def calc_monthly_climatology(base_data):
    """Calculate monthly climatology."""
    
    ntime, nlat, nlon = MV2.shape(base_data.data)
    monthly_climatology = MV2.ones([12, nlat, nlon]) * base_data.data.missing_value
    
    for i in range(0, 12):
        monthly_climatology[i, :, :] = MV2.average(base_data.data[i:ntime:12, :, :], axis=0) 

    monthly_climatology = MV2.masked_values(monthly_climatology, base_data.data.missing_value)

    return monthly_climatology


def calc_monthly_anomaly(complete_data, base_data):
    """Calculate monthly anomaly."""  
    
    # Calculate the monthly climatology #
    
    monthly_climatology = calc_monthly_climatology(base_data)
    
    # Calculate the monthly anomaly #
    
    ntime, nlat, nlon = MV2.shape(complete_data.data)
    months = complete_data.months()
    monthly_anomaly = MV2.ones([ntime, nlat, nlon]) * base_data.data.missing_value
    for i in range(0, ntime):
	month_index = months[i]
	monthly_anomaly[i, :, :] = MV2.subtract(complete_data.data[i, :, :], monthly_climatology[month_index-1, :, :])

    monthly_anomaly = MV2.masked_values(monthly_anomaly, base_data.data.missing_value)

    return monthly_anomaly


def main(inargs):
    """Run the program"""
    
    # Open the input file #

    full_data = nio.InputData(inargs.infile, inargs.variable)
    base_data = nio.InputData(inargs.infile, inargs.variable, time=inargs.base)
      
    # Calculate the monthly climatology and anomaly #
    
    monthly_anomaly = calc_monthly_anomaly(full_data, base_data)

    # Write output file #

    attributes = {'id': inargs.variable,
                 'long_name': full_data.data.long_name,
                 'units': full_data.data.units,
                 'notes': 'Calculated anomaly relative to the %s to %s monthly climatology.'  %(inargs.base[0], inargs.base[1])}

    indata_list = [full_data,]
    outdata_list = [monthly_anomaly,]
    outvar_atts_list = [attributes,]
    outvar_axes_list = [(full_data.data.getTime(), 
                        full_data.data.getLatitude(), 
                        full_data.data.getLongitude()),]

    nio.write_netcdf(inargs.outfile, 'monthly anomaly', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)

   
if __name__ == '__main__':

    extra_info = """
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_monthly_anomaly.py 
  /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly_native-ocean.nc ts
  /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc
"""    	

    description = 'Take a monthly timeseries and calculate the monthly anomaly timeseries.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--base", type=str, nargs=2, metavar=('START', 'END'), default=['1981-01-01', '2010-12-31'],
                        help="start and end dates for the base period [default: '1981-01-01', '2010-12-31']")

    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)	
