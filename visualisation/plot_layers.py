#!/usr/bin/env cdat

"""
GIT INFO: $Id$
Filename:     plot_layers.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au

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

from time import strftime
from datetime import datetime



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

def month_text(month_number):
    """Converts a month number to the text name"""
    
    formated_month = datetime(2012, int(month_number), 1)
    selected_month = formated_month.strftime("%b")
    
    return selected_month


def main(primary_files,primary_variables,ofile,contour_files,quiver_files,title,
         dates,region,ticks,units,contour_ticks,quiver_type,thin,key_value,equator,image_size):

    # Dimensions
    nfiles = len(primary_files)
    
    rows,cols = dimensions(nfiles)
    dims = [rows,cols]
    
    # Primary file list
    primary_file_list = shuffle(primary_files,rows,cols)
    primary_variable_list = shuffle(primary_variables,rows,cols)
    
    # Contour files
    if contour_files:
        draw_contours = True
	
	contour_file_list = unpack_comma_list(contour_files[0])
	contour_variable_list = unpack_comma_list(contour_files[1])
	
	assert len(contour_file_list) == nfiles, "wrong number of contour files"
        assert len(contour_variable_list) == nfiles, "wrong number of contour variables"
	
	contour_file_list = shuffle(contour_file_list,rows,cols)
	contour_variable_list = shuffle(contour_variable_list,rows,cols)
   
    else:
        draw_contours = False
	contour_file_list = None
	contour_variable_list = None
	
    
    # Quiver files
    if quiver_files:
        draw_quivers = True
	
	quiverx_file_list = unpack_comma_list(quiver_files[0])
	quiverx_variable_list = unpack_comma_list(quiver_files[1])
	quivery_file_list = unpack_comma_list(quiver_files[2])
	quivery_variable_list = unpack_comma_list(quiver_files[3])
	
	assert len(quiverx_file_list) == nfiles, "wrong number of quiver x files"
        assert len(quiverx_variable_list) == nfiles, "wrong number of quiver x variables"
	assert len(quivery_file_list) == nfiles, "wrong number of quiver y files"
        assert len(quivery_variable_list) == nfiles, "wrong number of quiver y variables"
        
	quiverx_file_list = shuffle(quiverx_file_list,rows,cols)
	quiverx_variable_list = shuffle(quiverx_variable_list,rows,cols)
	quivery_file_list = shuffle(quivery_file_list,rows,cols)
	quivery_variable_list = shuffle(quivery_variable_list,rows,cols)
    
    else:
        draw_quivers = False
	quiverx_file_list = None
	quiverx_variable_list = None
	quivery_file_list = None
	quivery_variable_list = None

    # Title
    
    start_year, start_month, start_day = dates[0].split('-')
    end_year, end_month, end_day = dates[1].split('-')
    
    if (start_year == end_year) and (start_month == end_month):
        new_title = '%s %s %s' %(title,month_text(start_month),start_year)
    else:
        new_title = '%s %s %s to %s %s ' %(title,month_text(start_month),start_year,month_text(end_month),end_year)

    
    plot_map.multiplot(primary_file_list,
                       primary_variable_list,
		       dimensions=dims,
		       ofile=ofile,
		       title=new_title,
		       timmean=dates,
		       region=region,
		       colourbar_colour='RdBu_r',
		       extend='both',
		       ticks=unpack_comma_list(ticks,data_type='float'),
		       units=units,
		       draw_contours=draw_contours,
		       contour_files=contour_file_list,
		       contour_variables=contour_variable_list,
		       contour_ticks=unpack_comma_list(contour_ticks,data_type='float'),
		       draw_vectors=draw_quivers,
		       vector_type=quiver_type,
		       uwnd_files=quiverx_file_list,
		       uwnd_variables=quiverx_variable_list,
		       vwnd_files=quivery_file_list,
		       vwnd_variables=quivery_variable_list,
		       thin=thin,
		       key_value=key_value,
		       draw_axis=True,
		       delat=30,
		       delon=30,
		       equator=equator,
		       enso=True,
		       contour=True,
		       image_size=image_size
		       )


if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M","--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-o","--ofile",dest="ofile",type='string',default=None,help="name of output file [default = test.png]")
    parser.add_option("-c","--contour_files",dest="contour_files",type='string',nargs=2,default=None,help="Two comma seperated contour lists (files variables) [default = None]")
    parser.add_option("-q","--quiver_files",dest="quiver_files",type='string',nargs=4,default=None,help="Four comma seperated quiver lists (x_dir_files x_vars y_files y_vars) [default = None]")
    parser.add_option('-d',"--dates",dest="dates",type='string',nargs=2,default=None,help="Two integer times (start_date end_date) [default = None]")
    parser.add_option("--title",dest="title",type='string',default='',help="plot title [default = date only]")
    parser.add_option("--region",dest="region",type='string',default='WORLD_DATELINE',help="name of region to plot [default = WORLD_DATELINE]")
    parser.add_option("--ticks", dest="ticks",type='string',default=None,help="List of comma seperated tick marks to appear on the colour bar [default = automatic]")
    parser.add_option("--units", dest="units",type='string',default=None,help="Units")
    parser.add_option("--contour_ticks", dest="contour_ticks",type='string',default=None,help="List of comma seperated tick marks for the contours [default = automatic]")
    parser.add_option("--quiver_type", dest="quiver_type",type='string',default='wind',help="Type of quiver being plotted [defualt = wind]")
    parser.add_option("--thin", dest="thin",type='int',default=1,help="Thinning factor for plotting wind vectors [defualt = 1]")
    parser.add_option("--key_value", dest="key_value",type='float',default=1.0,help="Size of the wind vector in the key (plot is not scaled to this) [defualt = 1]")
    parser.add_option("--equator",action="store_true",dest="equator",default=False,help="plot a distinct gridline for the equator [default = False]")
    parser.add_option("--image_size", dest="image_size",type='float',default=10.,help="Size of image [default = 10]")
    
    
    (options, args) = parser.parse_args()

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            cdat plot_layers.py [-h] [-c] [-q] [options] {primary files} {primary variables}
            
	    {primary files}         List of comma seperated primary files
	    {primary variables}     List of comma seperated primary variables
	      
	Options
            -M  ->  Display this on-line manual page and exit
            -h  ->  Display a help/usage message and exit
	    
	    --ofile          ->  Name of output file [default = test.png]
	    --contour_files  ->  Two comma seperated contour lists (files variables) [default = None]
	    --quiver_files   ->  Four comma seperated quiver lists (x_dir_files x_vars y_files y_vars) [default = None]
	    --dates          ->  Four integer times (start_date end_date) [default = None]
	                         e.g. 1980-09-01 1980-09-27  (for monthly data would give Sept 1980)
	    --region         ->  Selector defining a region (for cylindrical projection). Inbuilt regions are WORLD_GRENEWICH, WORLD_DATELINE, AUSTRALIA, AUS_NZ [default = WORLD_DATELINE]
	    --title          ->  Plot title [default = date only]
	    --ticks          ->  List of comma seperataed tick marks to appear on the colour bar [default = automatic]
	    --units          ->  Units of the data - appears as a label below the colourbar
	    --contour_ticks  ->  List of comma seperated tick marks for the contours [default = automatic]
	    --quiver_type    ->  Type of quiver being plotted (determines units for quiver key). Can be 'wind' or 'waf' (wave activity flux) [default = 'wind']
	    --thin           ->  Thinning factor for plotting wind vectors (e.g. 2 = every second vector; 3 = every third) [default = 1]
            --key_value      ->  Magnitude of the vector shown in the legend (plot vectors are not scaled to this) [default = 1]
	    --equator        ->  Plot a distinct gridline for the equator [default = False]
	    --image_size     ->  Width of individual images (in inches) [default = 10]
	    
	Example (abyss.earthsci.unimelb.edu.au)
	    /opt/cdat/bin/cdat plot_layers.py
	    /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc ts
	    /work/dbirving/processed/spatial_maps/ts-sf-waf_Merra_surface-250hPa-250hPa_monthly-anom-wrt-1981-2010_native.png
	    -c /work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc sf
	    -q /work/dbirving/datasets/Merra/data/processed/wafx_Merra_250hPa_monthly_native.nc wafx
	       /work/dbirving/datasets/Merra/data/processed/wafy_Merra_250hPa_monthly_native.nc wafy  
	    --title Merra_skin_temp_anomaly_and_250hPa_streamfunction_anomaly,
	    --ticks -5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5 
	    --units Celsius
	    --dates 2009-05-01 2009-05-27
	    -o /work/dbirving/processed/spatial_maps/ts-sf_Merra_surface-250hPa_May2009-anom-wrt-1981-2010_native-ocean.png
	    
	Author
            Damien Irving, 5 Nov 2012
	    
	List of interesting month/years (peak listed)
            Eastern Pacific El Nino, 1982/83: Jan,1983 or Jun,1983
            Central Pacific El Nino, 1990/91: Jan,1991
            Central Pacific El Nino, 1994/95: Feb,1995
            Eastern Pacific El Nino, 1997/98: Dec,1997
            Central Pacific El Nino, 2002/03: Nov,2002 or Mar,2003
            The Modoki             , 2004   : Aug,2004
            Central Pacific El Nino, 2009/10: Dec,2009
	    
	Required updates
	    Put date on image header
	
	Bugs
	    Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    else:

        main(unpack_comma_list(args[0]),   # primary_files
	     unpack_comma_list(args[1]),   # primary_variables
	     options.ofile,                # ofile
	     options.contour_files,
	     options.quiver_files,
	     options.title,
	     options.dates,
	     options.region,
	     options.ticks,
	     options.units,
	     options.contour_ticks,
	     options.quiver_type,
	     options.thin,
	     options.key_value,
	     options.equator,
	     options.image_size
	     )
