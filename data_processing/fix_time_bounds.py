"""
Filename:     fix_time_bounds.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Remove the time bounds inserted by CDO (iris doesn't like them)

"""

# Import general Python modules

import sys, os, pdb
import argparse
import xray


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


# Define functions and classes

def main(inargs):
    """Run the program."""

    dset = xray.open_dataset(inargs.infile)

    try:
        dset = dset.drop('bnds')
    except ValueError:
        print "Did not delete time bounds variable"

    try:
        dset.coords['time'].attrs.pop('bounds')
    except KeyError:
        pass

    gio.set_global_atts(dset, dset.attrs, {inargs.infile: dset.attrs['history'],})
    dset.to_netcdf(inargs.outfile)


if __name__ == '__main__':

    description="""Remove the time bounds inserted by CDO (iris doesn't like them)"""
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("outfile", type=str, help="Output file name")
                
    args = parser.parse_args()            

    main(args)
