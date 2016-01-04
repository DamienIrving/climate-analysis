"""
Filename: plot_scatter.py
Author: Damien Irving, d.irving@student.unimelb.edu.au
Description: Create a scatterplot

"""

# Import general Python modules

import os, sys, pdb

import numpy
import pandas, xray
import argparse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import seaborn
seaborn.set_context('paper')


# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

processing_dir = os.path.join(repo_dir, 'data_processing')
sys.path.append(processing_dir)

try:
    import general_io as gio
    import convenient_universal as uconv
    import calc_composite
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
                 c_data=None, cmap='Greys', clabel=None,
                 zero_lines=False, thin=1, 
                 plot_trend=False, trend_colour='r',
                 quadrant_labels=None):
    """Create scatterplot."""

    fig = plt.figure()
    ax = plt.axes()

    if zero_lines:
        plt.axhline(y=0, linestyle='-', color='0.5')
        plt.axvline(x=0, linestyle='-', color='0.5')

    x = x_data[::thin]
    y = y_data[::thin]
    c = c_data[::thin] if type(c_data) == pandas.core.series.Series else 'k'
    
    plt.scatter(x, y, c=c, cmap=cmap)
    cbar = plt.colorbar()
    if clabel:
        cbar.set_label(clabel)
        
    if plot_trend:
        p = numpy.polyfit(x, y, 1)
        print p
        plt.plot(x, p[0]*x+p[1], trend_colour)

    if quadrant_labels:
        plt.text(0.87, 0.95, quadrant_labels[0], fontsize='small', transform=ax.transAxes)
        plt.text(0.87, 0.04, quadrant_labels[1], fontsize='small', transform=ax.transAxes)
        plt.text(0.03, 0.04, quadrant_labels[2], fontsize='small', transform=ax.transAxes)
        plt.text(0.03, 0.95, quadrant_labels[3], fontsize='small', transform=ax.transAxes)
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.savefig(outfile, bbox_inches='tight')


def read_data(infile, var, subset={}):
    """Read an input data file into a pandas dataframe."""

    dset = xray.open_dataset(infile)
    gio.check_xrayDataset(dset, var)

    subset['method'] = 'nearest'

    dataframe = dset[var].sel(**subset).to_pandas()
    metadata = dset.attrs['history']

    return dataframe, metadata


def get_quadrant_text(x_data, y_data):
    """Calculate the percetage of data points that fall in each quadrant."""

    total = len(x_data)
    top_right = (numpy.sum((x_data >= 0) & (y_data >= 0)) / float(total)) * 100
    bottom_right = (numpy.sum((x_data >= 0) & (y_data < 0)) / float(total)) * 100
    bottom_left = (numpy.sum((x_data < 0) & (y_data < 0)) / float(total)) * 100
    top_left = (numpy.sum((x_data < 0) & (y_data >= 0)) / float(total)) * 100

    result = map(round, [top_right, bottom_right, bottom_left, top_left])

    return map(int, result)


def get_quadrant_labels(values, brackets=None):
    """Create the quadrant labels and include bracketed value if needed."""

    labels = []
    for i in range(0, len(values)):
        if brackets:
            label = '%i(%i)%%' %(values[i], brackets[i])
        else:
            label = '%i%%' %(values[i])
        labels.append(label)

    return labels


def main(inargs):
    """Run program."""

    # Read the data
    metadata_dict = {}
    x_dataframe, metadata_dict[inargs.xfile] = read_data(inargs.xfile, inargs.xvar) 
    y_dataframe, metadata_dict[inargs.yfile] = read_data(inargs.yfile, inargs.yvar) 

    dataframe_list = [x_dataframe, y_dataframe]
    headers = [inargs.xvar, inargs.yvar]

    if inargs.colour:
        subset = {'latitude': inargs.clat} if inargs.clat else {}
        c_dataframe, metadata_dict[inargs.colour[0]] = read_data(inargs.colour[0], inargs.colour[1], subset=subset)
        dataframe_list.append(c_dataframe)
        headers.append(inargs.colour[1])
    
    dataframe = pandas.concat(dataframe_list, join='inner', axis=1)
    dataframe.columns = headers
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

    # Get the quadrant info
    if inargs.quadrant_text:
        quadrant_pct = get_quadrant_text(dataframe[target_xvar], dataframe[target_yvar])
    else:
        quadrant_pct = None

    # Filter data
    filtered = False
    if inargs.threshold_filter:
        threshold = uconv.get_threshold(dataframe[inargs.threshold_filter[0]], inargs.threshold_filter[1])
        selector = dataframe[inargs.threshold_filter[0]] >= threshold
        dataframe = dataframe[selector]
        filtered = True

    if inargs.date_filter:
        dt_list, metadata_dict[inargs.date_filter] = calc_composite.get_datetimes(dataframe, inargs.date_filter)
        dataframe = dataframe[dataframe.index.isin(dt_list)]
        filtered = True

    # Get the quadrant labels
    if filtered and inargs.quadrant_text:
        filtered_quadrant_pct = get_quadrant_text(dataframe[target_xvar], dataframe[target_yvar])
        quadrant_labels = get_quadrant_labels(filtered_quadrant_pct, brackets=quadrant_pct)
    elif inargs.quadrant_text:
        quadrant_labels = get_quadrant_lables(quadrant_pct)
    else:
        quadrant_labels = None

    # Generate plot
    c_data = dataframe[inargs.colour[1]] if inargs.colour else None
    xlabel = uconv.fix_label(inargs.xlabel) if inargs.xlabel else inargs.xvar
    ylabel = uconv.fix_label(inargs.ylabel) if inargs.ylabel else inargs.yvar
    clabel = uconv.fix_label(inargs.clabel) if inargs.clabel else None

    scatter_plot(dataframe[target_xvar], dataframe[target_yvar], 
                 xlabel, ylabel,
                 inargs.ofile, 
                 c_data=c_data, cmap=inargs.cmap, clabel=clabel, 
                 zero_lines=inargs.zero_lines, thin=inargs.thin, 
                 plot_trend=inargs.trend_line, trend_colour=inargs.trend_colour,
                 quadrant_labels=quadrant_labels)

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
    parser.add_argument("--clat", type=float, default=None, 
                        help="Latitude to select from colour file")

    # Data options
    parser.add_argument("--threshold_filter", type=str, nargs=2, metavar=('METRIC', 'THRESHOLD'), default=None, 
                        help="Remove values where metric is below threshold. Threshold can be percentile (e.g. 90pct) or raw value.")
    parser.add_argument("--date_filter", type=str, default=None, 
                        help="Name of date file containing the list of dates to be included [default = None]")
    parser.add_argument("--normalise", action="store_true", default=False,
                        help="Switch for normalising the x and y input data [default: False]")
    parser.add_argument("--thin", type=int, default=1,
                        help="Stride for thinning the data (e.g. 3 will keep one-third of the data) [default: 1]")

    # Plot options
    parser.add_argument("--trend_line", action="store_true", default=False,
                        help="Switch for a linear line of best fit [default: False]")
    parser.add_argument("--quadrant_text", action="store_true", default=False,
                        help="Show the percentage values in each quadrant [default: False]")
    parser.add_argument("--trend_colour", type=str, default='r',
                        help="Colour of linear line of best fit [default: red]")
    parser.add_argument("--zero_lines", action="store_true", default=False,
                        help="Switch for drawing zero lines [default: False]")
    parser.add_argument("--cmap", type=str, default='Greys',
                        help="Colour map [default: False]")
    parser.add_argument("--xlabel", type=str, default=None,
                        help="x-axis label")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="y-axis label")
    parser.add_argument("--clabel", type=str, default=None,
                        help="colourbar label")


    args = parser.parse_args()            
    main(args)
