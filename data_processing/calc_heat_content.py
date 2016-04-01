"""
Filename:     calc_heat_content.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate heat content

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import xray
from scipy import integrate

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def extract_data(dset, inargs):
    """Extract the data from the input file."""

    subset_dict = gio.get_subset_kwargs(inargs)
    darray = dset[inargs.var].sel(**subset_dict)

    assert darray.dims[1] == 'lev', \
    'Script is setup to integrate vertically, with level as second coordinate (e.g. time, lev, lat, lon)'

    return darray


def main(inargs):
    """Run the program."""
    
    # Read the data
    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.var)
    darray = extract_data(dset_in, inargs)

    # Integrate vertically
    t_int = integrate.simps(darray.values, x=darray['lev'].values, axis=1)
    
    # Multiply by density and heat capacity
    # Multiple by the area of the grid cells (wondering if Iris grid areas will work?)

    #import iris.analysis.cartography
    #cube.coord('grid_latitude').guess_bounds()
    #cube.coord('grid_longitude').guess_bounds()
    #grid_areas = iris.analysis.cartography.area_weights(cube)

        
    # Write the output file
#    d = {}
#    for dim in dims:
#        d[dim] = darray[dim]

#    for outvar in outdata_dict.keys(): 
#        d[outvar] = (dims, outdata_dict[outvar][0])

#    dset_out = xray.Dataset(d)

#    for outvar in outdata_dict.keys(): 
#        dset_out[outvar].attrs = outdata_dict[outvar][1]

#    gio.set_global_atts(dset_out, dset_in.attrs, {inargs.infile: dset_in.attrs['history'],})
#    dset_out.to_netcdf(inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:

references:
    
"""

    description='Calculate ocean heat content'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("var", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
