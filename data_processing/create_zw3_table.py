"""
Filename:     create_zw3_table.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Takes all the ZW3 climatology results and puts
              them in a single table

"""

# Import general Python modules #

import sys, os, pdb
import argparse
import numpy, pandas
import netCDF4

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
    import general_io as gio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

def get_time_axis(time_variable):
    """Get the time axis using the netCDF4 module"""

    units = time_variable.units
    calendar = time_variable.calendar
    time_axis = netCDF4.num2date(time_variable, units=units, calendar=calendar)        
    
    return time_axis


def find_nearest(array, value):
    """Find the closest array item to value"""
    
    idx = (numpy.abs(array - value)).argmin()
    return array[idx]


def get_fourier(infile, lat_requested):
    """Extract Fourier coefficient data and output to a pandas DataFrame"""
    
    fin = netCDF4.Dataset(infile)
   
    # Variable list
    var_list = fin.variables.keys()
    var_list = map(str, var_list)
    
    # Time axis
    time_axis = get_time_axis(fin.variables['time'])

    # Latitude axis
    lat_axis = fin.variables['latitude'][:]
    lat_index = (numpy.abs(lat_axis - lat_requested)).argmin()
    lat_selected = lat_axis[lat_index]
    if lat_selected != lat_requested:
        print "Selecting the closest latitude to %s, which is %s" %(str(lat_requested), str(lat_selected))

    # Output DataFrame
    output = pandas.DataFrame(index=map(lambda x: x.strftime("%Y-%m-%d"), time_axis))
    for var in var_list:
        if not var[0:3].lower() in ['lat', 'lon', 'tim']:
	    output[var] = fin.variables[var][:, lat_index]

    return output


def get_zw3(infile):
    """Extract ZW3 index and output to a pandas DataFrame"""

    fin = netCDF4.Dataset(infile)
    time_axis = get_time_axis(fin.variables['time'])

    data = fin.variables['zw3'][:]

    output = pandas.DataFrame(data, index=map(lambda x: x.strftime("%Y-%m-%d"), time_axis), columns=['ZW3_index'])

    return output
    
    
def get_env(infile, normalised=False):
    """Extract wave envelope stats and output to pandas DataFrame"""

    fin = netCDF4.Dataset(infile)
    time_axis = get_time_axis(fin.variables['time'])

    data = numpy.zeros((len(time_axis), 4))
    tag = 'nenv' if normalised else 'env'
    headers = [] 
    for i, var in enumerate(['amp_mean', 'extent', 'start_lon', 'end_lon']):
        data[:, i] = fin.variables[var][:]
        headers.append(tag+'_'+var)

    output = pandas.DataFrame(data, index=map(lambda x: x.strftime("%Y-%m-%d"), time_axis), columns=headers)

    return output


def main(inargs):
    """Run the program."""

    # Read data and check inputs #
    
    fourier_DataFrame = get_fourier(inargs.fourier_file, inargs.latitude)
    zw3_DataFrame = get_zw3(inargs.zw3_file)
    env_DataFrame = get_env(inargs.env_file, normalised=False)
    nenv_DataFrame = get_env(inargs.nenv_file, normalised=True)
    
    output = fourier_DataFrame.join([zw3_DataFrame, env_DataFrame, nenv_DataFrame])
    metadata = gio.get_timestamp()
    output.to_csv(inargs.outfile)  # At the moment you can't write metadata headers with to_csv, hence metadata hasn't been used


if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.3.0/bin/cdat create_zw3_table.py 

author:
  Damien Irving, d.irving@student.unimelb.edu.au

note:
  Written to use netCDF4 instead of cdms2 because pandas can't be 
  installed alongside UV-CDAT on vortex

"""

    description='Take all the ZW3 climatology results and put them in a big table'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("env_file", type=str, help="Input wave envelope stats file")
    parser.add_argument("nenv_file", type=str, help="Input normalised wave envelope stats file")
    parser.add_argument("zw3_file", type=str, help="Input ZW3 index (Raphael, 2004) file")
    parser.add_argument("fourier_file", type=str, help="Input Fourier coefficients file")
    
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--latitude", type=float, default=-55,
                        help="Latitude to select from the fourier file")                    

    
    args = parser.parse_args()             
    
    main(args)    
