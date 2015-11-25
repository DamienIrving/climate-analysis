"""
Filename: plot_scathist.py
Author: Damien Irving, irving.damien@gmail.com
Description: Create a bivariate scatterplot with univariate histograms

"""

# Import general Python modules

import os, sys, pdb

import numpy, pandas
import xray
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

def read_data(infile, var, subset={}):
    """Read an input data file into a pandas dataframe."""

    dset = xray.open_dataset(infile)
    gio.check_xrayDataset(dset, var)

    subset['method'] = 'nearest'

    dataframe = dset[var].sel(**subset).to_pandas()
    metadata = dset.attrs['history']

    return dataframe, metadata


def main(inargs):
    """Run program."""

    metadata_dict = {}

    x_dataframe, metadata_dict[inargs.xfile] = read_data(inargs.xfile, inargs.xvar) 
    y_dataframe, metadata_dict[inargs.yfile] = read_data(inargs.yfile, inargs.yvar) 

    dataframe_list = [x_dataframe, y_dataframe]
    headers = [inargs.xvar, inargs.yvar]

    dataframe = pandas.concat(dataframe_list, join='inner', axis=1)
    dataframe.columns = headers
    dataframe = dataframe.dropna()
    dataframe = dataframe.iloc[::7, :]

    colors = ['black', 'red', 'blue']
    g = seaborn.JointGrid(x=inargs.xvar, y=inargs.yvar, data=dataframe)
    for index, subset_file in enumerate(inargs.subset):
        print subset_file
        if subset_file == 'all':
            subset_file = None
        dt_list, metadata = calc_composite.get_datetimes(dataframe, subset_file)
        if subset_file:
            metadata_dict[subset_file] = metadata
        dataframe_selection = dataframe[dataframe.index.isin(dt_list)]

        g.x = dataframe_selection[inargs.xvar].values
        g.y = dataframe_selection[inargs.yvar].values

        g = g.plot_joint(plt.scatter, color=colors[index])  #, alpha=0.5)
	if inargs.ylabel:
            plt.ylabel(inargs.ylabel.replace('_',' '))

        if inargs.xlabel:
            plt.xlabel(inargs.xlabel.replace('_',' '))
	
        g = g.plot_marginals(seaborn.distplot, kde=True, color=colors[index])

    dpi = inargs.dpi if inargs.dpi else plt.savefig.func_globals['rcParams']['figure.dpi']
    plt.savefig(inargs.ofile, bbox_inches='tight', dpi=dpi)
    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:
    python plot_scathist.py sam_data.nc sam nino34_data.nc nino34 outfile.png 
    --subset all --subset dates_phase8-18.txt --subset dates_phase39-49.txt

author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Create a bivariate scatterplot with univariate histograms'
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
    parser.add_argument("--subset", type=str, action='append',
                        help="Date file for subset") 

    # Plot options
    parser.add_argument("--xlabel", type=str, default=None,
                        help="x-axis label")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="y-axis label")
    parser.add_argument("--dpi", type=float, default=None,
                        help="Figure resolution in dots per square inch [default=auto]")

    args = parser.parse_args()            
    main(args)
