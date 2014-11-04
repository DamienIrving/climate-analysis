"""
Filename:     plot_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots composite maps

"""

# Import general Python modules #

import os, sys, re, pdb
import argparse

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

def switch_to_p(var_list):
    """Change variable names so they starts with p instead (e.g. tas_DJF becomes p_DJF)"""
    
    output = []
    for var in var_list:
        name, season = var.split('_')
        output.append(var+'_'+season)

    return output
    

def extract_data(infile, variable_list, p=False):
    """Return lists of the data and corresponding composite sample sizes:
    [size included, size excluded]

    If p is true it changes the variable names to get the p values instead.
    
    """

    if p:
        variable_list = switch_to_p(variable_list)    
        
    data_list = []
    sample_list = []
    for var in variable_list:
        temp_data = nio.InputData(infile, var)
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
    
    metadata = temp_data.global_atts['history']

    return data_list, sample_list, metadata
    

def main(inargs):
    """Run the program"""

    if inargs.contour_vars:
        assert len(inargs.variables) == len(inargs.contour_vars)
    if inargs.stippling:
        assert len(inargs.variables) == len(inargs.stippling)
        
    indata_list, temp, indata_metadata = extract_data(inargs.infile, inargs.variables)
    stipple_list, sample_list, temp = extract_data(inargs.infile, inargs.variables)
    stipple_list = stipple_list if inargs.stippling else None

    output_metadata = {inargs.infile: indata_metadata}

    if inargs.contour_file:
        contour_list, temp, contour_metadata = extract_data(inargs.contour_file, inargs.contour_vars)
        output_metadata[inargs.contour_file] = contour_metadata
    else:
        contour_list = None
	
    if inargs.dimensions:
        dimensions = inargs.dimensions
    else:
        dimensions = pm.get_dimensions(len(indata_list))

    if inargs.raphael_boxes:
        box1 = ('zw31', 'blue', 'solid')
	box2 = ('zw32', 'blue', 'solid')
	box3 = ('zw33', 'blue', 'solid')
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
                 stipple_data=stipple_list, stipple_threshold=0.05, stipple_size=1.0, stipple_thin=5,
		 ticks=inargs.ticks, discrete_segments=inargs.segments, colourbar_colour=inargs.palette,
                 projection=inargs.projection, 
                 extend=inargs.extend,
		 box=box_list,
                 image_size=inargs.image_size,
                 file_info=output_metadata)


if __name__ == '__main__':

    extra_info="""
example (abyss.earthsci.unimelb.edu.au):
    cdat plot_composite.py
    tas-infile.nc 
    tas_annual tas_DJF tas_MAM tas_JJA tas_SON
    --headings annual DJF MAM JJA SON
    --ticks -3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0
    --units temperature_anomaly 
    --contour_file zg-infile.nc
    --contour_vars zg_annual zg_DJF zg_MAM zg_JJA zg_SON
    --contour_ticks -30 -25 -20 -15 -10 -5 0 5 10 15 20 25 30
    --projection spstere

"""
  
    description='Plot composite.'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, 
                        help="composite file to plot (assumed to have come from calc_composite.py)")
    parser.add_argument("variables", type=str, nargs='+',
                        help="name of variables from infile to plot")
    
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
    parser.add_argument("--contour_file", type=str, default=None,
                        help="File for the contour plot (assumed to have come from calc_composite.py) [default: None]")
    parser.add_argument("--contour_vars", type=str, nargs='*', default=None,
                        help="name of variables from contour_file to plot [default: None]")
    parser.add_argument("--contour_ticks", type=float, nargs='*', default=None,
                        help="Ticks/levels for the contour plot [default: auto]")
    
    # Stippling			
    parser.add_argument("--stippling", action="store_true", default=False,
                        help="switch for plotting significance stippling [default: False]")


    args = parser.parse_args() 
    main(args)
