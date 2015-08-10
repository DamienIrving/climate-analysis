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
    df = dset_in.to_dataframe()

    # Select the amplitude columns
    amp_df = df.loc[:, df.columns.map(lambda x: 'amp' in x)]

    # Rank the amplitude columns
    arank = amp_df.apply(numpy.argsort, axis=1)

    # Select the ones where wave 5 and 6 are in the top 3 amplitudes
    wave5_top3 = arank['wave5_amp'] <= 2
    wave6_top3 = arank['wave6_amp'] <= 2
    top3 = wave5_top3.tolist() and wave6_top3.tolist()
    # df.iloc[top3]

    # Generate duration information


    pdb.set_trace()


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

    args = parser.parse_args()            
    main(args)
