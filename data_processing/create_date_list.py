# Import general Python modules

import os, sys, pdb
import argparse

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

def main(inargs):
    """Run the program"""
   
    # Read data 
    indata, metadata = aconv.nc_to_df(inargs.infile, [inargs.metric])
    metric_threshold = uconv.get_threshold(indata[inargs.metric], inargs.metric_threshold) 
    
    # Apply filters
    dt_selector = aconv.pandas_dt_selector(indata.index, inargs.season, inargs.start, inargs.end)
    selector = dt_selector
    
    assert inargs.threshold_direction in ['greater', 'less']
    if inargs.threshold_direction == 'greater':
        metric_selection = indata[inargs.metric] >= metric_threshold
    elif inargs.threshold_direction == 'less':
        metric_selection = indata[inargs.metric] <= metric_threshold

    selector = selector & metric_selection 
 
    data = indata[selector]

    # Metadata
    metadata_dict = {inargs.infile: metadata}

    gio.write_dates(inargs.outfile, data.index.tolist())
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Create a date list for a given input metric'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("metric", type=str, help="Name of the input file metric to be used")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--start", type=str, help="Time start filter (e.g. 1979-02-31)", default=None)
    parser.add_argument("--end", type=str, help="Time end filter (e.g. 2012-12-31)", default=None)
    parser.add_argument("--season", type=str, choices=('DJF', 'MAM', 'JJA', 'SON'), default=None,
                        help="Season selector [default = all]")

    parser.add_argument("--metric_threshold", type=str, default='75pct', 
                        help="Threshold metric value. Can be percentile (e.g. 75pct) or raw value.")
    parser.add_argument("--threshold_direction", type=str, choices=('greater', 'less'), default='greater', 
                        help="Keep values greater or less than the threshold.")

    args = parser.parse_args()            
    main(args)
