# Import general Python modules

import os, sys, pdb
import argparse
from dateutil import rrule, parser
import pandas

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

def main(inargs):
    """Run the program"""

    dates_df = pandas.read_csv(inargs.infile, header=1)

    all_dates = []
    for index, row in dates_df[['Start YYYY-MM-DD', 'End YYYY-MM-DD']].iterrows():
        start, end = row
        dates = list(rrule.rrule(rrule.DAILY,
                     dtstart=parser.parse(start),
                     until=parser.parse(end)))

        date_list = map(lambda x: x.strftime('%Y-%m-%d'), dates)
        all_dates.extend(date_list)

    gio.write_dates(inargs.outfile, all_dates)
    gio.write_metadata(inargs.outfile)


if __name__ == '__main__':

    description='Create a date list for a given CMMT date file'
    argparser = argparse.ArgumentParser(description=description, 
                                        argument_default=argparse.SUPPRESS,
                                        formatter_class=argparse.RawDescriptionHelpFormatter)

    argparser.add_argument("infile", type=str, help="Input file name")
    argparser.add_argument("outfile", type=str, help="Output file name")
    
    args = argparser.parse_args()            
    main(args)
