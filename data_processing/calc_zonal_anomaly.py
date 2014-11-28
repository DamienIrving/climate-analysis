"""
Filename:     calc_zonal_anomaly.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculate the zonal anomaly (i.e. subtract the zonal mean at each timestep)

"""

# Import general Python modules #

import os, sys
import argparse
import numpy
import cdutil

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')
    
    
# Define fuctions #

def calc_zonal_anomaly(indata):
    """Calculate zonal anomaly."""  
    
    assert indata.getOrder()[-1] == 'x', \
    'The last dimension must be longitude'
        
    # Calculate the zonal mean climatology #
    zonal_mean = cdutil.averager(indata, axis='x')
    
    # Broadcast to same shape and subract from data #
    zonal_mean_shape = list(zonal_mean.shape)
    zonal_mean_shape.append(1)
    zonal_mean_added_dim = numpy.reshape(zonal_mean, zonal_mean_shape)
    zonal_mean_field = numpy.repeat(zonal_mean_added_dim, indata.shape[-1], axis=-1)
    zonal_anomaly = indata - zonal_mean_field

    return zonal_anomaly


def main(inargs):
    """Run the program"""
    
    # Open the input file #
    indata = nio.InputData(inargs.infile, inargs.variable, **nio.dict_filter(vars(inargs), ['time',]))
      
    # Calculate the zonal anomaly #
    zonal_anomaly = calc_zonal_anomaly(indata.data)

    # Write output file # 
    attributes = {'id': inargs.variable,
                 'long_name': indata.data.long_name,
                 'units': indata.data.units,
                 'notes': 'The zonal mean has been subtracted at each time step.'}

    outdata_list = [zonal_anomaly,]
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
  /usr/local/uvcdat/1.3.0/bin/cdat calc_zonal_anomaly.py 
  zg_Merra_250hPa_monthly_native.nc zg zg_Merra_250hPa_monthly-zonal-anom_native.nc
"""    	

    description = 'Calculate the zonal anomaly (i.e. subtract the zonal mean at each timestep).'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)	
