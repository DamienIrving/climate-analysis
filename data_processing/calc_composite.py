"""
Filename:     calc_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates a composite

"""

# Import general Python modules #

import sys, os, pdb
import argparse
import numpy

import datetime
from dateutil.relativedelta import relativedelta

import MV2


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
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

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
        data_excluded = numpy.array([])
        date_metadata = None
    else:
        date_list, date_metadata = gio.read_dates(date_file)
        if offset:
            date_list = date_offset(date_list, offset)
    
        matching_dates = nio.match_dates(date_list, data.getTime().asComponentTime())
        missing_dates = nio.match_dates(date_list, data.getTime().asComponentTime(), invert_matching=True)

        data_included = nio.temporal_extract(data, matching_dates, indexes=False)
        data_excluded = nio.temporal_extract(data, missing_dates, indexes=False)

    return data_included, data_excluded, date_metadata, matching_dates, missing_dates


def get_composite(data, var, long_name, standard_name, units, season):
    """Calculate the composite and it's attributes (using the desired var, long_name
    units and season"""

    composite_mean = MV2.average(data, axis=0)

    composite_atts = {'id': var,
                      'standard_name': standard_name,
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
        
        selector = 'none' if season == 'annual' else season
	indata = nio.InputData(inargs.infile, inargs.var, time=(start_date, end_date, selector),  **nio.dict_filter(vars(inargs), ['region']))

	# Filter data #

	data_included, data_excluded, date_metadata, matching_dates, missing_dates = filter_dates(indata.data, inargs.date_file, inargs.offset)

	# Calculate composite # 

	composite, composite_atts = get_composite(data_included, inargs.var, 
                                        	  indata.data.long_name, indata.data.standard_name, indata.data.units,
                                        	  season)
	outdata_list.append(composite)
	outvar_atts_list.append(composite_atts)
	outvar_axes_list.append(composite.getAxisList())

	# Perform significance test # 

	if data_excluded.any():
            pval, pval_atts = uconv.get_significance(data_included, data_excluded)
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
example (vortex.earthsci.unimelb.edu.au):
  /usr/local/anaconda/bin/python calc_composite.py 
  /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/tas_ERAInterim_surface_030day-runmean_native.nc tas 
  /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw3/figures/composites/test.nc 
  --date_file /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw3/figures/composites/env_amp_median-date-list_zw3-w19-va-stats-extent75pct-filter90pct_ERAInterim_500hPa_030day-runmean_native-mermax.txt 
  --region small --time 1980-01-01 1982-01-01

fixme:
  The time selector is broken (it fails once it gets to SON)

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
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--date_file", type=str, default=None, 
                        help="File containing dates to be included in composite")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period over which to calculate the composite [default = entire]")
    parser.add_argument("--seasons", type=str, nargs='*', default=('DJF', 'MAM', 'JJA', 'SON', 'annual'),
                        help="Seasons for which to output a composite [default = DJF, MAM, JJA, SON, annual]")
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate the composite [default: entire]")

    parser.add_argument("--offset", type=int, default=None,
                        help="Number of days to offset the input dates by (from date_file) [default = None]")

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
