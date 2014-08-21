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
import cdms2

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
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

def get_fourier(infile):
    """Extract Fourier coefficient data and output to a pandas DataFrame"""
    
    fin = cdms2.open(infile)
    var_list = fin.listvariables()
    time_axis = fin.getAxis('time').asComponentTime()
    fin.close()
    
    output = pandas.DataFrame(index=map(gio.standard_datetime, time_index))
    
    for var in var_list:
        indata = nio.InputData(infile, var)
	output[var] = indata.data

    return output


def get_zw3(infile):
    """Extract ZW3 index and output to a pandas DataFrame"""

    indata = nio.InputData(infile, 'zw3')
    time_axis = indata.data.getTime().asComponentTime()
    
    output = pandas.DataFrame(indata.data, index=map(gio.standard_datetime, time_index))

    return output
    
    
def get_env(infile, normalised=False):
    """Extract wave envelope stats and output to pandas DataFrame"""
    
    df = pandas.read_csv(infile, header=1, index_col=0)
    tag = 'nenv' if normalised else 'env' 
    df.rename(columns=lambda x: tag+'_'+x, inplace=True)
    df.rename(index=lambda x: gio.standard_datetime(x), inplace=True)
    
    return df


def main(inargs):
    """Run the program."""

    # Read data and check inputs #
    
    fourier_DataFrame = get_fourier(inargs.fourier_file)
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

    
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  
    
    main(args)    
