"""
Filename:     calc_composite_dummy_file.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #


def main(inargs):
    """Run the program."""
    
    # Read input data #
    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'latitude', 'longitude']))
    
    lats = indata.data.getLatitude()[:]
    lons = indata.data.getLongitude()[:]
    ntime, nlats, nlons = indata.data.shape   # the order that nio.InputData produces is tyx
    months = numpy.array(indata.months())

    # Write dummy data output #

    dummy_data = numpy.ones(indata.data.shape) * inargs.constant_value
    dummy_history = ''

    dummy_history = dummy_history + 'Latitude %s (index 0), longitude %s (index 0) = all %s \n' %(str(lats[0]), str(lons[0]), str(inargs.constant_value))
    
    dummy_history = dummy_history +  'Latitude %s (index 0), longitude %s (index 1) = all %s except Apr %s \n' %(str(lats[0]), str(lons[1]), str(inargs.constant_value), str(inargs.extreme_value))
    dummy_data[:, 0, 1] = numpy.where(months == 4, inargs.extreme_value, inargs.constant_value)

    dummy_history = dummy_history + 'Latitude %s (index 1), longitude %s (index 0) = all %s except Jul -%s \n' %(str(lats[1]), str(lons[0]), str(inargs.constant_value), str(inargs.extreme_value))
    dummy_data[:, 1, 0] = numpy.where(months == 7, -inargs.extreme_value, inargs.constant_value)

    dummy_history = dummy_history + 'Latitude %s (index 1), longitude %s (index 1) = all random \n' %(str(lats[1]), str(lons[1]))
    dummy_data[:, 1, 1] = numpy.random.rand(ntime)

    data_atts = {'id': 'dummy',
                 'standard_name': 'dummy_data',
                 'long_name': 'dummy_data',
                 'units': 'none',
                 'notes': dummy_history}

    nio.write_netcdf(inargs.outfile_data, " ".join(sys.argv), 
                     indata.global_atts, 
                     [dummy_data],
                     [data_atts], 
                     [indata.data.getAxisList()])

    # Write dummy metric output #

    dummy_metric = numpy.where(months == 4, 8.0, 1.0)

    metric_atts = {'id': 'metric',
                   'standard_name': 'dummy_metric',
                   'long_name': 'dummy_metric',
                   'units': 'none',
                   'notes': "Dummy metric 8.0 in Apr and 1.0 elsewhere"}

    nio.write_netcdf(inargs.outfile_metric, " ".join(sys.argv), 
                     indata.global_atts, 
                     [dummy_metric],
                     [metric_atts], 
                     [[indata.data.getAxisList()[0]],])


if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
    /usr/local/anaconda/bin/python create_composite_dummy_file.py 
    /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/tas_ERAInterim_surface_daily_native.nc tas 
    /mnt/meteo0/data/simmonds/dbirving/temp/dummy_data.nc 
    /mnt/meteo0/data/simmonds/dbirving/temp/dummy_metric.nc 
    --time 1991-01-01 1993-12-31 none --latitude 14 15.5 --longitude 91 92.5
"""

    description='Create a dummy netCDF file for testing code'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile_data", type=str, help="Output dummy data file name")
    parser.add_argument("outfile_metric", type=str, help="Output dummy metric file name")
            
    # Input data options
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range over which to perform Fourier Transform [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'), default=None,
                        help="Longitude range over which to perform Fourier Transform (all other values are set to zero) [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    # Dummy data options
    parser.add_argument("--constant_value", type=float, default=2.0,
                        help="Constant value that most of the dummy data takes")
    parser.add_argument("--extreme_value", type=float, default=5.0,
                        help="Extreme value that a small minority of the data takes")

  
    args = parser.parse_args()            

    main(args)
