#!/usr/bin/env cdat

############
# Need to figure out what biased and centred means.
# I'm pretty sure genutil statistics can make decisions
# on the shape of input data with me having to write all
# the if statements.
#############



"""
SVN INFO: $Id$
Filename:     calc_stat.py
Author:       Damien Irving
Description:  Calculates a number of commonly used statistics
              in climate science

Input:        List of two files to compare
Output:       File containing the statistic of interest


Updates | By | Description
--------+----+------------
30 Jan 2013 | Damien Irving | Initial version.


"""

import sys
import os

import argparse

import numpy
import genutil

module_dir = os.path.join(os.environ['HOME'],'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio


def temporal_axis_check(data1, data2):
    """Check whether the input data are on the same axis"""
    
    assert len(data1.getTime()) > 1.0
    assert len(data1.getTime()) == len(data2.getTime())    

    data1_hasspatial = 'yx' in data1.getOrder()
    data2_hasspatial = 'yx' in data2.getOrder()

    if data1_hasspatial and data2_hasspatial:
        assert len(data1.getLatitude()) == len(data2.getLatitude())
        assert len(data1.getLongitude()) == len(data2.getLongitude())

    return data1_hasspatial, data2_hasspatial


def temporal_corr(data1, data2):
    """Temporal correlation.
    
    Comparison can be between data of order:
    * tyx vs. tyx
    * tyx vs. t
    * t vs. tyx

    """
    
    data1_hasspat, data2_hasspat = temporal_axis_check(data1, data2)

    primary_data, secondary_data = (data2, data1) if (data2_hasspat \
                                   and not data1_hasspat) else (data1, data2)

    if (data1_hasspat + data2_hasspat) >= 1:
        output_axes = (primary_data.getLatitude(),
                       primary_data.getLongitude(),)
	tempcorr = genutil.statistics.correlation(primary_data, secondary_data, centered=1, biased=1)
    else:       
        print genutil.statistics.correlation(primary_data, 
              secondary_data, centered=1, biased=1)
        sys.exit(0)

    attributes = {'id': 'tempcorr',
                  'long_name': 'temporal correlation',
                  'units': '',
                  'missing_value': 1e20, 
                  'notes': 'genutil.statistics.correlation(centered=1, biased=1)'
                 }
                  
    return tempcorr, output_axes, attributes
    

def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata1 = nio.InputData(inargs.infile1, inargs.variable1, 
                            **nio.dict_filter(vars(inargs), ['time', 'agg', 'region']))
    indata2 = nio.InputData(inargs.infile2, inargs.variable2, 
                            **nio.dict_filter(vars(inargs), ['time', 'agg', 'region']))

    # Calulcate the statistic #

    function_for_metric = {'tempcorr': temporal_corr}
    
    calc_stat = function_for_metric[inargs.stat]
    stat, axes, atts = calc_stat(indata1.data, indata2.data)

    # Write the output file #
 
    indata_list = (indata1, indata2,)
    outdata_list = (stat,)
    outvar_atts_list = (atts,)
    outvar_axes_list = (axes,)
    
    nio.write_netcdf(inargs.outfile, inargs.stat, 
                     indata_list, outdata_list, 
                     outvar_atts_list, outvar_axes_list, 
                     clear_history=True)   


if __name__ == '__main__':
    
    description = 'Calculate statistic.'
    parser = argparse.ArgumentParser(description=description,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("stat", type=str, choices=['tempcorr'], 
                        help="statistic to calculate")
    parser.add_argument("infile1", type=str, help="name of first input file")
    parser.add_argument("variable1", type=str, help="name of first input file variable")
    parser.add_argument("infile2", type=str, help="name of second input file")
    parser.add_argument("variable2", type=str, help="name of second input file variable")
    parser.add_argument("outfile", type=str, help="output file name")

    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="region over which to calculate statistic [default = entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="time period over which to calculate the statistic [default = entire]")
    parser.add_argument("--agg", type=str,
                        help="temporal aggregation selector")

    args = parser.parse_args()     

    print 'Statistic: ', args.stat
    print 'Input file 1: ', args.infile1
    print 'Input file 2: ', args.infile2
    print 'Output file: ', args.outfile

    main(args)
