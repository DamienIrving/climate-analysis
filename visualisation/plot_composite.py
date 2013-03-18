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
import plot_map as pm

import numpy
import cdms2
import MV2
import genutil


indir = '/work/dbirving/processed/composites/data/'
months = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
          7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

def main(inargs):

    if inargs.type == 'mean':
        
	ifile_list = []
	stipple_list = []
	for season in ['ann', 'djf', 'mam', 'jja', 'son']:
	    ifile_list.append((indir+'ts-composite-sf_Merra_surface-250hPa_monthly-'+season+'-anom-wrt-1979-2011-pc2-lower-1std_native-sh.nc', 
	                       'ts', 'None', 'None'))
	    stipple_list.append((indir+'ts-composite-sf_Merra_surface-250hPa_monthly-'+season+'-anom-wrt-1979-2011-pc2-lower-1std_native-sh.nc', 
	                         'p', 'None', 'None'))	       
	
        indata = pm.extract_data(ifile_list)
        stipdata = pm.extract_data(stipple_list)
        
        dims = [3, 2]
	img_headings_list = ['Annual (63)', 'DJF (16)', 'MAM (13)', 'JJA (17)', 'SON (16)']	
	image_size = 8
        title = 'Surface temperature composite - Merra'
        
        if not inargs.ticks:
            ticks = [-3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
        else:
            ticks = inargs.ticks

	pm.multiplot(indata,
		     dimensions=dims,
		     ofile=inargs.ofile,
		     title=title,
		     img_headings=img_headings_list,
		     draw_axis=True,
		     delat=30, delon=30,
		     contour=True,
                     stipple_data=stipdata, stipple_threshold=0.05, stipple_size=1.0, stipple_thin=5,
		     ticks=ticks, discrete_segments=inargs.segments, colourbar_colour=inargs.palette,
                     projection=inargs.projection, 
                     extend='both',
                     image_size=image_size
		     )
    else:

        infile = indir+'ts-composite-sf_Merra_surface-250hPa_monthly-'+inargs.type+'-anom-wrt-1979-2011-pc2-lower-1std_native-sh.nc'
        cfile = '/work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc'

        fin = cdms2.open(infile)
        ts_data = fin('ts')
        ts_ave = MV2.average(ts_data, axis=0)
        datetimes = ts_data.getTime().asComponentTime()
        fin.close()

        # Calculate the sf mean field
        pick = genutil.picker(time=datetimes)

        fin = cdms2.open(cfile)
        sf_data = fin('sf')(pick)
        print sf_data.shape        
        sf_ave = MV2.average(sf_data, axis=0)
        fin.close()
       
        # Get data for the individual fields
        ifile_list = []
	contour_list = []
        img_headings_list = [inargs.type+' average',]
        for dt in datetimes:
            date = str(dt).split(' ')[0]
            year = date.split('-')[0]
            month = months[int(date.split('-')[1])]
            ifile_list.append((infile, 'ts', date, date))
            contour_list.append((cfile, 'sf', date, date))
            img_headings_list.append(month+' '+year)

        indata = pm.extract_data(ifile_list)
        contdata = pm.extract_data(contour_list)

        indata.insert(0, ts_ave)
        contdata.insert(0, sf_ave)

        rows, cols = pm.get_dimensions(len(datetimes)+1)
        dims = [rows, cols]
        image_size = 6
        title = 'Composite members - %s' %(inargs.type) 
        
        if not inargs.ticks:
            ticks = [-5.0, -4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        else:
            ticks = inargs.ticks

        pm.multiplot(indata,
		     dimensions=dims,
		     ofile=inargs.ofile,
		     title=title,
		     img_headings=img_headings_list,
		     draw_axis=True,
		     delat=30, delon=30,
		     contour=True,
		     ticks=ticks, discrete_segments=inargs.segments, colourbar_colour=inargs.palette,
                     contour_data=contdata,
                     projection=inargs.projection, 
                     extend='both',
                     image_size=image_size
		     )


if __name__ == '__main__':

    extra_info="""
example (abyss.earthsci.unimelb.edu.au):
    /usr/local/uvcdat/1.2.0rc1/bin/cdat plot_composite.py mean
    --ofile /work/dbirving/processed/composites/figures/ts-sf_Merra_surface-250hPa_monthly-anom-wrt-1981-2010-pc2_native_composite-1979-2011_nsper.png
    --ticks -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0

"""
  
    description='Plot composite.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("type", type=str, choices=['mean', 'ann', 'djf', 'mam', 'jja', 'son'], 
                        help="type of plot")
    
    parser.add_argument("--ofile", type=str, default='test.png',
                        help="name of output file [default: test.png]")
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="List of tick marks to appear on the colour bar [default: auto]")
    parser.add_argument("--segments", type=str, nargs='*', default=None,
                        help="List of colours to appear on the colour bar")
    parser.add_argument("--palette", type=str, default='RdBu_r',
                        help="Colourbar name [default: RdBu_r]")
    parser.add_argument("--projection", type=str, default='nsper', choices=['cyl', 'nsper'],
                        help="Map projection [default: nsper]")

    
    args = parser.parse_args() 

    main(args)
