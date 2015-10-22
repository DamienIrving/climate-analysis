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
    inargs.subset.insert(0, None)

    # Read the data
    x_dataframe, metadata_dict[inargs.xfile] = read_data(inargs.xfile, inargs.xvar) 
    y_dataframe, metadata_dict[inargs.yfile] = read_data(inargs.yfile, inargs.yvar) 

    dataframe_list = [x_dataframe, y_dataframe]
    headers = [inargs.xvar, inargs.yvar]

    dataframe = pandas.concat(dataframe_list, join='inner', axis=1)
    dataframe.columns = headers
    dataframe = dataframe.dropna()

    # Read the data
#    dset_x = xray.open_dataset(inargs.xfile)
#    dset_y = xray.open_dataset(inargs.yfile)
#    gio.check_xrayDataset(dset_x, inargs.xvar)
#    gio.check_xrayDataset(dset_y, inargs.yvar)

#    subset_dict = gio.get_subset_kwargs(inargs)
#    darray_x = dset_x[inargs.xvar].sel(**subset_dict)
#    darray_y = dset_y[inargs.yvar].sel(**subset_dict)

    colors = ['black', 'red', 'blue']
    for index, subset_file in enumerate(inargs.subset):
        dt_list, metadata = calc_composite.get_datetimes(dataframe, subset_file)
        if subset_file:
            metadata_dict[subset_file] = metadata
        dataframe_selection = dataframe[dataframe.index.isin(dt_list)]
        
        #dt_list, metadata = calc_composite.get_datetimes(darray_x, subset_file)
        #if subset_file:
        #    metadata_dict[subset_file] = metadata
        #darray_x_selection = darray_x.sel(time=dt_list)
        #darray_y_selection = darray_y.sel(time=dt_list)

        g = seaborn.jointplot(x=inargs.xvar, y=inargs.yvar, data=dataframe_selection.iloc[::10, :], color=colors[index])
 
        plt.savefig(inargs.ofile, bbox_inches='tight')
 
    gio.write_metadata(inargs.ofile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:
   /usr/local/anaconda/bin/python plot_scatter.py 
   /mnt/meteo0/data/simmonds/dbirving/Indices/tos_CPC_surface_monthly_nino34.nc NINO34 
   /mnt/meteo0/data/simmonds/dbirving/Indices/psl_Marshall_surface_monthly_SAM.nc SAM 
   test_scatter.png 

author:
    Damien Irving, d.irving@student.unimelb.edu.au

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
    parser.add_argument("--subset", type=str, action='append', default=[],
                        help="Date file for subset") 

    # Plot options
    parser.add_argument("--xlabel", type=str, default=None,
                        help="x-axis label")
    parser.add_argument("--ylabel", type=str, default=None,
                        help="y-axis label")


    args = parser.parse_args()            
    main(args)
