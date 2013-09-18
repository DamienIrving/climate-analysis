"""
Filename:     plot_envelope.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plot wave envelope and associated wind and streamfunction anomalies

"""

import os
import sys
import argparse

module_dir = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir)
import plot_map as pm

import numpy
import cdms2
import MV2


def main(inargs):



    pm.multiplot(indata,
		 dimensions=dims,
		 ofile=inargs.ofile,
		 title=title,
		 units=units,
		 img_headings=img_headings_list,
		 draw_axis=True,
		 delat=30, delon=30,
		 contour=True,
		 ticks=ticks, discrete_segments=inargs.segments, colourbar_colour=inargs.palette,
        	 contour_data=contdata, contour_ticks=cticks,
		 uwnd_data=wafxdata, vwnd_data=wafydata, quiver_type='waf', quiver_thin=2,
		 quiver_scale=220, quiver_width=0.002,
        	 projection=inargs.projection, 
        	 extend='both',
        	 image_size=image_size
		 )


if __name__ == '__main__':

    extra_info="""
example (abyss.earthsci.unimelb.edu.au):
    /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_envelope.py
    /work/dbirving/test_data/vrot-env_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360-np30-270.nc
    vrot 30 270 0 0 
    /work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc ua
    /work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc va
    /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc sf

    --ticks 0 1 2 3 4 5 6 7 8 9 10 11 12

"""
  
    description='Plot wave envelope and associated wind and streamfunction anomalies'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("env_file", type=str, help="envelope file")
    parser.add_argument("env_var", type=str, help="envelope variable")
    parser.add_argument("np_lat", type=float, help="north pole latitude used for envelope extraction")
    parser.add_argument("np_lon", type=float, help="north pole longitude used for envelope extraction")
    parser.add_argument("pm_lat", type=float, help="prime meridian point latitude used for envelope extraction")
    parser.add_argument("pm_lon", type=float, help="prime meridian point longitude used for envelope extraction")
    parser.add_argument("u_file", type=str, help="zonal wind anomaly file")
    parser.add_argument("u_var", type=str, help="zonal wind anomaly variable")
    parser.add_argument("v_file", type=str, help="meridional wind anomaly file")
    parser.add_argument("v_var", type=str, help="meridional wind anomaly variable")
    parser.add_argument("sf_file", type=str, help="streamfunction anomaly file")
    parser.add_argument("sf_var", type=str, help="streamfunction anomaly variable")

    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="List of tick marks to appear on the colour bar [default: auto]")
    parser.add_argument("--segments", type=str, nargs='*', default=None,
                        help="List of colours to appear on the colour bar")
    parser.add_argument("--palette", type=str, default='RdBu_r',
                        help="Colourbar name [default: RdBu_r]")
    parser.add_argument("--projection", type=str, default='cyl', choices=['cyl', 'nsper'],
                        help="Map projection [default: nsper]")
    
    args = parser.parse_args() 

    main(args)
