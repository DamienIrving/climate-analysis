"""
Filename: combine_dates.py
Author: Damien Irving, d.irving@student.unimelb.edu.au
Description: Combine multiple lists of dates into a single list of common dates

"""

# Import general Python modules

import sys, os
import argparse

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
vis_dir = os.path.join(repo_dir, 'visualisation')
sys.path.append(vis_dir)

try:
    import general_io as gio
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')



def main(inargs):
    """Run the program."""

    # Initialise with the first file
    metadata_dict = {}
    date_list, date_metadata = gio.read_dates(inargs.infiles[0])
    metadata_dict[inargs.infiles[0]] = date_metadata  

    # Loop through the remaining files
    for date_file in inargs.infiles[1:]:
        dates, metadata = gio.read_dates(date_file)
        date_list = list(set(date_list).intersection(dates))
        metadata_dict[date_file] = metadata

    date_list.sort()

    # Write output
    gio.write_dates(inargs.outfile, date_list)
    gio.write_metadata(ofile=inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Combine multiple lists of dates into a single list of common dates'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")

    args = parser.parse_args()            

    print 'Input files: ', args.infiles
    print 'Output file: ', args.outfile  

    main(args)
