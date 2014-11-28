"""
Filename:     txt_to_nc.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

"""

# Import general Python modules #

import sys, os, pdb
import argparse
import cdtime, cdms2
import numpy
import pandas
from datetime import datetime


# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

def read_Marshall(infile, metric, time_start):
    """Read the data from http://www.antarctica.ac.uk/met/gjma/sam.html"""

    SAM_index = pandas.read_csv(infile, 
                                skiprows=2, 
                                delim_whitespace=True, 
                                header=0, 
                                index_col=0,
                                names=range(1,13))

    output_data = []
    output_times = []
    for year, data in SAM_index.iterrows():
        for month in data.keys():
            if not numpy.isnan(data[month]):
                output_data.append(data[month])
                ct = cdtime.comptime(year, month, 15)
                rt = ct.torel(time_start).value
                output_times.append(rt)

    output_atts = {'id': 'SAM',
                   'standard_name': 'SAM',
                   'long_name': 'Southern Annular Mode index',
                   'units': '',
                   'notes': 'SAM index (Marshall, 2003)'}

    history_dict = {'history': datetime.now().strftime("%a %b %d %H:%M:%S %Y")+': downloaded from http://www.antarctica.ac.uk/met/gjma/sam.html \n'}

    return numpy.array(output_data), output_times, output_atts, history_dict


def read_CPC(infile, metric, time_start):
    """Read the monthly SST data from http://www.cpc.ncep.noaa.gov/data/indices/"""

    name_list = ('nino12', 'nino12_anom', 
                 'nino3', 'nino3_anom', 
                 'nino4', 'nino4_anom',
                 'nino34', 'nino34_anom')

    ENSO_index = pandas.read_csv(infile,  
                                 delim_whitespace=True, 
                                 header=0,
                                 names=name_list, 
                                 index_col=(0,1))

    output_data = []
    output_times = []
    for date, data in ENSO_index.iterrows():
        year, month = date
        if not numpy.isnan(data[metric]):
            output_data.append(data[metric])
            ct = cdtime.comptime(year, month, 15)
            rt = ct.torel(time_start).value
            output_times.append(rt)

    output_atts = {'id': metric,
                   'standard_name': metric,
                   'long_name': metric,
                   'units': 'degrees Celcius',
                   'notes': ''}

    history_dict = {'history': datetime.now().strftime("%a %b %d %H:%M:%S %Y")+': monthly SST data downloaded from http://www.cpc.ncep.noaa.gov/data/indices/ \n'}

    return numpy.array(output_data), output_times, output_atts, history_dict


def create_taxis(time_values, time_start):
    """Create a cdms2 compatible time axis"""

    time = cdms2.createAxis(time_values) 
    time.id = 'time'
    time.standard_name = 'time'
    time.units = time_start
    time.calendar = 'standard'
    time.axis = 'T'

    return time


def main(inargs):
    """Run the program."""
    
    data_sources = {'Marshall': read_Marshall,
                    'CPC': read_CPC}

    output_data, output_times, output_atts, history_dict = data_sources[inargs.source](inargs.infile, inargs.metric, inargs.time_start)
    time_axis = create_taxis(output_times, inargs.time_start)

    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     history_dict, 
                     [output_data,],
                     [output_atts,], 
                     [(time_axis,),])


if __name__ == '__main__':

    extra_info =""" 
example:
  /usr/local/anaconda/bin/python txt_to_nc.py 
  /mnt/meteo0/data/simmonds/dbirving/Indices/newsam.1957.2014.txt 
  SAM Marshall test_SAM.nc
  
"""

    description='Take a text file and convert to netCDF'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("metric", type=str, help="The metric of interest (e.g. SAM, NINO3.4)")
    parser.add_argument("source", type=str, choices=('Marshall', 'CPC'), help="Where the data were obtained from")
    parser.add_argument("outfile", type=str, help="Output file name")
  
    parser.add_argument("--time_start", type=str, default="hours since 1900-01-01 00:00:00",
                        help="Starting point for time axis")

    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)

