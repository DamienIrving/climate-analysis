"""
Filename:     plot_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots composite maps

"""

import os
import sys
import argparse

vis_dir = os.path.join(os.environ['HOME'], 'phd', 'visualisation')
sys.path.insert(0, vis_dir)
import plot_map as pm

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def main(inargs):
    """Run the program"""
        
    ifile_list = []  #elements must be (fname, var)
    stipple_list = []
    for ifile in inargs.files:	
        ifile_list.append((ifile, inargs.variable))
	stipple_list.append((ifile, 'p'))

    indata_list = pm.extract_data(ifile_list, region=inargs.region)
    stipdata_list = pm.extract_data(stipple_list, region=inargs.region)

    pm.multiplot(indata_list,
		 ofile=inargs.ofile,
		 units=inargs.units,
		 img_headings=inargs.headings,
		 draw_axis=True,
		 delat=30, delon=30,
		 contour=True,
                 stipple_data=stipdata_list, stipple_threshold=0.05, stipple_size=1.0, stipple_thin=5,
		 ticks=inargs.ticks, discrete_segments=inargs.segments, colourbar_colour=inargs.palette,
                 projection=inargs.projection, 
                 extend='both',
                 image_size=8)


if __name__ == '__main__':

    extra_info="""
example (abyss.earthsci.unimelb.edu.au):
    cdat plot_composite.py tas
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-annual.nc
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-DJF.nc
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-MAM.nc
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-JJA.nc
    hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-SON.nc
    --headings annual DJF MAM JJA SON
    --ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0
    --units temperature_anomaly_(Celsius)

"""
  
    description='Plot composite.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("variable", type=str, 
                        help="name of variable to plot")
    parser.add_argument("files", type=str, nargs='+', 
                        help="composite files to plot (assumed that these came from calc_composite.py")
    
    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    
    # Colors
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="List of tick marks to appear on the colour bar [default: auto]")
    parser.add_argument("--segments", type=str, nargs='*', default=None,
                        help="List of colours to appear on the colour bar")
    parser.add_argument("--palette", type=str, default='RdBu_r',
                        help="Colourbar name [default: RdBu_r]")

    # Region/projection
    parser.add_argument("--projection", type=str, default='nsper', choices=['cyl', 'nsper'],
                        help="Map projection [default: nsper]")
    parser.add_argument("--region", type=str, choices=nio.regions.keys(), default='world-psa',
                        help="Region over which plot the composite [default = world_psa]")
    
    # Headings/labels
    parser.add_argument("--headings", type=str, nargs='*', default=None,
                        help="List of headings corresponding to each of the input files [default = none]")
    parser.add_argument("--units", type=str, default=None, 
                        help="Units label")


    args = parser.parse_args() 
    main(args)
