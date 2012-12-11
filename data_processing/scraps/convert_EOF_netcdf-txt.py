#!/usr/bin/env cdat

"""
GIT INFO: $Id$
Filename:     convert_EOF_netcdf-txt.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Takes the EOF timeseries from my standard netCDF
              output and writes it into a .txt file compatible
	      with my timeseries plotting routine

Updates | By | Description
--------+----+------------
1 November 2012 | Damien Irving | Initial version.

"""


__version__= '$Revision$'   ## Get this working for Git


### Import required modules ###

import optparse
from optparse import OptionParser
import sys

import cdms2 

from datetime import datetime


### Define functions ###


def main(in_file,in_var,out_file):
    """Run the program"""

    ## Get the input data ##

    fin=cdms2.open(in_file,'r')
    in_data = fin(in_var)
    in_time = fin.getAxis('time').asComponentTime()
    
    years = []
    months = []
    for ii in range(0,len(in_time)):
	years.append(int(str(in_time[ii]).split('-')[0]))
	months.append(int(str(in_time[ii]).split('-')[1]))


    ## Write the text file output ##

    fout = open(out_file,'w')
    fout.write('Timeseries for %s \n' %(in_data.name))
    fout.write('Input file = %s \n' %(in_file))
    fout.write('Created %s using %s \n' %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"),sys.argv[0]))
    fout.write(' YR   MON  %s \n' %(in_var.split('_')[-1].upper())) 

    for ii in range(0,len(in_time)):
	print >> fout, '%4i %3i %7.2f' %(years[ii],months[ii],in_data[ii])

    fout.close()


    
if __name__ == '__main__':

    ## Help and manual information ##

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
  
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(args) != 3:
	print """
	Usage:
            cdat convert_PC_netcdf-txt.py [-M] [-h] {input file} {input_variable} {output file}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    	
	Example (abyss.earthsci.unimelb.edu.au)
	    /opt/cdat/bin/cdat convert_EOF_netcdf-txt.py 
	    /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF_monthly-1979-2012_native-eqpacific.nc 
	    sf_ts_eof1
	    /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF1_monthly_native-eqpacific.txt
	
	Author
            Damien Irving, 1 Nov 2012.

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    else:
                
        print 'Input file:', args[0]
        print 'Output file:', args[2]

        main(args[0],args[1],args[2])
    
