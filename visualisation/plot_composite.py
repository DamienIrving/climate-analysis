"""
Filename:     plot_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots composite maps

"""

# Import general Python modules #

import os
import sys
import argparse
import re
import pdb

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
vis_dir = os.path.join(repo_dir, 'visualisation')
sys.path.append(vis_dir)

try:
    import plot_map as pm
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from somewhere within the phd git repo')


# Define functions #

def extract_data(file_list, variable):
    """Return lists of the data and corresponding composite sample sizes:
    [size included, size excluded]
    
    """

    data_list = []
    sample_list = []
    for infile in file_list:
        temp_data = nio.InputData(infile, variable)
	try:
	    temp_history = temp_data.data.attributes['history']
	    matches = re.findall(r'(size=[0-9]+)', temp_history)
	    if matches:
	        sample_sizes = map(lambda x: x.split('=')[1], matches)
	    else:
	        sample_sizes = None
	except KeyError:
	    sample_sizes = None
	
	sample_list.append(sample_sizes)
	data_list.append(temp_data.data)
    
    return data_list, sample_list
    

def main(inargs):
    """Run the program"""
        
    indata_list, temp = extract_data(inargs.files, inargs.variable)
    stipple_list, sample_list = extract_data(inargs.files, 'p')
    
    if inargs.stippling:
        stipdata_list = stipple_list
    else:
        stipdata_list = None

    if inargs.contour_files:
        contour_list, temp = extract_data(inargs.contour_files, inargs.contour_var)
    else:
        contour_list = None
	
    if inargs.dimensions:
        dimensions = inargs.dimensions
    else:
        dimensions = pm.get_dimensions(len(indata_list))

    if inargs.raphael_boxes:
        box1 = (-50, -45, 45, 60, 'blue', 'solid')
	box2 = (-50, -45, 161, 171, 'blue', 'solid')
	box3 = (-50, -45, 279, 289, 'blue', 'solid')
	box_list = [box1, box2, box3]
    else:
        box_list = []
 
    if inargs.headings:
        if sample_list[0]:
	    assert len(inargs.headings) == len(sample_list), \
	    'Number of headings (%s) and samples (%s) must be the same' %(len(inargs.headings), len(sample_list))
            heading_list = []
	    for i in range(0, len(inargs.headings)):
	        included_sample_size = sample_list[i][0]
		excluded_sample_size = sample_list[i][1]
		total_size = float(included_sample_size) + float(excluded_sample_size)
		heading_list.append(inargs.headings[i]+' ('+included_sample_size+'/'+str(int(total_size))+')') 
        else:
	    heading_list = inargs.headings    
 
    pm.multiplot(indata_list,
                 dimensions=dimensions,
		 region=inargs.region,
		 ofile=inargs.ofile,
		 units=inargs.units,
		 img_headings=heading_list,
		 draw_axis=True,
		 delat=30, delon=30,
		 contour=True,
		 contour_data=contour_list, contour_ticks=inargs.contour_ticks,
                 stipple_data=stipdata_list, stipple_threshold=0.05, stipple_size=1.0, stipple_thin=5,
		 ticks=inargs.ticks, discrete_segments=inargs.segments, colourbar_colour=inargs.palette,
                 projection=inargs.projection, 
                 extend=inargs.extend,
		 box=box_list,
                 image_size=inargs.image_size)


if __name__ == '__main__':

    extra_info="""
example (abyss.earthsci.unimelb.edu.au):
    cdat plot_composite.py tas
    tas-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-annual.nc
    tas-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-DJF.nc
    tas-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-MAM.nc
    tas-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-JJA.nc
    tas-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-SON.nc
    --headings annual DJF MAM JJA SON
    --ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0
    --units temperature_anomaly_(Celsius)
    --contour_var sf
    --contour_files
    sf-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-annual.nc
    sf-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-DJF.nc
    sf-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-MAM.nc
    sf-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-JJA.nc
    sf-hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-SON.nc
    --contour_ticks -30 -25 -20 -15 -10 -5 0 5 10 15 20 25 30

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
    parser.add_argument("--dimensions", type=int, nargs=2, default=None, metavar=('ROWS', 'COLUMNS'), 
                        help="matrix dimensions [default: 1 row]")
    parser.add_argument("--image_size", type=float, default=8, 
                        help="size of image [default: 8]")
    
    # Colors
    parser.add_argument("--ticks", type=float, nargs='*', default=None,
                        help="List of tick marks to appear on the colour bar [default: auto]")
    parser.add_argument("--segments", type=str, nargs='*', default=None,
                        help="List of colours to appear on the colour bar")
    parser.add_argument("--palette", type=str, default='RdBu_r',
                        help="Colourbar name [default: RdBu_r]")
    parser.add_argument("--extend", type=str, choices=('both', 'neither', 'min', 'max'), default='neither',
                        help="selector for arrow points at either end of colourbar [default: 'neither']")
			
    # Region/projection
    parser.add_argument("--projection", type=str, default='nsper', choices=['cyl', 'nsper', 'spstere'],
                        help="Map projection [default: nsper]")
    parser.add_argument("--region", type=str, choices=nio.regions.keys(), default='sh-psa-extra',
                        help="Region over which plot the composite [default = sh-psa-extra]")
    
    # Headings/labels
    parser.add_argument("--headings", type=str, nargs='*', default=None,
                        help="List of headings corresponding to each of the input files [default = none]")
    parser.add_argument("--units", type=str, default=None, 
                        help="Units label")
    parser.add_argument("--raphael_boxes", action="store_true", default=False,
                        help="switch for plotting boxes showing the ZW3 index [default: False]")
    
    # Contour plot
    parser.add_argument("--contour_var", type=str, default=None,
                        help="Variable for the contour plot [default: None]")
    parser.add_argument("--contour_files", type=str, nargs='*', default=None,
                        help="Files for the contour plot [default: None]")
    parser.add_argument("--contour_ticks", type=float, nargs='*', default=None,
                        help="Ticks/levels for the contour plot [default: auto]")
    
    # Stippling			
    parser.add_argument("--stippling", action="store_true", default=False,
                        help="switch for plotting significance stippling [default: False]")


    args = parser.parse_args() 
    main(args)
