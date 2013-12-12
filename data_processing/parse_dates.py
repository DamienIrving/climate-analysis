"""
Filename:     parse_dates.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Parse a list of dates and output a simple statistic

"""

from datetime import datetime

import argparse

filter_dir = os.path.join(os.environ['HOME'], 'phd', 'data_processing')
sys.path.insert(0, filter_dir)
from filter_dates import read_dates

def main():
    """Run the program"""

    date_list = read_dates(inargs.dates)

    month_selection = {}
    month_selection['DJF'] = (12, 1, 2)
    month_selection['MAM'] = (3, 4, 5)
    month_selection['JJA'] = (6, 7, 8)
    month_selection['SON'] = (9, 10, 11)

    dt_list = map(lambda x: datetime.strptime(x, '%Y-%m-%d'), date_list)

    # months = times_dt.map(lambda x: x.month)
    # season_selection = (months.map(lambda val: val in month_selection[season]))
    # combined_selection = combined_selection & season_selection
    
