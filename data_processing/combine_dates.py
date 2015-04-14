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



def stat_writer(fout, len_primary, len_intersect, len_secondary, season):
    """Write stats for a given season."""

    primary_statement = 'Total primary %s dates = %i \n' %(season, len_primary) 
    intersect_statement = 'Total intersection %s dates = %i \n' %(season, len_intersect) 
    secondary_statement = 'Total secondary %s dates = %i \n' %(season, len_secondary) 

    
    intersect_primary_ratio = (len_intersect / float(len_primary)) * 100
    intersect_primary_statement = 'Intersect to primary ratio = %f percent \n' %(intersect_primary_ratio) 

    fout.write(primary_statement)
    fout.write(secondary_statement)
    fout.write(intersect_statement)
    fout.write(intersect_primary_statement)


def main(inargs):
    """Run the program."""

    # Read input
    metadata_dict = {}
    primary_date_list, metadata_dict[inargs.primary_infile] = gio.read_dates(inargs.primary_infile)
    secondary_date_list, metadata_dict[inargs.secondary_infile] = gio.read_dates(inargs.secondary_infile)

    # Find the common dates
    common_date_list = list(set(primary_date_list).intersection(secondary_date_list))
    common_date_list.sort()

    # Write some stats to a .dat file
    season_dict = {'DJF': ['12', '01', '02'],
                    'MAM': ['03', '04', '05'],
                    'JJA': ['06', '07', '08'],
                    'SON': ['09', '10', '11']}

    fname, extension = inargs.outfile.split('.')
    output_data_file = open(fname+'.dat', 'w')

    stat_writer(output_data_file, len(primary_date_list), len(common_date_list), len(secondary_date_list), 'annual')
    for season, month_list in season_dict.iteritems():
        season_filtered_primary_date_list = [date for date in primary_date_list if date.split('-')[1] in month_list]
        season_filtered_common_date_list = [date for date in common_date_list if date.split('-')[1] in month_list]
        season_filtered_secondary_date_list = [date for date in secondary_date_list if date.split('-')[1] in month_list]

        stat_writer(output_data_file, len(season_filtered_primary_date_list), 
                    len(season_filtered_common_date_list), 
                    len(season_filtered_secondary_date_list), season)

    output_data_file.close()

    # Write output date file
    gio.write_dates(inargs.outfile, common_date_list)
    gio.write_metadata(ofile=inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Combine two lists of dates into a single list of common dates'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("primary_infile", type=str, help="Name of the primary input file")
    parser.add_argument("secondary_infile", type=str, help="Name of the secondary input file")
    parser.add_argument("outfile", type=str, help="Output file name")


    args = parser.parse_args()            

    print 'Primary input file: ', args.primary_infile
    print 'Secondary input file: ', args.secondary_infile
    print 'Output file: ', args.outfile  

    main(args)
