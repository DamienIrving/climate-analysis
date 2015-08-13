# Import general Python modules

import os, sys, pdb
import argparse
import numpy, pandas
import xray
import operator
from itertools import groupby
from scipy.stats import rankdata


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

#
#def add_duration(DataFrame, metric, metric_threshold):
#    """Add a duration column to the input DataFrame. 
#
#    An event is defined by the number of consecutive timesteps greater than 
#    the metric_threshold.
#    
#    Note that every timestep is assigned a duration value equal to the number of
#    days in the entire event.
#    
#    """
#
#    events = DataFrame[metric].map(lambda x: x > metric_threshold)
#    event_list = events.tolist()
#    grouped_events = [(k, sum(1 for i in g)) for k,g in groupby(event_list)]
#
#    duration = []
#    for event in grouped_events:
#        if event[0]:
#            data = [event[1]] * event[1]
#        else:
#            data = [0] * event[1]
#        duration.append(data)
#
#    DataFrame['duration'] = reduce(operator.add, duration)
#    DataFrame['event'] = events
#
#    return DataFrame  


season_months = {'DJF': (12, 1, 2), 'MAM': (3, 4, 5), 
                 'JJA': (6, 7, 8), 'SON': (9, 10, 11)}

def main(inargs):
    """Run the program"""

    # Read data
    dset_in = xray.open_dataset(inargs.fourier_file)
    df = dset_in.to_dataframe()

    # Select the amplitude columns
    amp_df = df.loc[:, df.columns.map(lambda x: 'amp' in x)]

    # Rank the amplitude columns
    arank = amp_df.apply(rankdata, axis=1)

    # Select the ones where wave 5 and 6 are in the top 3 amplitudes
    # (worst ranking must be 8 + 9 = 17) 
    top3 = (arank['wave5_amp'].values + arank['wave6_amp'].values) >= 17
    # df.iloc[top3]
    #arank.loc[(arank['wave5_amp'] >= 8) & (arank['wave6_amp'] >= 8)]

    # Generate duration information
    grouped_events = [(k, sum(1 for i in g)) for k,g in groupby(top3)]  
    #could replace top3 with a magnitude criteria  e.g. events = DataFrame[metric].map(lambda x: x > metric_threshold)

    duration = []
    for event in grouped_events:
        if event[0]:
            data = [event[1]] * event[1]
        else:
            data = [0] * event[1]
        duration.append(data)

    arank['duration'] = reduce(operator.add, duration)

    # Select all days where duration > 5 data times
    final = arank.loc[arank['duration'] > 10]

    # Optional filtering by season
    if inargs.season_filter:
        season = inargs.season_filter
        months_subset = pandas.to_datetime(final.index.values).month
        bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
        final = final.loc[bools_subset]

    # Optional filtering by wave number
    if inargs.freq_filter:
        target_amp = 'wave%i_amp' %(inargs.freq_filter)
        final = final.loc[final[target_amp] == 10]

    # Optional filtering by wave phase
    if inargs.phase_filter:
        assert inargs.freq_filter, "Must give a freq_filter to use phase filter"
        phase_min, phase_max = inargs.phase_filter
        target_phase = 'wave%i_phase' %(inargs.freq_filter)
        final = final.loc[(final[target_phase] > phase_min) & (final[target_phase] < phase_max)]

    # Write outputs
    gio.write_dates(inargs.output_file, final.index.values)
    metadata_dict = {inargs.fourier_file: dset_in.attrs['history']}
    gio.write_metadata(inargs.output_file, file_info=metadata_dict)


if __name__ == '__main__':

    description='Create a psa date list from Fourier information'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fourier_file", type=str, help="Input file name")
    parser.add_argument("output_file", type=str, help="Output file name")

    parser.add_argument("--season_filter", type=str, choices=('DJF', 'MAM', 'JJA', 'SON'), default=None, 
                        help="only keep the selected season [default = no season filter]")
    parser.add_argument("--freq_filter", type=int, default=None, 
                        help="only keep times where freq_filter is most dominant [default = no filter]")
    parser.add_argument("--phase_filter", type=float, nargs=2, metavar=['MIN', 'MAX'], default=None, 
                        help="phase range to retain [default = all]")


    args = parser.parse_args()            
    main(args)
