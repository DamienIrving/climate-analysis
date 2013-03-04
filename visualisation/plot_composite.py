"""
Filename:     plot_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots composite maps


Updates | By | Description
--------+----+------------
4 March 2013 | Damien Irving | Initial version.

"""

import os
import sys
import argparse

module_dir = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir)
import plot_map

import numpy


def main(inargs):

    # Dimensions
    rows,cols = plot_map.dimensions(len(inargs.var))
    dims = [rows,cols]
    
    # Input file list
    ifiles = [inargs.infile] * len(inargs.var) 
    ifile_list = plot_map.shuffle(ifiles, rows, cols)
    
    # Variable list
    variable_list = plot_map.shuffle(inargs.var, rows, cols)
            
    # Image headings
    img_headings = []
    for var in inargs.var:
	img_headings.append(var[-3:])
    img_headings_list = plot_map.shuffle(img_headings, rows, cols)

    plot_map.multiplot(ifile_list,
                       variable_list,
		       dimensions=dims,
		       ofile=inargs.ofile,
		       title=inargs.title,
                       colourbar_colour=inargs.palette,
		       img_headings=img_headings_list,
		       draw_axis=True,
		       delat=30,delon=30,
		       contour=True,
		       ticks=inargs.ticks,
		       discrete_segments=inargs.segments,
                       projection=inargs.projection,
#                       region='TROPICAL_PACIFIC',
#                       extend='both'
		       )


if __name__ == '__main__':

    extra_info="""
example (abyss.earthsci.unimelb.edu.au):
    /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_composite.py 
    /work/dbirving/processed/composites/data/ts-sf_Merra_surface-250hPa_monthly-anom-wrt-1981-2010-pc2_native_composite-1979-2011.nc 
    ts_ann ts_djf ts_mam ts_jja ts_son 
    --ofile /work/dbirving/processed/composites/figures/ts-sf_Merra_surface-250hPa_monthly-anom-wrt-1981-2010-pc2_native_composite-1979-2011_nsper.png
    --ticks -2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5,3.0

Author
    Damien Irving, 22 Jun 2012

"""
  
    description='Plot composite'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("var", type=str, nargs='*', help="Input file variables")

    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="List of tick marks to appear on the colour bar [default: auto]")
    parser.add_argument("--segments", type=str, nargs='*', default=None,
                        help="List of comma seperated colours to appear on the colour bar")
    parser.add_argument("--title", type=str, default='composites',
                        help="plot title [default: None]")
    parser.add_argument("--palette", type=str, default='RdBu_r',
                        help="Colourbar name [default: RdBu_r]")
    parser.add_argument("--projection", type=str, default='cyl', choices=['cyl', 'nsper'],
                        help="Map projection [default: cylindrical]")
#    parser.add_argument("--region", type=str, default='cyl', choices=['cyl', 'nsper'],
#                        help="Map projection [default: cylindrical]")

    
    args = parser.parse_args() 

    main(args)
