#!/usr/bin/env cdat

"""
GIT INFO: $Id$
Filename:     plot_EOF.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Plots the spatial EOF


Updates | By | Description
--------+----+------------
5 November 2012 | Damien Irving | Initial version.

"""


### Import required modules ###

import optparse
from optparse import OptionParser
import sys

import cdms2 

import numpy
import math

import plot_map


def dimensions(nfiles):
    """Determine the correct number of rows and columns for the number of input files"""
    if nfiles <= 2:
        cols=1.0
    elif nfiles <= 6:
        cols=2.0
    elif nfiles <= 9:
        cols=3.0
    elif nfiles <= 16:
        cols=4.0
    else:
        cols=5.0
    
    rows=math.ceil(nfiles/cols)
    
    return int(rows),int(cols)


def shuffle(in_list,rows,cols):
    """Put the input list into the correct order for mpltools.multiplot"""
    rows=int(rows)
    cols=int(cols)
    nfiles = len(in_list)
    nblanks = int((rows*cols) - nfiles)
    start = int(1 + cols*(rows-1))
    
    new_list = []
    for k in range(nfiles+nblanks):
        new_list.append('')
    
    for i in range(nblanks):
       in_list.insert(cols-nblanks,'')
    
    for c in range(cols):
        for r in range(rows):
            new_list[c+(r*cols)] = in_list[start+c-(r*cols)-1]
            
    return new_list


def unpack_comma_list(comma_list,data_type='str'):
    """Converts a comma separated list into a python array"""
    
    if comma_list:  # because it might be 'None'
	if data_type == 'int':
	    python_array = [int(s) for s in comma_list.split(',')]
	elif data_type == 'float':
	    python_array = [float(s) for s in comma_list.split(',')]
	else:
	    python_array = [str(s) for s in comma_list.split(',')]
    else:
	python_array = None

    return python_array


def main(neofs,ifile,var,ofile,title,ticks,segments,equator):

    # Dimensions
    rows,cols = dimensions(neofs)
    dims = [rows,cols]
    
    # Input file list
    ifiles = [ifile] * neofs 
    ifile_list = shuffle(ifiles,rows,cols)
    
    # Variable lists
    variables = []
    for i in range(1,neofs+1):
        variables.append(var+'_spatial_eof'+str(i))
    variable_list = shuffle(variables,rows,cols)
    
    # Map bounds
    fin = cdms2.open(ifiles[0])
    data = fin(variables[0])
    in_lat = data.getLatitude()[:]
    in_lon = data.getLongitude()[:]
    
    minlat = min(in_lat)
    maxlat = max(in_lat)
    minlon = min(in_lon)
    maxlon = max(in_lon)
    
    fin.close()
        
    # Image headings
    img_headings = []
    for i in range(1,neofs+1):
        fin = cdms2.open(ifiles[i-1])
	data = fin(var+'_perc_eof'+str(i))
	img_headings.append('EOF%s  (%3.1f%% variance explained)' %(str(i),data.data))
        fin.close()
    img_headings_list = shuffle(img_headings,rows,cols)


    plot_map.multiplot(ifile_list,
                       variable_list,
		       ofile=ofile,
		       dimensions=dims,
		       minlat=minlat,maxlat=maxlat,minlon=minlon,maxlon=maxlon,
		       img_headings=img_headings_list,
		       draw_axis=True,
		       delat=15,delon=15,
		       equator=equator,
		       contour=True,
		       ticks=unpack_comma_list(ticks,data_type='float'),
		       discrete_segments=unpack_comma_list(segments),
		       title=title
		       )


if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-e", "--equator",action="store_true",dest="equator",default=False,help="plot a distinct gridline for the equator [default = False]")
    parser.add_option("--ofile",dest="ofile",type='string',default=None,help="name of output file [default = test.png]")
    parser.add_option("--ticks", dest="ticks",type='string',default=None,help="List of comma seperataed tick marks to appear on the colour bar")
    parser.add_option("--segments", dest="segments",type='string',default=None,help="List of comma seperated colours to appear on the colour bar")
    parser.add_option("--title",dest="title",type='string',default=None,help="plot title [default = None]")
    
    (options, args) = parser.parse_args()

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            cdat plot_EOF.py [-h] [options] {neofs} {input file} {variable}

	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    
	    --ofile    ->  Name of output file [default = test.png]
	    --equator  ->  Plot a distinct gridline for the equator [default = False]
	    --title    ->  Plot title [default = None]
	    --ticks    ->  List of comma seperataed tick marks to appear on the colour bar [default = automatic]
	    --segments ->  List of comma seperated colours to appear on the colour bar [default = automatic]
	    
	Example (abyss.earthsci.unimelb.edu.au)
	    /opt/cdat/bin/cdat plot_EOF.py 4 
	    /work/dbirving/processed/indices/data/sf_Merra_250hPa_EOF_monthly-1979-2012_native-eqpacific.nc sf 
	    /work/dbirving/processed/indices/figures/sf_Merra_250hPa_EOF_monthly-1979-2012_native-eqpacific.png
	    --title 250hPa_streamfunction_EOF_analysis,_1979-2012,_Merra
	    --ticks -2.5,-2.0,-1.5,-1.0,-0.5,0,0.5,1.0,1.5,2.0,2.5,3.0
	    --segments 'blue7','blue6','blue5','blue4','blue3','red3','red4','red5','red6','red7','red8'
	    
	Author
            Damien Irving, 22 Jun 2012
	    
	Upgrades needed
	    Need to figure out what the units are for EOFs
	    
	Bugs
	    Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    else:

        main(int(args[0]),args[1],args[2],options.ofile,options.title,options.ticks,options.segments,options.equator)
