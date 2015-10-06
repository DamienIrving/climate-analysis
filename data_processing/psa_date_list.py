# Import general Python modules

import os, sys, pdb
import argparse
import numpy, pandas
import xray
import operator
from itertools import groupby
from scipy import stats
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
 
season_months = {'DJF': (12, 1, 2), 'MAM': (3, 4, 5), 
                 'JJA': (6, 7, 8), 'SON': (9, 10, 11)}

def fix_boundary_data(data, freq):
    """If a data series straddles 0/60, adjust accordingly."""

    assert freq == 6, "At the moment fix_boundary_data() is hard-wired to a freq of 6"

    data = numpy.array(data)
    if len(data) > 1: 
	diffs = numpy.abs(numpy.diff(data))
	if diffs.max() > 50:
            data = numpy.where(data < 30, data + 60, data)

    return data


def set_phase_bounds(user_bounds, freq):
    """Make sure phase remains within the associated bounds."""

    phase_min, phase_max = user_bounds
    max_value = 360. / freq
    if phase_min > max_value:
        phase_min = phase_min - max_value

    if phase_max > max_value:
        phase_max = phase_max - max_value

    assert phase_min < max_value
    assert phase_max < max_value

    return phase_min, phase_max


def event_info(df, freq):
    """Add columns to the DataFrame that contain event information."""

    df['dates'] = df.index
    df['time_delta'] = df['dates'].diff()
    df['in_event'] = df['time_delta'] < pandas.tslib.Timedelta('2 days')

    # Event number
    event_number = -1
    event_list = []
    for index, row in df.iterrows():
        if not row['in_event']:
            event_number = event_number + 1
        event_list.append(event_number)
    df['event_number'] = event_list

    # Event duration and gradient
    duration_list = []
    gradient_list = []
    phase_list = []
    target_freq = 'wave%i_phase' %(freq)
    for event in range(0, event_number + 1):
        event_duration = event_list.count(event)
        event_phase_data = fix_boundary_data(df[target_freq].loc[df['event_number'] == event].values, freq)
        event_gradient, intercept, r_value, p_value, std_err = stats.linregress(numpy.arange(0, event_duration), event_phase_data)
        
        duration_list = duration_list + [event_duration] * event_duration
        phase_list = phase_list + list(event_phase_data)
        gradient_list = gradient_list + [event_gradient] * event_duration

    df['event_duration'] = duration_list
    df['event_phase'] = phase_list
    df['event_gradient'] = gradient_list

    # Flag start and end data times
    start_bool = [False] * len(df.index)
    end_bool = [False] * len(df.index)
    row_num = 0
    for index, row in df.iterrows():
        if row['in_event'] == False:
            start_bool[row_num] = True
            end_bool[row_num + row['event_duration'] - 1] = True
        row_num = row_num + 1    

    df['event_start'] = start_bool
    df['event_end'] = end_bool

    return df
  

def main(inargs):
    """Run the program"""

    # Read data
    dset_in = xray.open_dataset(inargs.fourier_file)
    df = dset_in.to_dataframe()

    # Change the amplitue columns so the value is a ranking
    amp_df = df.loc[:, df.columns.map(lambda x: 'amp' in x)]
    rank_df = amp_df.apply(rankdata, axis=1)
    rank_df = rank_df.combine_first(df)

    # Select the ones where wave 5 and 6 are in the top 3 amplitudes
    # (worst ranking must be 8 + 9 = 17) 
    included = (rank_df['wave5_amp'].values + rank_df['wave6_amp'].values) >= 17
    final = rank_df.loc[included]

    # Reject days that change sign too much
    if inargs.max_sign_change:
        final = final.loc[final['sign_count'] <= inargs.max_sign_change]

    final = event_info(final, inargs.freq)

    if inargs.full_stats:
        assert not inargs.phase_filter and not inargs.season_filter and not inargs.duration_filter, \
        "Cannot filter by phase, season or duration for full stats, because then they would not be full!"
        final.to_csv(inargs.output_file)

    else: 
        # Optional filtering by duration
        if inargs.duration_filter:
            final = final.loc[final['event_duration'] > inargs.duration_filter]

        # Optional filtering by season
        if inargs.season_filter:
            season = inargs.season_filter
            months_subset = pandas.to_datetime(final.index.values).month
            bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
            final = final.loc[bools_subset]

        # Optional filtering by wave phase
        if inargs.phase_filter:
            phase_min, phase_max = set_phase_bounds(inargs.phase_filter, inargs.freq)
            target_phase = 'wave%i_phase' %(inargs.freq)
            min_bools = (final[target_phase] > phase_min).values
            max_bools = (final[target_phase] < phase_max).values
            if phase_min < phase_max:
                final = final.loc[numpy.logical_and(min_bools, max_bools)]
            else:
                final = final.loc[numpy.logical_or(min_bools, max_bools)]

        # Write date file
        gio.write_dates(inargs.output_file, final.index.values)

    metadata_dict = {inargs.fourier_file: dset_in.attrs['history']}
    gio.write_metadata(inargs.output_file, file_info=metadata_dict)


if __name__ == '__main__':

    description='Create a psa date list (or stats csv) from Fourier information'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fourier_file", type=str, help="Input file name")
    parser.add_argument("output_file", type=str, help="Output file name")

    parser.add_argument("--max_sign_change", type=int, default=None, 
                        help="maximum number of times the signal can change sign over the search domain [default = None; i.e. not applied]")
    parser.add_argument("--freq", type=int, default=6, 
                        help="frequency used for phase filtering and event gradient calculation [default = 6]")

    parser.add_argument("--full_stats", action="store_true", default=False,
                        help="switch for outputting a full stats file instead of just dates [default: False]")

    parser.add_argument("--duration_filter", type=int, default=None, 
                        help="minimum duration for a PSA event [default = no filter]")
    parser.add_argument("--season_filter", type=str, choices=('DJF', 'MAM', 'JJA', 'SON'), default=None, 
                        help="only keep the selected season [default = no season filter]")
    parser.add_argument("--phase_filter", type=float, nargs=2, metavar=['MIN_PHASE', 'MAX_PHASE'], default=None, 
                        help="phase range to retain at the given frequecy. [default = no filter]")

    args = parser.parse_args()            
    main(args)
