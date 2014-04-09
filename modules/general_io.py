"""
Collection of commonly used functions for general file input
and output

To import:
module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)

Included functions:
find_duplicates -- Find duplicates in a list
read_dates      -- Read in a list of dates
write_dates     -- Write a list of dates

"""

import sys
from datetime import datetime
from collections import defaultdict

try:
    from git import Repo  #doesn't come standard with uvcdat install
    REPO_DIR = os.path.join(os.environ['HOME'], 'phd')
    MODULE_HASH = Repo(REPO_DIR).head.commit.hexsha
except ImportError:
    MODULE_HASH = 'unknown'

## Alternative provenance tracking, if netcdf_io.py 
#  was under version control directly ##
#repo_dir = os.path.abspath(os.path.dirname(__file__))
#MODULE_HASH = Repo(repo_dir).head.commit.hexsha



def find_duplicates(inlist):
    """Return list of duplicates in a list"""
    
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    D = {k:v for k,v in D.items() if len(v)>1}
    
    return D
    

def get_timestamp():
    """Return time stamp that incuded the command line entry"""
    
    time_stamp = """%s: python %s (Git hash: %s)""" %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), " ".join(sys.argv), MODULE_HASH[0:7])

    return time_stamp


def read_dates(infile):
    """Read a file of dates (one per line) and write to a list"""
    
    fin = open(infile, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()
    date_metadata = date_list.pop(0)

    return date_list, date_metadata


def write_dates(outfile, date_list):
    """Write a list of dates to file"""
    
    fout = open(outfile, 'w')
    timestamp = get_timestamp()
    fout.write(timestamp+'\n')
    for date in date_list:
        fout.write(date+'\n')
    fout.close()


def write_metadata(ofile, file_info=None, extra_notes=None):
    """Write a metadata output file
    
    Arguments:
      ofile        --  name of output image file
      file_info    --  list of file info lists: ['fname', 'var_id', 'global atts history']
      extra_notes  --  list containing character strings of extra information (output is one list item per line)
      
    """
    
    # Open .met file
    fname, extension = ofile.split('.')
    fout = open(fname+'.met', 'w')
    
    # Write the timestamp
    time_stamp = get_timestamp()
    fout.write(time_stamp+'\n \n')
    
    # Write the extra info
    if extra_notes:
        fout.write('Extra notes: \n \n')
	for line in extra_notes:
	    fout.write(line+'\n')
    
    # Write the file details
    if file_info:
        fout.write('\n')
        for ifile in file_info:
	    fname, var_id, history = ifile
	    fout.write('Input file: %s, %s \n \n' %(fname, var_id))
	    fout.write('History: %s \n \n' %(history))
    	
    fout.close()
