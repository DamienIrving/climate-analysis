"""
Filename:     calc_hovmoller.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Write data to a hovmoller diagram

"""

import sys
import os

import argparse
import numpy

import MV2
import cdutil

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio

import pdb


def clip_data(data, method, threshold):
    """Define the envelope clipping threshold.
    
    Method can be 'absolute' or 'scaled'.
      - Absolute simply sets all data < threshold to zero
      - Scaled sets all data < tau to zero, where tau is
        the spatial average of the input data for each timestep
	mutliplied by threshold (see equation 1, Glatt et al 2013)
      
    """

    if method == 'absolute':
        clipped_data = MV2.where(data < threshold, 0.0, data)

    elif method == 'scaled':

        # Calulate the spatial average of the input data at each timestep #
	
	pdb.set_trace()
	
	ave_axes = data.getOrder().translate(None, 't')
        spatial_ave = cdutil.averager(data, axis=ave_axes, weights=['unweighted']*len(ave_axes))

        # Resize the spatial average so it matches the input data #
	
	try:
	    index = data.getOrder().index('t')
	    tile_shape = list(data.shape)
	    tile_shape.pop(index)
	except ValueError:
	    tile_shape = data.shape
	
        for dim in ave_axes:
	    spatial_ave = numpy.expand_dims(spatial_ave, axis=1)     #spatial_ave[:, numpy.newaxis]
	spatial_ave = numpy.tile(spatial_ave, tile_shape)
	
	# Calculate the clipping threshold (tau) and apply it to data #
	
	tau = threshold * spatial_ave
        clipped_data = MV2.where(data < tau, 0.0, data)
    
    
    return clipped_data
        

def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude']))
 
    # Clip the data #

    clipped_data = clip_data(indata.data, inargs.clip_method, inargs.clip_threshold)

    # Collapse the spatial dimension #

    ave_axes = clipped_data.getOrder().translate(None, 'tx')
    hov_data = cdutil.averager(clipped_data, axis=ave_axes, weights=['unweighted']*len(ave_axes))
  
    # Write output file #

    var_atts = {'id': 'env',
                'name': 'Clipped wave envelope',
                'long_name': 'Clipped wave envelope, presented on a Hovmoller diagram (i.e. time, longitude axes)',
                'units': 'm s-1',
                'history': 'Clip method: %s. Clip threshold: %s. Latitude range: %s to %s' %(inargs.clip_method, 
                                                                                             inargs.clip_threshold,
                                                                                             str(indata.data.getLatitude()[0]),
                                                                                             str(indata.data.getLatitude()[-1]))}
    indata_list = [indata,]
    outdata_list = [hov_data,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [hov_data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, 'Hovmoller diagram of clipped wave envelope', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_envelope.py 
  /work/dbirving/datasets/Merra/data/processed/vrot-env-w567_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270.nc env
  absolute 12
  /work/dbirving/datasets/Merra/data/processed/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270_absolute12.nc
  --latitude -15 15

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Create Hovmoller diagram'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("clip_method", type=str, choices=['absolute', 'scaled'],
                        help="Clipping can be an absolute threshold or scaled relative to the mean")
    parser.add_argument("clip_threshold", type=float,
                        help="Threshold for the clipping")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region [default = entire]")
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Longitude range [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")
    
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
