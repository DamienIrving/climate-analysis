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

def get_significance(data_included, data_excluded):
    """Calculate the composite.
    
    The approach for the significance test is to compare the mean of the included
    data sample with that of the excluded data sample via an independent, two-sample,
    parametric t-test (for details, see Wilks textbook). 
    
    http://stackoverflow.com/questions/21494141/how-do-i-do-a-f-test-in-python

    FIXME: If equal_var=False then it will perform a Welch's t-test, which is for samples
    with unequal variance (early versions of scipy don't have this option). To test whether
    the variances are equal or not you use an F-test (i.e. do the test at each grid point and
    then assign equal_var accordingly). If your data is close to normally distributed you can 
    use the Barlett test (scipy.stats.bartlett), otherwise the Levene test (scipy.stats.levene).
    
    FIXME: I need to account for autocorrelation in the data by calculating an effective
    sample size (see Wilkes, p 147). I can get the autocorrelation using either
    genutil.autocorrelation or the acf function in the statsmodels time series analysis
    python library, however I can't see how to alter the sample size in stats.ttest_ind.

    FIXME: I also need to consider whether a parametric t-test is appropriate. One of my samples
    might be very non-normally distributed, which means a non-parametric test might be better. 
    
    """

#    alpha = 0.05 
#    w, p_value = scipy.stats.levene(data_included, data_excluded)
#    if p_value > alpha:
#        equal_var = False# Reject the null hypothesis that Var(X) == Var(Y)
#    else:
#        equal_var = True

    t, pvals = stats.ttest_ind(data_included, data_excluded, axis=0, equal_var=True) 
    print 'WARNING: Significance test did not account for autocorrelation (and is thus overconfident) and assumed equal variances'

    pval_atts = {'id': 'p',
                 'long_name': 'Two-tailed p-value',
                 'units': ' ',
                 'history': """Standard independent two sample t-test comparing the data sample that meets the composite criteria (size=%s) to a sample containing the remaining data (size=%s)""" %(len(matching_dates), len(missing_dates)),
                 'reference': 'scipy.stats.ttest_ind(a, b, axis=t, equal_var=False)'}

    return pvals, pval_atts


def date_offset(date_list, offset):
    """Offset a list of dates by the specified number of days"""
    
    dt_list = map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'), date_list)

    if offset > 0:
        edited_dt_list = map(lambda x: x + relativedelta(days=offset), dt_list)
    else:
        edited_dt_list = map(lambda x: x - relativedelta(days=abs(offset)), dt_list)
	
    edited_date_list = map(lambda x: x.strftime('%Y-%m-%d'), edited_dt_list)

    return edited_date_list


def filter_dates(data, date_file, offset):
    """Filter the data into an included (in date_file) and excluded subset. An
    offset can be applied to the dates in date_file"""

    if not date_file:
        data_included = data
        data_excluded = None
        date_metadata = None
    else:
        date_list, date_metadata = gio.read_dates(date_file)
        if offset:
            date_list = date_offset(date_list, offset)
    
        matching_dates = nio.match_dates(date_list, data.getTime().asComponentTime())
        missing_dates = nio.match_dates(date_list, data.getTime().asComponentTime(), invert_matching=True)

        data_included = nio.temporal_extract(data, matching_dates, indexes=False)
        data_excluded = nio.temporal_extract(data, missing_dates, indexes=False)

    return data_included, data_excluded, date_metadata


def get_composite(data, var, long_name, units, season):
    """Calculate the composite and it's attributes (using the desired var, long_name
    units and season"""

    composite_mean = MV2.average(data, axis=0)

    composite_atts = {'id': var,
                      'long_name': long_name,
                      'units': units,
                      'history': 'Composite mean for %s season' %(season)}

    return composite_mean, composite_atts


def main(inargs):
    """Run the program."""
    
    # Initialise output #

    outdata_list = []
    outvar_atts_list = []
    outvar_axes_list = []

    if inargs.time:
        start_date, end_date = inargs.time
    else:
        start_date = end_date = 'none'

    for season in inargs.seasons:

	# Prepate input data #

	indata = nio.InputData(inargs.infile, inargs.var, time=(start_date, end_date, season))

	# Filter data #

	data_included, data_excluded, date_metadata = filter_dates(indata.data, inargs.date_file, inargs.offset)

	# Calculate composite # 

	composite, composite_atts = get_composite(data_included, inargs.var, 
                                        	  indata.data.long_name, indata.data.units,
                                        	  season)
	outdata_list.append(composite)
	outvar_atts_list.append(composite_atts)
	outvar_axes_list.append(composite.getAxisList())

	# Perform significance test # 

	if data_excluded:
            pval, pval_atts = get_significance(data_included, data_excluded)
            outdata_list.append(pval)
            outvar_atts_list.append(pval_atts)
            outvar_axes_list.append(composite.getAxisList())	


    # Write the output file #
 
    if date_metadata:
        indata.global_atts['history'] = '%s \n%s' %(date_metadata, indata.global_atts['history'])
    else:
        indata.global_atts['history'] = indata.global_atts['history']

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
    parser.add_argument("date_file", type=str, help="File containing dates to be included in composite")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period over which to calculate the composite [default = entire]")
    parser.add_argument("--seasons", type=str, nargs='*', default=('DJF', 'MAM', 'JJA', 'SON', 'annual'),
                        help="Seasons for which to output a composite [default = DJF, MAM, JJA, SON, annual]")

    parser.add_argument("--offset", type=int, default=None,
                        help="Number of days to offset the input dates by (from date_file) [default = None]")

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
