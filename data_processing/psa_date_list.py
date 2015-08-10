# Import general Python modules

import os, sys, pdb
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

def main(inargs):
    """Run the program"""

    # Read data
    dset_in = xray.open_dataset(inargs.fourier_file)
    dframe = dset_in.to_dataframe()

    pdb.set_trace()

    subset_dict = gio.get_subset_kwargs(inargs)


    darray = dset_in[inargs.metric].sel(**subset_dict)


    # Select the amplitude columns
    amp_df = dframe.loc[:, dframe.columns.map(lambda x: 'amp' in x)]

    # Rank the amplitude columns
    arank = dframe.apply(numpy.argsort, axis=1)
    ranked_cols = dframe.columns.to_series()[arank.values[:,::-1][:,:2]]
    rank_amp_df = pandas.DataFrame(ranked_cols, index=dframe.index)


#    # Make selection
#    metric_threshold = uconv.get_threshold(darray.values, inargs.metric_threshold) 
#    
#    assert inargs.threshold_direction in ['greater', 'less']
#    if inargs.threshold_direction == 'greater':
#        indexes = darray >= metric_threshold
#    elif inargs.threshold_direction == 'less':
#        indexes = darray <= metric_threshold
#
#    darray_selection = darray.loc[indexes]
#
#    # Write outputs
#    gio.write_dates(inargs.outfile, darray_selection['time'].values)
#    metadata_dict = {inargs.infile: dset_in.attrs['history']}
#    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    description='Create a psa date list from Fourier information'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fourier_file", type=str, help="Input file name")
    parser.add_argument("output_file", type=str, help="Output file name")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to provide dates [default = entire]")

    args = parser.parse_args()            
    main(args)
