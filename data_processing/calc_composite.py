"""
Filename:     eof_anal.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Performs and Empiricial Orthogonal Function (EOF) analysis
Reference:    Uses eof2 package: https://github.com/ajdawson/eof2

Updates | By | Description
--------+----+------------
23 October 2012 | Damien Irving | Initial version.
10 December 2012 | Damien Irving | Switched over to eof2 package

"""

import sys
import os

import argparse

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.var, 
                           **nio.dict_filter(vars(inargs), ['time', 'region']))
    index  = nio.InputData(inargs.index_file, inargs.index_var, 
                           **nio.dict_filter(vars(inargs), ['time', 'region']))

    # Calculate the composites

    if inargs.bound == 'between':
        assert len(inargs.limit) == 2, \
        """If the bound is 'between', two limits (LOWER, UPPER) must be supplied"""
        limit = (inargs.limit[0], inargs.limit[1])
    else:
        limit = inargs.limit[0]

    seasons = ['ann', 'djf', 'mam', 'jja', 'son']
    composites = {}
    outdata_list = []
    outvar_atts_list = []
    for season in seasons:
        composite = indata.temporal_composite(index.data, average=True, season=season, limit=limit, 
                                              bound=inargs.bound, method=inargs.method,
					      normalise=inargs.normalise, remove_ave=inargs.remove_ave)
					      
        outdata_list.append(composite)
            
        attributes = {'id': inargs.var+'_'+season,
                      'long_name': indata.data.long_name,
                      'units': indata.data.units,
                      'count': composite.count,
                      'history': 'Composite mean field for %s (included %s fields)'   %(season, composite.count)}
        outvar_atts_list.append(attributes)    

    
    # Write output file #

    indata_list = [indata, index]
    outvar_axes_list = [(indata.data.getLatitude(),
                        indata.data.getLongitude(),),] * 5 

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
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_composite.py 
  /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native.nc ts 
  /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF_monthly-1979-2011_native-sh.nc pc2 
  /work/dbirving/processed/composites/data/ts-sf_Merra_surface-250hPa_monthly-anom-wrt-1981-2010-pc2_native_composite-1979-2011.nc 
  --time 1979-01-01 2011-12-31 --method std --limit -1.0 --bound lower

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
    parser.add_argument("index_file", type=str, help="Input index file name")
    parser.add_argument("index_var", type=str, help="Input index file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
			
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate the composite [default: entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to calculate the composite [default: entire]")

    parser.add_argument("--method", type=str, choices=[None, 'std',], default=None,
                        help="Method for determining the composite threshold [default: None]")
    parser.add_argument("--limit", type=float, nargs='*', default=1.0,
                        help="Value applied to that method (e.g. 1.0 standard deviations)")
    parser.add_argument("--bound", type=str, choices=['upper', 'lower', 'between'], default = 'upper',
                        help="Indicates what type of bound the limit is [default: upper]")

    parser.add_argument("--normalise", action='store_true', default=False,
                        help="normalise the data before calculating the composite [default: False]")
    parser.add_argument("--remove_ave", action='store_true', default=False,
                        help="remove average in the normalisation procedure [default: False]")

    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
