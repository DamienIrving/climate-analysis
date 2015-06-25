"""
Filename:     calc_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates a composite

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import xray


# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import general_io as gio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def get_dates(darray, date_file, invert=False):
    """Filter the data into a subset that only includes dates in date_file. 

    """

    if not date_file:
        match_dates = darray['time'].values 
        date_metadata = None
        size_inlcuded = False
        size_excluded = False
    else:
        date_list, date_metadata = gio.read_dates(date_file)

        time_dim = map(str, darray['time'].values)
        match_dates, miss_dates = uconv.match_dates(date_list, time_dim)
 
        match_dates = map(numpy.datetime64, match_dates)
        size_included = len(match_dates)
        size_excluced = len(miss_dates)

    return match_dates, date_metadata, size_included, size_excluded


def calc_composites(darray, seasonal_darray):
    """Calculate the composites and define their attributes."""

    season_months = {'annual': None, 
                     'DJF': 2, 'MAM': 5, 'JJA': 8, 'SON': 11}

    composite_means = {}
    composite_mean_atts = {}    
    for season, month in season_months.iteritems():
        if season == 'annual':
            composite_means['annual'] = darray.mean(dim='time').values
        else:
            indexes = pandas.to_datetime(seasonal_darray['time'].values).month == month
            composite_means[season] = seasonal_darray.loc[indexes].mean(dim='time').values

        composite_atts[season] = {'standard_name': darray.attrs['standard_name']+'_'+season,
                                  'long_name': darray.attrs['standard_name']+'_'+season,
                                  'units': darray.attrs['units'],
                                  'notes': 'Composite mean for %s season' %(season)}

    return composite_means, composite_mean_atts


def main(inargs):
    """Run the program."""

    # Read the data
    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.var)

    subset_dict = gio.get_subset_kwargs(inargs)
    darray = dset_in[inargs.var].sel(**subset_dict)

    # Generate datetime list
    dt_list, date_list_metadata, size_filtered, size_excluded = get_dates(darray, inargs.date_file)

    # Filter the data
    darray_filtered = darray.sel(time=dt_list)
    seasonal_darray_filtered = darray_filtered.resample('Q-FEB', dim='time', how='mean', label='right')

    # Calculate the composites
    composite_means, composite_mean_atts = calc_composites(darray_filtered, seasonal_darray_filtered) 



 #   # Initialise output
#    outdata_list = []
#    outvar_atts_list = []
#    outvar_axes_list = []
#
#    if inargs.time:
#        start_date, end_date = inargs.time
#    else:
#        start_date = end_date = 'none'
#
#    for season in inargs.seasons:
#
#	# Prepate input data
#        selector = 'none' if season == 'annual' else season
#	indata = nio.InputData(inargs.infile, inargs.var, time=(start_date, end_date, selector),  **nio.dict_filter(vars(inargs), ['region']))
#        assert indata.data.getOrder()[0] == 't', "First axis must be time"
#
#	# Filter data
#	data_filtered, date_metadata, size_filtered = filter_dates(indata.data, inargs.date_file, offset=inargs.offset, invert=inargs.invert)
#
#	# Calculate composite
#	composite, composite_atts = get_composite(data_filtered, inargs.var, 
#                                        	  indata.data.long_name, indata.data.standard_name, indata.data.units,
#                                        	  season)
#	outdata_list.append(composite)
#	outvar_atts_list.append(composite_atts)
#	outvar_axes_list.append(indata.data.getAxisList()[1:])
#
#	# Perform significance test
#	if inargs.date_file and not inargs.no_sig:
#            pval, pval_atts = uconv.get_significance(data_filtered, indata.data, 
#	                                             'p_'+season, 'p_value_'+season, 
#						     size_filtered, indata.data.shape[0])
#            outdata_list.append(pval)
#            outvar_atts_list.append(pval_atts)
#            outvar_axes_list.append(indata.data.getAxisList()[1:])	
#
#
#    # Write the output file
#    if date_metadata:
#        infile_insert = 'History of %s:\n' %(inargs.infile)
#        date_insert = 'History of %s:\n' %(inargs.date_file)
#        indata.global_atts['history'] = '%s %s \n %s %s' %(infile_insert, indata.global_atts['history'], 
#                                                           date_insert, date_metadata)
#    else:
#        indata.global_atts['history'] = indata.global_atts['history']



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

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to calculate the composite [default = entire]")
    parser.add_argument("--region", type=str, choices=gio.regions.keys(),
                        help="Region over which to calculate the composite [default: entire]")

    parser.add_argument("--no_sig", action="store_true", default=False,
                        help="do not perform the significance testing [default: False]")

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
