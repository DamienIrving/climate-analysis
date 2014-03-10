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

from collections import defaultdict


def find_duplicates(inlist):
    """Return list of duplicates in a list"""
    
    D = defaultdict(list)
    for i,item in enumerate(mylist):
        D[item].append(i)
    D = {k:v for k,v in D.items() if len(v)>1}
    
    return D
    

def read_dates(infile):
    """Read a file of dates (one per line) and write to a list"""
    
    fin = open(infile, 'r')
    date_list = []
    for line in fin:
        date_list.append(line.rstrip('\n'))
    fin.close()

    return date_list


def write_dates(outfile, date_list):
    """Write a list of dates to file"""
    
    fout = open(outfile, 'w')
    for date in date_list:
        fout.write(date+'\n')
    fout.close()
