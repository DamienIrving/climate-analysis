"""
Filename:     plot_zonal_anomaly.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot the zonal anomaly for a given timescale

"""

import os
import sys
import argparse

module_dir = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir)
import plot_map

module_dir2 = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir2)
import netcdf_io as nio


def main(inargs):
    """Create the plot"""

    # Read the input data
    if inargs.time:
        time_selection= [inargs.time[0], inargs.time[1], 'none']    
        indata = nio.InputData(inargs.infile, inargs.var, time=time_selection)
    else:
        indata = nio.InputData(inargs.infile, inargs.var)

    assert indata.data.getOrder()[0] == 't', \
    'Time must be the first dimension' 

    # Create data and image heading arrays #
    times = indata.data.getTime().asComponentTime() 
    data_list = []
    header_list = []
    for i in range(0, len(times)):
        year, month, day = str(times[i]).split(' ')[0].split('-')
	if inargs.timescale == 'daily':
	    date_abbrev = year+'-'+month+'-'+day
	elif inargs.timescale == 'monthly': 
	    date_abbrev = year+'-'+month
	else:
	    date_abbrev = year
	    
        data_list.append(indata.data[i, ::])
	header_list.append(date_abbrev)

    plot_map.multiplot(data_list,
		       ofile=inargs.ofile,
		       dimensions=plot_map.get_dimensions(len(data_list)),
		       title=inargs.title,
		       region='world-dateline',
		       units=indata.data.units,
                       draw_axis=True,
		       delat=10, delon=30,
		       contour=True,
		       ticks=inargs.ticks, colourbar_colour='RdBu_r',
		       img_headings=header_list,
        	       projection='spstere', 
        	       extend='both',
        	       image_size=inargs.image_size)


if __name__ == '__main__':

    extra_info="""
example (vortex.earthsci.unimelb.edu.au):
    /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_zonal_anomaly.py
    /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/zg_Merra_250hPa_monthly-zonal-anom_native.nc 
    zg monthly
    --time 2003-06-01 2003-06-30 none
    --ofile /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/figures/zg_Merra_250hPa_monthly-zonal-anom_native_2005.png
    --ticks -250 -200 -150 -100 -50 0 50 100 150 200 250 
    --title Monthly_mean_zonal_anomaly,_250hPa_geopotential_height
    
"""
  
    description='Plot the zonal anomaly for a given timescale'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="envelope file")
    parser.add_argument("var", type=str, help="envelope variable")
    parser.add_argument("timescale", type=str, choices=['daily', 'monthly', 'annual'], 
                         help="timescale of the data")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period (after timescale filtering) [default = entire]")

    parser.add_argument("--ofile", type=str, default='test.png', 
                        help="name of output file")

    parser.add_argument("--title", type=str, default=None, 
                        help="Title for the plot (underscores will be removed)")
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="List of tick marks to appear on the colour bar [default: auto]")
    parser.add_argument("--image_size", type=float, default=7, 
                        help="size of image [default: 7]")

    
    args = parser.parse_args() 

    main(args)
