"""
Filename:     calc_index_composite.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  For a given variable, calculate a composite of a related index

"""

# Import general Python modules #

import sys, os, pdb, operator
import argparse
import numpy
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
    import netcdf_io as nio
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

def check_time_axis(var_indata, metric_indata):
    """Check that the time axes are the same and trim to 
    the shortest if they're not.

    Assumes daily timestep data.

    """

    var_dates = var_indata.datetime_axis()
    metric_dates = metric_indata.datetime_axis()
    diff_flag = False

    if var_dates[0].strftime("%Y-%m-%d") == metric_dates[0].strftime("%Y-%m-%d"):
        new_start_date = var_dates[0].strftime("%Y-%m-%d")
    elif var_dates[0] > metric_dates[0]:
        new_start_date = var_dates[0].strftime("%Y-%m-%d")
        diff_flag = True
    else:
        new_start_date = metric_dates[0].strftime("%Y-%m-%d") 
        diff_flag = True

    if var_dates[-1].strftime("%Y-%m-%d") == metric_dates[-1].strftime("%Y-%m-%d"):
        new_end_date = var_dates[-1].strftime("%Y-%m-%d")+' 23:59:0.0'
    elif var_dates[-1] < metric_dates[-1]:
        new_end_date = var_dates[-1].strftime("%Y-%m-%d")+' 23:59:0.0'
        diff_flag = True
    else:
        new_end_date = metric_dates[-1].strftime("%Y-%m-%d")+' 23:59:0.0'
        diff_flag = True
      
    return new_start_date, new_end_date, diff_flag


def extract_data(inargs, start_date, end_date, selector):
    """Extract the data"""

    var_indata = nio.InputData(inargs.varfile, inargs.var, time=(start_date, end_date, selector),  **nio.dict_filter(vars(inargs), ['region']))

    time_index = var_indata.data.getOrder().index('t')
    assert time_index == 0, "If time is not the first axis, the numpy.resize broadcasting in this script will mess up the data"
        
    metric_indata = nio.InputData(inargs.metricfile, inargs.metric, time=(start_date, end_date, selector))

    return var_indata, metric_indata, time_index
    

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
        var_indata, metric_indata, time_index = extract_data(inargs, start_date, end_date, selector)
        new_start_date, new_end_date, diff_flag = check_time_axis(var_indata, metric_indata)
        if diff_flag:
            var_indata, metric_indata, time_index = extract_data(inargs, new_start_date, new_end_date, selector)
            assert var_indata.data.shape[0] == metric_indata.data.shape[0]

        if inargs.absolute:
            var_indata.data = MV2.absolute(var_indata.data)

        # Find threshold for variable and get boolean index array for samples > and <= the threshold #
        
        threshold = uconv.get_threshold(var_indata.data, inargs.threshold, axis=time_index)
        threshold = numpy.resize(threshold, var_indata.data.shape)

        if inargs.include == 'above':
            excluded_indexes = var_indata.data > threshold  # Because True gets masked, and I want the trues included
        else:
            excluded_indexes = var_indata.data < threshold  # Because True gets masked, and I want the trues included
        included_indexes = numpy.invert(excluded_indexes)
 
        size_included = excluded_indexes.sum(axis=0)
        size_excluded = included_indexes.sum(axis=0)
 
        # Create masked metric arrays #

        if len(var_indata.data.shape) > 1:
            dim_size = reduce(operator.mul, var_indata.data.shape[1:], 1)
            metric_data = numpy.repeat(metric_indata.data, dim_size)
            metric_data = numpy.reshape(metric_data, var_indata.data.shape)
        else:
            metric_data = metric_indata.data

        metric_data_included = numpy.ma.masked_array(metric_data, mask=included_indexes)
        metric_data_excluded = numpy.ma.masked_array(metric_data, mask=excluded_indexes)
 
	# Calculate composite # 
	
        composite_mean = metric_data_included.mean(axis=time_index)

        composite_atts = {'id': inargs.metric+'_'+season,
                          'standard_name': metric_indata.data.standard_name+'_'+season,
                          'long_name': metric_indata.data.long_name+'_'+season,
                          'units': metric_indata.data.units,
                          'history': 'Composite mean for %s season' %(season)}

        outdata_list.append(composite_mean)
	outvar_atts_list.append(composite_atts)
	outvar_axes_list.append(var_indata.data.getAxisList()[1:])  #exclude time axis

	# Perform significance test # 

        pval, pval_atts, size_incl_atts, size_excl_atts = uconv.get_significance(metric_data_included, metric_data_excluded,
                                                                                 'p_'+season, 'p_value_'+season,
                                                                                 'size_incl_'+season, 'size_excl_'+season)
        for data, atts in [(pval, pval_atts), (size_included, size_incl_atts), (size_excluded, size_excl_atts)]:
            outdata_list.append(data)
            outvar_atts_list.append(atts)
            outvar_axes_list.append(var_indata.data.getAxisList()[1:]) #exclude time axis	


    # Write the output file #

    var_insert = 'History of %s:\n' %(inargs.varfile)
    metric_insert = 'History of %s:\n' %(inargs.metricfile)
    var_indata.global_atts['history'] = '%s %s \n %s %s' %(var_insert, var_indata.global_atts['history'], 
                                                           metric_insert, metric_indata.global_atts['history'])

    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     var_indata.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (vortex.earthsci.unimelb.edu.au):

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Calculate composite'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("varfile", type=str, help="Name of input file containing variable of interest")
    parser.add_argument("var", type=str, help="Name of variable in varfile")
    parser.add_argument("metricfile", type=str, help="Name of file containing metric")
    parser.add_argument("metric", type=str, help="Name of metric in metricfile")
    parser.add_argument("threshold", type=str,help="Threshold for defining an extreme event. Can be percentile (e.g. 90pct) or raw value.")
    parser.add_argument("outfile", type=str, help="Output file name")
    

    parser.add_argument("--include", type=str, choices=('above', 'below'), default='above',
                        help="Include values above or below threshold [default: above]")
    parser.add_argument("--absolute", action="store_true", default=False,
                        help="Use the absolute value of var [default: above]")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="Time period over which to calculate the composite [default = entire]")
    parser.add_argument("--seasons", type=str, nargs='*', default=('DJF', 'MAM', 'JJA', 'SON', 'annual'),
                        help="Seasons for which to output a composite [default = DJF, MAM, JJA, SON, annual]")
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate the composite [default: entire]")

    args = parser.parse_args()            

    main(args)
