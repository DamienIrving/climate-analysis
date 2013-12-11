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



def west_antarctica_filter():
    """Filter according to the sign of the meridional wind anomaly
    over the region 110W to 75W and 65S to 75S. This is an approximate
    area based on the findings of Ding2013 and you'd expect there to be 
    a signal in autumn
    """  




def main(inargs):
    """Run program."""

    # Read dates

    fin = open(inargs.dates, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()
    
    # Perform additional filtering
    
    filters = {'west_antarctica': west_antarctica_filter,}  
    
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
