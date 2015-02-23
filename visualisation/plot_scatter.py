"""
Filename: plot_scatter.py
Author: Damien Irving, d.irving@student.unimelb.edu.au
Description: Create a scatterplot

"""

# Import general Python modules

import os, sys, pdb

import numpy
import pandas
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


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
    import convenient_anaconda as aconv
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def normalise_series(series):
    """Normalise a Pandas data series. 

    i.e. subtract the mean and divide by the standard deviation

    """

    ave = series.mean()
    stdev = series.std()
    
    return (series - ave) / stdev

     
def scatter_plot(x_data, y_data, 
                 xlabel, ylabel,
                 outfile, 
                 c_data=None, 
                 zero_lines=False, thin=1, 
                 trend=False, cmap='jet'):
    """Create scatterplot."""

    plt.figure()

    if zero_lines:
        plt.axhline(y=0, linestyle='-', color='0.5')
        plt.axvline(x=0, linestyle='-', color='0.5')

    x = x_data[::thin]
    y = y_data[::thin]
    c = c_data[::thin] if type(c_data) == pandas.core.series.Series else 'k'
    
    plt.scatter(x, y, c=c, cmap=cmap)

    if trend:
        p = numpy.polyfit(x, y, 1)
        print p
        plt.plot(x, p[0]*x+p[1], 'r')
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.savefig(outfile, bbox_inches='tight')


def main(inargs):
    """Run program."""

    # Read input data into a single pandas DataFrame
    x_dataframe, x_metadata = aconv.nc_to_df(inargs.xfile, [inargs.xvar], lat=inargs.xlat)
    y_dataframe, y_metadata = aconv.nc_to_df(inargs.yfile, [inargs.yvar], lat=inargs.ylat)
    dataframe_list = [y_dataframe]

    metadata_dict = {}
    metadata_dict[inargs.xfile] = x_metadata
    metadata_dict[inargs.yfile] = y_metadata

    if inargs.colour:
        c_dataframe, c_metadata = aconv.nc_to_df(inargs.colour[0], [inargs.colour[1]], lat=inargs.clat)
        dataframe_list.append(c_dataframe)
        metadata_dict[inargs.colour[0]] = c_metadata
        
    dataframe = x_dataframe.join(dataframe_list)
    dataframe = dataframe.dropna()

    # Normalise data 
    if inargs.normalise:
        target_xvar = inargs.xvar+'_norm'
        target_yvar = inargs.yvar+'_norm'
        dataframe[target_xvar] = normalise_series(dataframe[inargs.xvar])
        dataframe[target_yvar] = normalise_series(dataframe[inargs.yvar])
    else:
        target_xvar = inargs.xvar
        target_yvar = inargs.yvar

    # Filter data
    if inargs.filter:
        threshold = uconv.get_threshold(dataframe[inargs.filter[0]], inargs.filter[1])
        selector = dataframe[inargs.filter[0]] >= threshold
        dataframe = dataframe[selector]

    # Generate plot
    c_data = dataframe[inargs.colour[1]] if inargs.colour else None
    xlabel = inargs.xlabel.replace('_',' ') if inargs.xlabel else inargs.xvar
    ylabel = inargs.ylabel.replace('_',' ') if inargs.ylabel else inargs.yvar

    scatter_plot(dataframe[target_xvar], dataframe[target_yvar], 
                 xlabel, ylabel,
                 inargs.ofile, 
                 c_data=c_data, 
                 zero_lines=inargs.zero_lines, thin=inargs.thin, 
                 trend=inargs.trend_line, cmap=inargs.cmap)

    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:
   /usr/local/anaconda/bin/python plot_scatter.py 
   /mnt/meteo0/data/simmonds/dbirving/Indices/tos_CPC_surface_monthly_nino34.nc NINO34 
   /mnt/meteo0/data/simmonds/dbirving/Indices/psl_Marshall_surface_monthly_SAM.nc SAM 
   test_scatter.png 
   --colour /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw3/wavestats_zw3_w19-extent75pct_env-va_ERAInterim_500hPa_030day-runmean_native-mermax-55S.nc ampmedian

author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Create a scatterplot'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required data
    parser.add_argument("xfile", type=str, help="Input file for the x-axis")
    parser.add_argument("xvar", type=str, help="Variable name in x-axis input file")
    parser.add_argument("yfile", type=str, help="Input file for the x-axis")
    parser.add_argument("yvar", type=str, help="Variable name in x-axis input file")
    parser.add_argument("ofile", type=str, help="Output file name")
    
    # Optional data
    parser.add_argument("--colour", type=str, nargs=2, metavar=('FILE', 'VAR'), default=None, 
                        help="Input file and variable for colouring the dots")
 
    # Data options
    parser.add_argument("--filter", type=str, nargs=2, metavar=('METRIC', 'THRESHOLD'), default=None, 
                        help="Remove values where metric is below threshold. Threshold can be percentile (e.g. 90pct) or raw value.")
    parser.add_argument("--normalise", action="store_true", default=False,
                        help="Switch for normalising the x and y input data [default: False]")
    parser.add_argument("--thin", type=int, default=1,
                        help="Stride for thinning the data (e.g. 3 will keep one-third of the data) [default: 1]")
    
    parser.add_argument("--xlat", type=str, nargs=3, metavar=('LAT_MIN', 'LAT_MAX', 'METHOD'), default=None, 
                        help="Collapse the latitude axis of xfile over range (LAT_MIN, LAT_MAX) using METHOD (mermax or spatave; or none if LAT_MAX == LAT_MIN)")
    parser.add_argument("--ylat", type=str, nargs=3, metavar=('LAT_MIN', 'LAT_MAX', 'METHOD'), default=None, 
                        help="Collapse the latitude axis of yfile over range (LAT_MIN, LAT_MAX) using METHOD (mermax or spatave; or none if LAT_MAX == LAT_MIN)")
    parser.add_argument("--clat", type=str, nargs=3, metavar=('LAT_MIN', 'LAT_MAX', 'METHOD'), default=None, 
                        help="Collapse the latitude axis of colour file over range (LAT_MIN, LAT_MAX) using METHOD (mermax or spatave); or none if LAT_MAX == LAT_MIN")

    # Plot options
    parser.add_argument("--trend_line", action="store_true", default=False,
                        help="Switch for a linear line of best fit [default: False]")
    parser.add_argument("--zero_lines", action="store_true", default=False,
                        help="Switch for drawing zero lines [default: False]")
    parser.add_argument("--cmap", type=str, default='jet', choices=('jet', 'jet_r', 'hot', 'hot_r', 'RdBu', 'RdBu_r'),
                        help="Colour map [default: False]")
    parser.add_argument("--xlabel", type=str, default=None,
                        help="x-axis label")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="y-axis label")


    args = parser.parse_args()            
    main(args)
