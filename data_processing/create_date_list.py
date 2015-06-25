# Import general Python modules

import os, sys, pdb
import argparse
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
    dset_in = xray.open_dataset(inargs.infile)
    gio.check_xrayDataset(dset_in, inargs.metric)

    subset_dict = gio.get_subset_kwargs(inargs)
    darray = dset_in[inargs.metric].sel(**subset_dict)

    # Make selection
    metric_threshold = uconv.get_threshold(darray.values, inargs.metric_threshold) 
    
    assert inargs.threshold_direction in ['greater', 'less']
    if inargs.threshold_direction == 'greater':
        indexes = darray >= metric_threshold
    elif inargs.threshold_direction == 'less':
        indexes = darray <= metric_threshold

    darray_selection = darray.loc[indexes]

    # Write outputs
    gio.write_dates(inargs.outfile, darray_selection['time'].values)
    metadata_dict = {inargs.infile: dset_in.attrs['history']}
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    description='Create a date list for a given input metric'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("metric", type=str, help="Name of the input file metric to be used")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to provide dates [default = entire]")

    parser.add_argument("--metric_threshold", type=str, default='75pct', 
                        help="Threshold metric value. Can be percentile (e.g. 75pct) or raw value.")
    parser.add_argument("--threshold_direction", type=str, choices=('greater', 'less'), default='greater', 
                        help="Keep values greater or less than the threshold.")

    args = parser.parse_args()            
    main(args)
