"""
Filename:     calc_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates a composite

"""

# Import general Python modules #

import sys
import os
import argparse

import datetime
from dateutil.relativedelta import relativedelta

import MV2
from scipy import stats

import pdb

# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

def calc_composite(data_included, data_excluded):
    """Calculate the composite.
    
    The approach for the significance test is to compare the mean of the included
    data sample with that of the excluded data sample via an independent, two-sample,
    parametric t-test (for details, see Wilks textbook). 
    
    FIXME: If equal_var=False then it will perform a Welch's t-test, which is for samples
    with unequal variance (early versions of scipy don't have this option). To test whether
    the variances are equal or not you use an F-test (i.e. do the test at each grid point and
    then assign equal_var accordingly). If your data is close to normally distributed you can 
    use the Barlett test (scipy.stats.bartlett), otherwise the Levene test (scipy.stats.levene).
    
    FIXME: I need to account for autocorrelation in the data by calculating an effective
    sample size (see Wilkes, p 147). I can get the autocorrelation using either
    genutil.autocorrelation or the acf function in the statsmodels time series analysis
    python library, however I can't see how to alter the sample size in stats.ttest_ind. 
    
    """
    
    t, p_vals = stats.ttest_ind(data_included, data_excluded, axis=0, equal_var=True) 
    print 'WARNING: Significance test did not account for autocorrelation (and is thus overconfident) and assumed equal variances'

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

    date_list, date_metadata = gio.read_dates(inargs.date_file)
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
                 'history': """Standard independent two sample t-test comparing the data sample that meets the composite criteria (size=%s) to a sample containing the remaining data (size=%s)""" %(len(matching_dates), len(missing_dates)),
                 'reference': 'scipy.stats.ttest_ind(a, b, axis=t, equal_var=False)'}

    outdata_list = [composite, p_val]
    outvar_atts_list = [composite_atts, pval_atts]
    outvar_axes_list = [composite.getAxisList(), composite.getAxisList()] 
    indata.global_atts['history'] = '%s \n %s' %(date_metadata, indata.global_atts['history'])

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
