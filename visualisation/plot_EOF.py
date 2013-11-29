"""
Filename:     plot_EOF.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots the spatial EOF


Updates | By | Description
--------+----+------------
5 November 2012 | Damien Irving | Initial version.

"""


### Import required modules ###

import os
import sys

import argparse

import cdms2 

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio

module_dir = os.path.join(os.environ['HOME'], 'phd', 'visualisation')
sys.path.insert(0, module_dir)
import plot_map


def main(inargs):

    # Dimensions
    rows, cols = plot_map.get_dimensions(inargs.neofs)
    dims = [rows, cols]
    
    # Input data list
    indata_list = []
    var_exp_list = []
    for i in range(1, inargs.neofs + 1):
        var = 'eof'+str(i)
	indata_list.append(nio.InputData(inargs.infile, var, region=inargs.region).data)
    
    # Image headings
    img_headings = []
    for i in range(1, inargs.neofs + 1):
	img_headings.append('EOF%s  (%3.1f%%)' %(str(i), float(indata_list[i-1].var_exp) * 100.0))

    plot_map.multiplot(indata_list,
		       dimensions=dims,
		       img_headings=img_headings,
		       draw_axis=True,
		       delat=30, delon=30,
		       contour=True,
		       **nio.dict_filter(vars(inargs), nio.list_kwargs(plot_map.multiplot)))


if __name__ == '__main__':

    extra_info = """
example:
  /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_EOF.py  
  /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF_monthly-1979-2012_native-eqpacific.nc 
  eqpacific
  --ofile /work/dbirving/processed/indices/figures/sf_Merra_250hPa_EOF_monthly-1979-2012_native-eqpacific.png
  --title 250hPa_streamfunction_EOF_analysis,_1979-2012,_Merra
  --ticks -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0
  
  /usr/local/uvcdat/1.2.0/bin/cdat plot_EOF.py 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/eof-sf_Merra_250hPa_monthly-anom-wrt-1979-2011-annual_native-sh.nc sh-psa 
  --ticks -1 -0.8 -0.6 -0.4 -0.2 0.0 0.2 0.4 0.6 0.8 1.0 
  --search_paths 30 270 190 340 -20 20 5
  --title 250hPa_streamfunction_anomaly_EOF_analysis,_1979-2012,_Merra
  
"""

    description='Plot EOF spatial maps.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("infile", type=str, help="input file name")
    parser.add_argument("region", type=str, choices=nio.regions.keys(), 
                        help="region name")
			
    parser.add_argument("--neofs", type=int, default=4, 
                        help="number of EOFs to plot")
    parser.add_argument("--units", type=str, 
                        help="units label for the colourbar")
    parser.add_argument("--ofile", type=str,
                        help="name of output file [default = test.png]")
    parser.add_argument("--ticks", type=float, nargs='*',
                        help="List of tick marks to appear on the colour bar")
    parser.add_argument("--discrete_segments", type=str, nargs='*',
                        help="List of colours to appear on the colour bar")
    parser.add_argument("--title", type=str, 
                        help="plot title [default = None]")
    parser.add_argument("--colourbar_colour", type=str, default='RdBu_r',
                        help="Colourbar name [default = RdBu_r]")
    parser.add_argument("--search_paths", type=float, nargs=7, 
                        metavar=('NP_LAT', 'NP_LON', 'START_LON', 'END_LON', 'START_LAT', 'END_LAT', 'LAT_STRIDE'),
                        help="draw the search paths for the specified north pole [default: None]")
    
    args = parser.parse_args() 
    
    main(args)
