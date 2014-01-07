"""
Filename:     calc_trend.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Performs linear regression

Updates | By | Description
--------+----+------------
7 January 2014 | Damien Irving | Initial version.

"""

import sys
import os
import argparse

import genutil

module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.var, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'agg']))
    
    try:
        season = inargs.agg[1]
    except AttributeError:
        season = 'annual'
    
    slope, slope_error, pt1, pt2, pf1, pf2 = genutil.statistics.linearregression(indata.data, axis='t', nointercept=1, error=3, probability=1)

    slope_atts = {'id': inargs.var,
                  'long_name': 'Trend in %s' %(inargs.var),
                  'units': 'K',  #'%s per year' %(indata.data.units),
                  'history': 'Slope from genutil.statistics.linearregression for %s season ' %(season)}

#    pval_atts = {'id': 'p',
#                 'long_name': 'Two-tailed p-value',
#                 'units': ' ',
#                 'history': """Standard independent two sample t-test comparing the data sample that meets the composite criteria to a sample containing the remaining data""",
#                 'reference': 'scipy.stats.ttest_ind(a, b, axis=t, equal_var=False)'}

    outdata_list = [slope,] #p_val]
    outvar_atts_list = [slope_atts,] #pval_atts]
    outvar_axes_list = [slope.getAxisList(),] #composite.getAxisList()] 

    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     indata.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.3.0/bin/cdat calc_trend.py 
  /work/dbirving/datasets/HadISST/data/tos_HadISST_surface_monthly_native.nc tos
  test.nc
  --agg raw MAM 

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Perform linear regression'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("var", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate the composite [default: entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to calculate the composite [default = entire]")
    parser.add_argument("--agg", type=str, nargs=2,
                        help="Aggregation details (e.g. raw DJF)")			

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
