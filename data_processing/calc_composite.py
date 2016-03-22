"""
Filename:     calc_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculates a composite

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy, pandas
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

season_months = {'annual': None, 'DJF': (12, 1, 2), 'MAM': (3, 4, 5), 'JJA': (6, 7, 8), 'SON': (9, 10, 11)}

def get_datetimes(darray, date_file):
    """Generate a list of datetimes common to darray and date_file."""

    try:
        time_values = darray['time'].values
    except KeyError:
        time_values = darray.index.values 

    if date_file:
        time_dim = map(str, time_values)     
        date_list, date_metadata = gio.read_dates(date_file)
    
        match_dates, miss_dates = uconv.match_dates(date_list, time_dim)
        match_dates = map(numpy.datetime64, match_dates)

    else:
        match_dates = time_values
        date_metadata = None

    return match_dates, date_metadata


def calc_composites(darray, dtlist, sig_test=True):
    """Calculate the composites and define their attributes."""

    standard_name = darray.attrs['standard_name']
    darray_selection = darray.sel(time=dtlist)

    composite_means = {}
    pvals = {}
    composite_mean_atts = {}
    pval_atts = {}    
    for season, months in season_months.iteritems():
        if season == 'annual':
            composite_means['annual'] = darray_selection.mean(dim='time').values
            
            if sig_test:
                pvals['annual'], pval_atts['annual'] = uconv.calc_significance(darray_selection.values, 
                                                                               darray.values, 'p_value_'+season)
        else: 
            months_subset = pandas.to_datetime(darray_selection['time'].values).month
            bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
            data_subset = darray_selection.loc[bools_subset]
            composite_means[season] = data_subset.mean(dim='time').values

            if sig_test:
                months_all = pandas.to_datetime(darray['time'].values).month
                bools_all = (months_all == season_months[season][0]) + (months_all == season_months[season][1]) + (months_all == season_months[season][2])
                data_all = darray.loc[bools_all]
                pvals[season], pval_atts[season] = uconv.calc_significance(data_subset.values, 
                                                                           data_all.values, 'p_value_'+season)

        composite_mean_atts[season] = {'standard_name': standard_name+'_'+season,
                                       'long_name': standard_name+'_'+season,
                                       'units': darray.attrs['units'],
                                       'notes': 'Composite mean for %s season' %(season)}

    return composite_means, composite_mean_atts, pvals, pval_atts


def main(inargs):
    """Run the program."""

    # Read the data
    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.var)

    subset_dict = gio.get_subset_kwargs(inargs)
    darray = dset_in[inargs.var].sel(**subset_dict)

    assert darray.dims == ('time', 'latitude', 'longitude'), \
    "Order of the data must be time, latitude, longitude"

    # Generate datetime list
    dt_list, dt_list_metadata = get_datetimes(darray, inargs.date_file)

    # Calculate the composites
    if not inargs.date_file:
        inargs.no_sig = True    
    cmeans, cmean_atts, pvals, pval_atts = calc_composites(darray, dt_list, sig_test=not inargs.no_sig) 

    # Write the output file
    d = {}
    d['latitude'] = darray['latitude']
    d['longitude'] = darray['longitude']

    for season in season_months.keys(): 
        d[inargs.var+'_'+season] = (['latitude', 'longitude'], cmeans[season])
        if not inargs.no_sig:
            d['p_'+season] = (['latitude', 'longitude'], pvals[season])

    dset_out = xray.Dataset(d)

    for season in season_months.keys(): 
        dset_out[inargs.var+'_'+season].attrs = cmean_atts[season]
        if not inargs.no_sig:
            dset_out['p_'+season].attrs = pval_atts[season]
    
    output_metadata = {inargs.infile: dset_in.attrs['history'],}
    if inargs.date_file:
        output_metadata[inargs.date_file] = dt_list_metadata

    gio.set_global_atts(dset_out, dset_in.attrs, output_metadata)
    dset_out.to_netcdf(inargs.outfile, format='NETCDF3_CLASSIC')


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
