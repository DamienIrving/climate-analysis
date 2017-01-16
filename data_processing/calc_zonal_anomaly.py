"""
Filename:     calc_zonal_anomaly.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculate the zonal anomaly (i.e. subtract the zonal mean at each timestep)

"""

# Import general Python modules

import os, sys, pdb
import argparse
import xarray

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
    

# Define fuctions

def main(inargs):
    """Run the program."""
    
    # Read the data
    dset_in = xarray.open_dataset(inargs.infile)
    gio.check_xarrayDataset(dset_in, inargs.variable)

    subset_dict = gio.get_subset_kwargs(inargs)
    darray = dset_in[inargs.variable].sel(**subset_dict)
      
    # Calculate the zonal anomaly
    zonal_mean = darray.mean(dim='longitude')
    zonal_anomaly = darray - zonal_mean

    # Write output file
    d = {}
    for dim in darray.dims:
        d[dim] = darray[dim]
    d[inargs.variable] = (darray.dims, zonal_anomaly)

    dset_out = xarray.Dataset(d)

    dset_out[inargs.variable].attrs = {'long_name': darray.attrs['long_name'],
        'standard_name': darray.attrs['standard_name'],
        'units': darray.attrs['units'],
        'notes': 'The zonal mean has been subtracted at each time step.'}

    gio.set_global_atts(dset_out, dset_in.attrs, {inargs.infile: dset_in.attrs['history'],})
    dset_out.to_netcdf(inargs.outfile, format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    extra_info = """
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/anaconda/bin/python calc_zonal_anomaly.py 
  zg_Merra_250hPa_monthly_native.nc zg zg_Merra_250hPa_monthly-zonal-anom_native.nc
"""    	

    description = 'Calculate the zonal anomaly (i.e. subtract the zonal mean at each timestep).'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)	
