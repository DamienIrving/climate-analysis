"""
Filename:     calc_drift_coefficients.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the polynomial coefficents that characterise model drift 

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import xarray
import dask.array as da


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

def polyfit(data):
    
    if data[0] == missing_value:
        return numpy.array([missing_value]*4)[:, None, None]
    else:    
        return numpy.polyfit(time_axis, data.squeeze(), 3)[:, None, None] 


def main(inargs):
    """Run the program."""
    
    # Read the data
    dset = xarray.open_mfdataset(inargs.infiles, decode_cf=False)
    
    global time_axis
    time_axis = dset.time.values
    ntimes = len(time_axis)
    
    global missing_value
    missing_value = dset[inargs.var].missing_value

    # Chunk
    dset_rechunked = dset.chunk({'time': ntimes, 'lev' : 1, 'lat' : 1, 'lon' : 1})
    darray = dset_rechunked[inargs.var].data
    
    # Calculate coefficients for cubic polynomial
    coefficients = darray.map_blocks(polyfit, chunks=(4,1,1,1))

    # Write the output file
    dims = dset[inargs.var].dims[1:]
    d = {}
    for dim in dims:
        d[dim] = dset[dim]

    d['a'] = (dims, coefficients[0, ...])
    d['b'] = (dims, coefficients[1, ...])
    d['c'] = (dims, coefficients[2, ...])
    d['d'] = (dims, coefficients[3, ...])

    dset_out = xarray.Dataset(d)

    for outvar in ['a', 'b', 'c', 'd']: 
        dset_out[outvar].attrs['long_name'] = outvar
        dset_out[outvar].attrs['standard_name'] = outvar
        dset_out[outvar].attrs['units'] = ' '
        dset_out[outvar].encoding['_FillValue'] = missing_value

    dset.attrs['polynomial'] = 'ax^3 + bx^2 + cx + d'
    gio.set_global_atts(dset_out, dset.attrs, {inargs.infiles[-1]: dset.attrs['history'],})

    dset_out.to_netcdf(inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    
"""

    description='Calculate the polynomial coefficents that characterise model drift'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("var", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")


    args = parser.parse_args()
    main(args)

