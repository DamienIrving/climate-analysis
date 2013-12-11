"""
Filename:     filter_dates.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  

"""

import sys
import os

import argparse
import numpy
import re

import cdms2

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio




def main(inargs):
    """Run program."""

    # Read dates

    fin = open(inargs.dates, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()
    
    # Perform additional filtering
    
    filters = {'amundsen': amundsen_filter,}  
    
    filter_func = filters[inargs.statistic]
    new_date_list = stat_func(, )




if __name__ == '__main__':

    extra_info =""" 
example:

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Description'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("dates", type=str, help="File containing dates of interest (one date per line)")
    parser.add_argument("filter_method", type=str, choices=('none', 'amundsen'),  
                        help="Method for filtering the list of dates (can be none)")
    parser.add_argument("output_type", type=str, choices=('new_list', 'monthly_totals', 'seasonal_totals'), 
                        help="Desired output")
    parser.add_argument(
