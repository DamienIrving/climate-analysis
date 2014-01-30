"""
Filename:     calc_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates a composite

Updates | By | Description
--------+----+------------
18 March 2013 | Damien Irving | Initial version.

"""

import sys
import os
import argparse

import datetime
from dateutil.relativedelta import relativedelta

import MV2
from scipy import stats

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import general_io as gio
import netcdf_io as nio


def calc_composite(data_included, data_excluded):
    """Calculate the composite"""
    
    # Perform the t-test 
    # To perform a Welch's t-test (two independent samples, unequal variances), need the 
    # latest version of scipy in order to use the equal_var keyword argument
	
    t, p_vals = stats.ttest_ind(data_included, data_excluded, axis=0, equal_var=False) 

    # Perform necessary averaging #

    composite_mean = MV2.average(data_included, axis=0)


    return composite_mean, p_vals


def date_offset(date_list, offset):
    """Offset a list of dates by the specified number of days"""
    
    dt_list = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), date_list)

    if offset > 0:
        edited_dt_list = map(lambda x: x + relativedelta(days=offset), dt_list)
    else:
        edited_dt_list = map(lambda x: x - relativedelta(days=abs(offset)), dt_list)
	
    edited_date_list = map(lambda x: x.strftime('%Y-%m-%d'), edited_dt_list)

    return edited_date_list


def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.var, 
                           **nio.dict_filter(vars(inargs), ['time', 'region']))

    date_list = gio.read_dates(inargs.date_file)
    if inargs.offset:
        date_list = date_offset(date_list, inargs.offset)

    # Filter the data #
    
    matching_dates = nio.match_dates(date_list, indata.data.getTime().asComponentTime())
    missing_dates = nio.match_dates(date_list, indata.data.getTime().asComponentTime(), invert_matching=True)

    data_included = nio.temporal_extract(indata.data, matching_dates, indexes=False)
    data_excluded = nio.temporal_extract(indata.data, missing_dates, indexes=False)

    # Calculate the composite #
        
    composite, p_val = calc_composite(data_included, data_excluded)
	
    # Write the output file #

    try:
        selector = inargs.time[2]
	season = selector if selector.lower() != 'none' else 'annual'
    except AttributeError or IndexError:
        season = 'annual'

    composite_atts = {'id': inargs.var,
                      'long_name': indata.data.long_name,
                      'units': indata.data.units,
                      'history': 'Composite mean for %s season' %(season)}

    pval_atts = {'id': 'p',
                 'long_name': 'Two-tailed p-value',
                 'units': ' ',
                 'history': """Standard independent two sample t-test comparing the data sample that meets the composite criteria to a sample containing the remaining data""",
                 'reference': 'scipy.stats.ttest_ind(a, b, axis=t, equal_var=False)'}

    outdata_list = [composite, p_val]
    outvar_atts_list = [composite_atts, pval_atts]
    outvar_axes_list = [composite.getAxisList(), composite.getAxisList()] 

    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     indata.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  cdat calc_composite.py /usr/local/uvcdat/1.3.0/bin/cdat calc_composite.py 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/tas_Merra_surface_daily-anom-wrt-1979-2012_native.nc tas 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/stats/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va.txt 
  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/stats/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-1979-2012_y181x360_np20-260_absolute14_lon225-335_dates_filter-west-antartica-northerly-va_composite-annual.nc 
  --time 1979-01-01 2012-12-31 none

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Calculate composite'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("var", type=str, help="Input file variable")
    parser.add_argument("date_file", type=str, help="List of dates to be included in composite")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate the composite [default: entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period over which to calculate the composite [default = entire]")
    parser.add_argument("--offset", type=int, default=None,
                        help="Number of days to offset the input dates by (from date_file) [default = None]")

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
