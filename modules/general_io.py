"""
Collection of commonly used functions for general file input
and output

To import:
module_dir = os.path.join(os.environ['HOME'], 'phd', 'modules')
sys.path.insert(0, module_dir)

Included functions:
read_dates      -- Read in a list of dates
write_dates     -- Write a list of dates

"""

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
