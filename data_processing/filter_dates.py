"""
Filename:     filter_dates.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Take a list of dates and filter according to a supplied dataset

"""

import sys
import os

import argparse
import itertools
import numpy

import cdutil

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio
import general_io as gio

import pdb


def west_antarctica_filter(date_file, data_file, var, threshold, select):
    """Filter according to the sign of the meridional wind anomaly
    over the region 110W to 75W and 65S to 75S. This is an approximate
    area based on the findings of Ding2013 and you'd expect there to be 
    a signal in autumn.
    """  
       
    # Read meridional wind data and extract region of interest
    indata = nio.InputData(data_file, var, latitude=(-75, -65, 'cc'), longitude=(250, 285, 'cc'))
    
    # Select data corresponding to input date list
    date_list = gio.read_dates(date_file)
    matching_date_list = nio.match_dates(date_list, indata.data.getTime().asComponentTime())
    input_selection = nio.temporal_extract(indata.data, matching_date_list, indexes=False) 
    
    # Calculate the spatial average of the data
    ave_axes = indata.data.getOrder().translate(None, 't')  #all but the time axis
    spatial_ave = cdutil.averager(input_selection, axis=ave_axes, weights=['unweighted']*len(ave_axes))

    # Select data where mean meridional wind is less or more than threshold
    assert select in ['above', 'below']
    test = spatial_ave < threshold if select == 'below' else spatial_ave > threshold
    
    new_date_list = list(itertools.compress(matching_date_list, test))
    
    return map(lambda x: str(x).split()[0], new_date_list)


def main(inargs):
    """Run program."""

    # Read dates
    date_list = gio.read_dates(inargs.dates)

    # Perform additional filtering
    filters = {'west_antarctica': west_antarctica_filter,}

    filter_func = filters[inargs.filter]
    new_date_list = filter_func(inargs.dates, 
                                inargs.infile, inargs.var, 
                                inargs.threshold, inargs.selection)
    
    # Write output file
    gio.write_dates(inargs.outfile, new_date_list)


if __name__ == '__main__':

    extra_info =""" 
example:
  /usr/local/uvcdat/1.3.0/bin/cdat filter_dates.py 
  hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates.txt 
  west_antarctica 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/va_Merra_250hPa_daily_native.nc va 
  0 below

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Take a list of dates and filter according to a supplied dataset'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("dates", type=str, 
                        help="File containing dates of interest (one date per line)")
    parser.add_argument("filter", type=str, choices=('west_antarctica',),  
                        help="Method for filtering the list of dates (can be none)")
    parser.add_argument("infile", type=str,
                        help="File containing data to be used for the filtering method")
    parser.add_argument("var", type=str,
                        help="Variable to extract from file")
    parser.add_argument("threshold", type=float,  
                        help="Threshold value against which the selection is made")
    parser.add_argument("selection", type=str, choices=('above', 'below'),  
                        help="Segment of the selection to retain (i.e. above or below threshold)")   

    parser.add_argument("--outfile", type=str, default='test.txt',
                        help="Name of output file")   
                        
    args = parser.parse_args()            
    main(args)

