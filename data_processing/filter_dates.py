"""
Filename:     filter_dates.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  

"""

import sys
import os

import argparse
import numpy

import cdutil

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio

roim_dir = os.path.join(os.environ['HOME'], 'phd', 'data_processing', 'roim')
sys.path.insert(0, roim_dir)
from roim_stat import write_dates


def west_antarctica_filter(date_list, infile, var, threshold, select):
    """Filter according to the sign of the meridional wind anomaly
    over the region 110W to 75W and 65S to 75S. This is an approximate
    area based on the findings of Ding2013 and you'd expect there to be 
    a signal in autumn.
    """  
    
    # Read meridional wind data and extract region of interest
    indata = nio.InputData(infile, var, latitude=(-75, -65, 'cc'), longitude=(250, 285, 'cc'))
    
    # Select data corresponding to input date list
    input_selection = nio.temporal_extract(indata.data, date_list, indexes=False) 
    
    # Calculate the spatial average of the data
    ave_axes = indata.data.getOrder().translate(None, 't')  #all but the time axis
    spatial_ave = cdutil.averager(input_selection, axis=ave_axes, weights=['unweighted']*len(ave_axes))

    # Select data where mean meridional wind is less or more than threshold
    assert select in ['above', 'below']
    test = spatial_ave < threshold if select == 'below' else spatial_ave > threshold
    
    indexes = numpy.where(test, 1, 0)
    output_selection = nio.temporal_extract(spatial_ave, indexes, indexes=True)
    
    # Generate the new date list
    new_date_list = output_selection.getTime().asComponentTime()
    return map(lambda x: x.split()[0], new_date_list)


def calc_totals():
    """Calculate the total number of days for each month or season
    (expressed as a percentage of the total number of days in the month/season)
    """
    


def read_dates(infile):
    """Read a file of dates (one per line) and write to a list"""
    
    fin = open(infile, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()

    return date_list
    

def main(inargs):
    """Run program."""

    # Read dates
    date_list = read_dates(inargs.dates)

    # Perform additional filtering
    filters = {'west_antarctica': west_antarctica_filter,}
    if inargs.filter.lower() != 'none':
        filter_func = filters[inargs.filter]
        new_date_list = stat_func(inargs.dates, 
                                  inargs.data[0], inargs.data[1], 
                                  inargs.threshold, inargs.selection)
    else:
        new_date_list = inargs.dates
    
    # Return the desired output type
    if inargs.output == 'new_list':
        write_dates(inargs.outfile, new_date_list)
    else:
        calc_totals()
    



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
    parser.add_argument("filter", type=str, choices=('none', 'west_antarctica'),  
                        help="Method for filtering the list of dates (can be none)")
    parser.add_argument("output", type=str, choices=('new_list', 'monthly_totals', 'seasonal_totals'), 
                        help="Desired output")
    
    parser.add_argument("--data", type=str, nargs=2, metavar=('FILE', 'VARIABLE'),
                        help="Data to be used for the filtering method")
    parser.add_argument("--threshold", type=float, default=0.0,  
                        help="Threshold value against which the selection is made")
    parser.add_argument("--selection", type=str, choices=('above', 'below'), default='above',  
                        help="Segment of the selection to retain (i.e. above or below threshold)")   
    parser.add_argument("--outfile", type='str', default='test.txt',
                        help="Name of output file")   
                        
    args = parser.parse_args()            

    main(args)

