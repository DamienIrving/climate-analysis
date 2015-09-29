# Import general Python modules

import os, sys, pdb
import argparse
import numpy, pandas
import xray
import operator
from itertools import groupby
from scipy import stats
from scipy.stats import rankdata

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

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

def fix_boundary_data(data):
    """If a data series straddles 0/60, adjust accordingly."""

    data = numpy.array(data) 
    diffs = numpy.abs(numpy.diff(data))
    if diffs.max() > 50:
        data = numpy.where(data < 30, data + 60, data)

    return data
        

def plot_phase(df, min_duration, ofile):
    """Plot a line graph showing phase throughout PSA event lifecycle."""

    # Collect up all the event phase info
    event_phase_list = []
    event_amp_list = []
    current_event_phase = []
    current_event_amp = []
    for index, row in df.iterrows():
        if row['duration'] == 0:
            event_phase_list.append(current_event_phase)
            event_amp_list.append(current_event_amp)
            current_event_phase = [row['wave6_phase']]
            current_event_amp = [row['env_max']]
        else:
            current_event_phase.append(row['wave6_phase'])
            current_event_amp.append(row['env_max'])
    event_phase_list.pop(0)    
    event_amp_list.pop(0)

    amp_max = numpy.max(sum(event_amp_list, []))
    amp_min = numpy.min(sum(event_amp_list, []))

    # Create the plot
    fig = plt.figure(figsize=(8,11))
    for phases, amps in zip(event_phase_list, event_amp_list):
        if len(phases) > min_duration:
            x_axis = numpy.arange(0, len(phases))
            phase_data = fix_boundary_data(phases)
            amp_data = numpy.array(amps)

            slope, intercept, r_value, p_value, std_err = stats.linregress(x_axis, phase_data)
            if slope > 0.2:
                cmap = 'Reds'
            elif slope < -0.2:
                cmap = 'Blues'
            else:
                cmap = 'Greys'
            
            points = numpy.array([x_axis, phase_data]).T.reshape(-1, 1, 2)
            segments = numpy.concatenate([points[:-1], points[1:]], axis=1)
            lc = LineCollection(segments, cmap=plt.get_cmap(cmap), norm=plt.Normalize(amp_min, amp_max))
            lc.set_array(amp_data)
            lc.set_linewidth(3)
            plt.gca().add_collection(lc)

    plt.xlim(0, df['duration'].max())
    plt.ylim(0, 83)

    plt.xlabel('day')
    plt.ylabel('wave 6 phase')
   
    plt.savefig(ofile, bbox_inches='tight')


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

    # Compile event duration information
    final['dates'] = final.index
    final['time_delta'] = final['dates'].diff()
    in_event = final['time_delta'] < pandas.tslib.Timedelta('2 days')
    grouped_events = [(k, sum(1 for i in g)) for k,g in groupby(in_event)] 

    #select all days where duration > minimum threshold
    duration = []
    for event in grouped_events:
        if event[0]:
            data = [event[1]] * event[1]
        else:
            data = [0] * event[1]
        duration.append(data)
    final['duration'] = reduce(operator.add, duration)

    if inargs.event_plot:
        assert not inargs.phase_filter and not inargs.season_filter, \
        "Have not added functionality to filter by phase or season for event plot"
        plot_phase(final, inargs.duration_filter, inargs.output_file)
    else: 
	# Optional filtering by duration
	if inargs.duration_filter:
	    final = final.loc[final['duration'] > inargs.duration_filter]

	# Optional filtering by season
	if inargs.season_filter:
            season = inargs.season_filter
            months_subset = pandas.to_datetime(final.index.values).month
            bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
            final = final.loc[bools_subset]

	# Optional filtering by wave phase
	if inargs.phase_filter:
            freq, phase_min, phase_max = inargs.phase_filter
            target_phase = 'wave%i_phase' %(freq)
            final = final.loc[(final[target_phase] > phase_min) & (final[target_phase] < phase_max)]

	# Write date file
	gio.write_dates(inargs.output_file, final.index.values)

    metadata_dict = {inargs.fourier_file: dset_in.attrs['history']}
    gio.write_metadata(inargs.output_file, file_info=metadata_dict)


if __name__ == '__main__':

    description='Create a psa date list (or event summary plot) from Fourier information'
    parser = argparse.ArgumentParser(description=description, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("fourier_file", type=str, help="Input file name")
    parser.add_argument("output_file", type=str, help="Output file name")

    parser.add_argument("--max_sign_change", type=int, default=5, 
                        help="maximum number of times the signal can change sign over the search domain [default = 5]")

    parser.add_argument("--event_plot", action="store_true", default=False,
                        help="switch for creating a phase/amplitude summary plot instead [default: False]")

    parser.add_argument("--duration_filter", type=int, default=None, 
                        help="minimum duration for a PSA event [default = no filter]")
    parser.add_argument("--season_filter", type=str, choices=('DJF', 'MAM', 'JJA', 'SON'), default=None, 
                        help="only keep the selected season [default = no season filter]")
    parser.add_argument("--phase_filter", type=float, nargs=3, metavar=['FREQ', 'MIN_PHASE', 'MAX_PHASE'], default=None, 
                        help="phase range to retain at the given frequecy. [default = no filter]")


    args = parser.parse_args()            
    main(args)
