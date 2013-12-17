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

module_dir = os.path.join(os.environ['HOME'], 'phd, 'modules')
sys.path.insert(0, module_dir)
import general_io as gio
import netcdf_io as nio


def calc_composite():
    """Calculate the composite"""
    
    # Perform the t-test 
    # To perform a Welch's t-test (two independent samples, unequal variances), need the 
    # latest version of scipy in order to use the equal_var keyword argument
	
    t, p_vals = stats.ttest_ind(data_in_composite, data_out_composite, axis=0) #equal_var=False) 

    # Perform necessary averaging #

#    count = numpy.shape(composite)[0]
#        
#    final_composite = MV2.average(composite, axis=0) if average else composite
#    final_composite.count = count

    return data_in_composite, p_vals



def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.var, 
                           **nio.dict_filter(vars(inargs), ['time', 'region']))

    date_list = gio.read_dates(inargs.dates)

    # Filter the data #
    
    matching_dates_included = nio.match_dates(date_list, indata.data.getTime().asComponentTime())
    matching_dates_excluded = nio.match_dates(date_list, indata.data.getTime().asComponentTime(), invert=True)

    data_included = nio.temporal_extract(indata.data, matching_dates_included, indexes=False)
    data_excluded = nio.temporal_extract(indata.data, matching_dates_excluded, indexes=False)

    # Calculate the composite #
        
    composite, p_val = calc_composite(data_included, data_excluded)
	
    # Write the output file #

    composite_atts = {'id': inargs.var,
                      'long_name': indata.data.long_name,
                      'units': indata.data.units,
                      'history': '%s data that meet the composite criteria (see global atts)' %(inargs.season)}

    pval_atts = {'id': 'p',
                 'long_name': 'Two-tailed p-value',
                 'units': ' ',
                 'history': """Standard independent two sample t-test comparing the data sample that meets the composite criteria to a sample containing the remaining data""",
                 'reference': 'scipy.stats.ttest_ind(a, b, axis=t, equal_var=True)'}

    indata_list = [indata, index]
    outdata_list = [composite, p_val]
    outvar_atts_list = [composite_atts, pval_atts]
    outvar_axes_list = [composite.getAxisList(), composite.getAxisList()[1:]] 

    extras = 'Threshold method = %s. Limit = %s. Bound = %s. Index = %s, %s. Normalised = %s (mean removed = %s).'  %(inargs.method, 
    inargs.limit, inargs.bound, inargs.index_file, inargs.index_var, str(inargs.normalise), str(inargs.remove_ave))
    nio.write_netcdf(inargs.outfile, 'composite', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list,
		     extra_history=extras)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  cdat calc_composite.py 


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

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
