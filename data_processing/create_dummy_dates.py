import pdb, os, sys
import datetime
import numpy, pandas

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


season_months = {'DJF': (12, 1, 2), 'MAM': (3, 4, 5), 
                 'JJA': (6, 7, 8), 'SON': (9, 10, 11)}


index = pandas.date_range(datetime.datetime(1979, 1, 1), periods=13200, freq='D')
columns = ['A']

df = pandas.DataFrame(index=index, columns=columns)
df = df.fillna(0)

for season in ['DJF', 'MAM', 'JJA', 'SON']:
    months_subset = pandas.to_datetime(df.index.values).month
    bools_subset = (months_subset == season_months[season][0]) + (months_subset == season_months[season][1]) + (months_subset == season_months[season][2])
    final = df.loc[bools_subset]
 
    outfile = 'dummy_'+season+'_dates.txt'
    gio.write_dates(outfile, final.index.values)
    gio.write_metadata(outfile)
