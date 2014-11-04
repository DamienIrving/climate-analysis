"""
Collection of commonly used functions for general file input
and output

To import:
module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)

Included functions:
find_duplicates   -- Find duplicates in a list
read_dates        -- Read in a list of dates
set_outfile_date  -- Take an outfile name and replace existing date with new one
standard_datetime -- Convert any arbitrary date/time to standard format: YYYY-MM-DD
write_dates       -- Write a list of dates

"""

import os, sys, pdb
from datetime import datetime
from dateutil import parser
from collections import defaultdict
import re

try:
    from git import Repo 
    cwd = os.getcwd()
    repo_dir = '/'
    for directory in cwd.split('/')[1:]:
        repo_dir = os.path.join(repo_dir, directory)
        if directory == 'phd':
            break
    try:
        MODULE_HASH = Repo(repo_dir).head.commit.hexsha
    except AttributeError: # Older versions of gitpython work differently
        MODULE_HASH = Repo(repo_dir).commits()[0].id
except ImportError:
    MODULE_HASH = 'unknown'


def find_duplicates(inlist):
    """Return list of duplicates in a list"""
    
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    D = {k:v for k,v in D.items() if len(v)>1}
    
    return D
    

def get_timestamp():
    """Return time stamp that incuded the command line entry"""
    
    time_stamp = """%s: %s %s (Git hash: %s)""" %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), sys.executable, " ".join(sys.argv), MODULE_HASH[0:7])

    return time_stamp


def read_dates(infile):
    """Read a file of dates (one per line) and write to a list.

    Assumes there is a metadata file corresponding to infile which 
    has exactly the same name but ends with .met

    """
    
    fin = open(infile, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()

    file_body = infile.split('.')[0]
    with open (file_body+'.met', 'r') as metfile:
        date_metadata=metfile.read()

    return date_list, date_metadata


def set_outfile_date(outfile, new_date):
    """Take an outfile name and replace the existing date
    (in YYYY-MM-DD format) with new_date"""

    new_dt = parser.parse(str(new_date))
    
    date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
    assert re.search(date_pattern, outfile), \
    """Output file must contain the date of the final timestep in the format YYYY-MM-DD"""
    
    return re.sub(r'([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})', new_dt.strftime("%Y-%m-%d"), outfile)


def standard_datetime(dt):
    """Take any arbitrarty date/time and convert to the standard
    I use for all outputs: YYYY-MM-DD"""

    new_dt = parser.parse(str(dt))

    return new_dt.strftime("%Y-%m-%d")


def write_dates(outfile, date_list):
    """Write a list of dates to file"""
    
    fout = open(outfile, 'w')
    for date in date_list:
        fout.write(date+'\n')
    fout.close()


def write_metadata(ofile=None, file_info=None, extra_notes=None):
    """Write a metadata output file
    
    Arguments:
      ofile        --  name of output file that we want to create a .met file
                       alongside (i.e. new file with .met extension will be created)
      file_info    --  a dictionary where keys are filenames and values are the global attribute history
      extra_notes  --  list containing character strings of extra information (output is one list item per line)
      
    """
    
    result = ''
        
    # Write the timestamp
    time_stamp = get_timestamp()
    result += time_stamp + '\n'
    
    # Write the extra info
    if extra_notes:
        result += 'Extra notes: \n'
        for line in extra_notes:
            result += line + '\n'
    
    # Write the file details
    if file_info:
        assert type(file_info) == dict
        nfiles = len(file_info.keys())
        for fname, history in file_info.iteritems():
            if nfiles > 1:
                result += 'History of %s: \n %s \n' %(fname, history)
            else:
                result += '%s \n' %(history)
    
    # Create outfile or return string
    if ofile:
        fname, extension = ofile.split('.')
        fout = open(fname+'.met', 'w')
        fout.write(result) 
        fout.close()
    else:
        return result
