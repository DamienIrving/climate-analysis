#!/tools/python/2.5.1/bin/python

"""
SVN INFO: $Id$
Filename:     plot_map.py
Description:  Creates a spatial plot     

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

"""

__version__= '$Revision$'


### Import required modules ###

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid

import matplotlib.colors

from scipy import interpolate
import numpy
import numpy.ma as ma
import math

import cdms2
import cdutil

import optparse
from optparse import OptionParser
import re
import sys
import os
from datetime import datetime

import pylab


### Define globals ###

#Regions
AUSTRALIA = cdms2.selectors.Selector(latitude=(-45,-10,'cc'),longitude=(110,160,'cc'))
AUS_NZ = cdms2.selectors.Selector(latitude=(-50,0,'cc'),longitude=(100,185,'cc'))
WORLD_GREENWICH = cdms2.selectors.Selector(latitude=(-90,90,'cc'),longitude=(-180,180,'cc'))
WORLD_DATELINE = cdms2.selectors.Selector(latitude=(-90,90,'cc'),longitude=(0,360,'cc'))

#Colours
blue1,blue2,blue3,blue4,blue5, = ['#EAF4FF','#DFEFFF','#BFDFFF','#95CAFF','#55AAFF']
blue6,blue7,blue8,blue9,blue10 = ['#0B85FF','#006AD5','#004080','#002B55','#001B35']

brown1,brown2,brown3,brown4,brown5, = ['#FFFAEA','#FFF8DF','#FFEFBF','#FFE495','#FFD555']
brown6,brown7,brown8,brown9,brown10 = ['#FFC20B','#D59F00','#806000','#554000','#352800']

hot1,hot2,hot3,hot4,hot5, = ['#FFFFEA','#FFFFDF','#FFFF95','#FFFF0B','#FFAA0B']
hot6,hot7,hot8,hot9,hot10 = ['#FF660B','#FF0B0B','#800000','#550000','#350000']

red1,red2,red3,red4,red5, = ['#FFEAEA','#FFDFDF','#FFBFBF','#FF9595','#FF5555']
red6,red7,red8,red9,red10 = ['#FF0B0B','#D50000','#800000','#550000','#350000']

green1,green2,green3,green4,green5, = ['#F4FFEA','#EFFFDF','#DFFFBF','#CAFF95','#AAFF55']
green6,green7,green8,green9,green10 = ['#85FF0B','#6AD500','#408000','#2B5500','#1B3500']

purple1,purple2,purple3,purple4,purple5, = ['#F4EAFF','#EFDFFF','#DFBFFF','#CA95FF','#AA55FF']
purple6,purple7,purple8,purple9,purple10 = ['#850BFF','#6A00D5','#400080','#2B0055','#1B0035']

grey1,grey2,grey3,grey4,grey5,grey6 = ['#FFFFFF','#EBEBEB','#E6E6E6','#DCDCDC','#D2D2D2','#CCCCCC']
grey7,grey8,grey9,grey10,grey11,grey12 = ['#787878','#666666','#4B4B4B','#333333','#1E1E1E','#000000']

jet0,jet1,jet2,jet3,jet4,jet5,jet6 = ['#001B35','#000080','#0000D5','#006AD5','#55AAFF','#55FFFF','#55FFAA']
jet7,jet8,jet9,jet10,jet11,jet12 = ['#D5FF55','#FFD555','#FF850B','#D51B00','#800000','#350000']

IPCCrain1,IPCCrain2,IPCCrain3,IPCCrain4,IPCCrain5,IPCCrain6 = ['#FFF295','#FFD555','#FF850B','#D55000','#D50000','#550040']
IPCCrain7,IPCCrain8,IPCCrain9,IPCCrain10,IPCCrain11,IPCCrain12 = ['#600080','#000080','#0000D5','#0B85FF','#55AAFF','#95CAFF']

grey = '#CCCCCC'
white = '#FFFFFF'


### Define functions ###


def quickplot(ifile,ofile=None,variable=None):
    """Function for producing a quick plot using all default values"""
    
    if not os.path.exists(ifile):
        print "ERROR input file %s does not exists" % ifile
        sys.exit(1)

    multiplot(ifile,variable,os.path.basename(ifile))


def multiplot(ifiles,variables,
              #Variables below here are optional, should give a reasonable image by default
              dimensions=None,
              #Output file name and title
              ofile=None,title=None,timmean=None,
              #can use a pre-defined region or override with min/max lat/lon, 
              region=WORLD_DATELINE,minlat=None,minlon=None,maxlat=None,maxlon=None,latX=-20,lonX=-125,projection='cyl',
              #colourbar settings
              colourbar_colour='jet',ticks=None,discrete_segments=None,units=None,convert=False,scale=None,extend="neither",
              #resolution of image
              res='l',area_threshold=1.,
	      #contours
	      draw_contours=False,contour_files=None,contour_variables=None,contour_ticks=None,contour_scale=None,
	      #wind vectors
	      draw_vectors=False,vector_type='wind',uwnd_files=None,uwnd_variables=None,vwnd_files=None,vwnd_variables=None,thin=1,key_value=1,
	      quiver_scale=170,quiver_width=0.0015,quiver_headwidth=3.5,quiver_headlength=4.0,
	      #stippling
	      draw_stippling=False,stipple_files=None,stipple_variables=None,
              #Headings if using mutiple plots in a single plot
              row_headings=None,inline_row_headings=False,col_headings=None,img_headings=None,
              #Axis options to draw lat/lon lines
              draw_axis=False,delat=30,delon=30,equator=False,enso=False,
	      #contour plot
	      contour=False,
              #Width of image in inches (individual image)
              #so single imgage would be 6 inches wide or image with two columns would be 12 inches wide etc.)
              image_size=6,
	      textsize=18):

    """Takes all the input arguments and determines the correct call to matrixplot"""

    ifiles = str2list(ifiles)
    variables = str2list(variables)

    file_matrix = numpy.array(ifiles)
    var_matrix = numpy.array(variables)


    ## Reshape the file, variable and header lists according to the plot dimensions ##
    
    if not dimensions:
        dimensions = (len(ifiles),1)
        file_matrix = numpy.reshape(file_matrix,(len(ifiles),1))
        file_matrix = numpy.tile(file_matrix,(1,len(variables)))
        var_matrix = numpy.tile(var_matrix,(len(ifiles),1))
    else:
        file_matrix = numpy.reshape(file_matrix,(dimensions))
        var_matrix = numpy.reshape(var_matrix,(dimensions))

    if img_headings:
        img_headings = numpy.reshape(img_headings,(dimensions))


    ## Call matrixplot, accounting for the special cases that require additional data (e.g. wind vectors or stippling) ##

        
    matrixplot(file_matrix,var_matrix,
               ofile,title,timmean,
               region,minlat,minlon,maxlat,maxlon,latX,lonX,projection,
               colourbar_colour,ticks,discrete_segments,units,convert,scale,extend,
               res,area_threshold,
	       draw_contours,reshape_list(contour_files,(dimensions)),reshape_list(contour_variables,(dimensions)),contour_ticks,contour_scale,
	       draw_vectors,vector_type,reshape_list(uwnd_files,(dimensions)),reshape_list(uwnd_variables,(dimensions)),reshape_list(vwnd_files,(dimensions)),reshape_list(vwnd_variables,(dimensions)),thin,key_value,
	       quiver_scale,quiver_width,quiver_headwidth,quiver_headlength,
	       draw_stippling,reshape_list(stipple_files,(dimensions)),reshape_list(stipple_variables,(dimensions)),
               row_headings,inline_row_headings,col_headings,img_headings,
               draw_axis,delat,delon,equator,enso,
	       contour,
               image_size,
	       textsize) 


def matrixplot(ifiles,variables,
              #Variables below here are optional, should give a reasonable image by default
              #Output file name default is 'title'.png
              ofile=None,title=None,timmean=None,
              #can use a pre-defined region or override with min/max lat/lon, 
              region=WORLD_DATELINE,minlat=None,minlon=None,maxlat=None,maxlon=None,latX=-20,lonX=-125,projection='cyl',
              #colourbar settings
              colourbar_colour='jet',ticks=None,discrete_segments=None,units=None,convert=False,scale=None,extend="neither",
              #resolution of image
              res='l',area_threshold=1.,
	      #contours
	      draw_contours=False,contour_files=None,contour_variables=None,contour_ticks=None,contour_scale=None,
	      # wind vectors
	      draw_vectors=False,vector_type='wind',uwnd_files=None,uwnd_variables=None,vwnd_files=None,vwnd_variables=None,thin=1,key_value=1,
	      quiver_scale=170,quiver_width=0.0015,quiver_headwidth=3.5,quiver_headlength=4.0,
	      # stippling
	      draw_stippling=False,stipple_files=None,stipple_variables=None,
              #Headings if using mutiple plots in a single plot
              row_headings=None,inline_row_headings=False,col_headings=None,img_headings=None,
              #Axis options to draw lat/lon lines
              draw_axis=False,delat=30,delon=30,equator=False,enso=False,
	      #contour plot
	      contour=False,
              #Width of image in inches (individual image)
              #so single imgage would be 6 inches wide or image with two columns would be 12 inches wide etc.)
              image_size=6,
              #Change text size
              textsize=18):
	      
    """Takes all the input arguments and determines the correct call to matrixplot"""


    ## Perform initial checks ##

    #Check size of file and var matrix
    if not (ifiles.size == variables.size):
        print "ERROR file and variable matrix are different sizes"
        sys.exit()

    #rows/cols
    nrows = len(ifiles[:,0])
    ncols = len(ifiles[0,:])
    
    if ofile:
        if os.path.exists(ofile):
            print "WARNING replacing output file '%s'" % ofile

    #Check length of headings matches num files/variables
    if(row_headings):
        row_headings = str2list(row_headings)

        if not (len(row_headings) == nrows):
            print "Error row headings do not match number of rows, ",
            print "there are %s rows and %s headings" % (nrows,len(row_headings))
            sys.exit(1)

    if(col_headings):
        col_headings = str2list(col_headings)

        if not (len(col_headings) == ncols):
            print "Error column headings do not match number of columns, ",
            print "there are %s columns and %s headings" % (ncols,len(col_headings))
            sys.exit(1)


    ## Define the bounding region for the plot ##
    
    # map string region to selector object
    if isinstance(region, basestring):
        if region in globals():
            region = globals()[region]
    
    #apply custom region if necessary
    if minlat is not None and maxlat is not None and \
         minlon is not None and maxlon is not None:
	region = cdms2.selectors.Selector(latitude=(minlat,maxlat,'cc'),longitude=(minlon,maxlon,'cc'))
    elif isinstance(region, cdms2.selectors.Selector):
	for selector_component in region.components():
            if selector_component.id == 'lat':
                minlat = selector_component.spec[0]
                maxlat = selector_component.spec[1]
            elif selector_component.id == 'lon':
                minlon = selector_component.spec[0]
                maxlon = selector_component.spec[1]
    else:
        print "Error could not determine region"
        sys.exit(1)


    ## Define the colourbar ##

    #Make sure discrete_segments is in the correct format
    if isinstance(discrete_segments,list):
        if len(discrete_segments) == 1:
	    discrete_segments = int(discrete_segments[0])

    #Setup colour map (unless custom which is created later)
    if discrete_segments or ticks:
        continuous_colourbar = False
    else:
        continuous_colourbar = True
    
    if colourbar_colour:
	if hasattr(plt.cm, colourbar_colour):
            colourmap = getattr(plt.cm, colourbar_colour)
	elif(isinstance(colourbar_colour,matplotlib.colors.LinearSegmentedColormap)):
            colourmap = colourbar_colour
	else:
            print "Error, color option '",colourbar_colour,"' not a valid option"
            sys.exit(1)
	    
    #Get the min/max level for colourbar settings
    #TODO, perhaps use -/+ 2 standard deviations if no min/max specified 
    #as outlies will reduce colours/featues, you may end up with an image entirely one
    #colour and a dark/light spot representing the outlier
    if ticks:
        min_level = ticks[0]
        max_level = ticks[-1]
    else:
        min_level,max_level = get_min_max(ifiles,variables,timmean,region)
	diff = max_level - min_level
	if isinstance(discrete_segments,list):
	    step = diff/float(len(discrete_segments))
	elif discrete_segments:
	    step = diff/float(discrete_segments)
	else:
	    step = diff/10.0
	    
	ticks = list(numpy.arange(min_level,max_level+(step/2),step))

    dec = decimal_places(max_level - min_level)
    space = abs(ticks[0]-ticks[1])*0.2
    
    if extend == 'both':
        min_level = min_level - space
        max_level = max_level + space
        ticks.append(max_level)
        ticks.insert(0,min_level)

    if extend == 'max':
        max_level = max_level + space
        ticks.append(max_level)
	    
    if extend == 'min':
        min_level = min_level - space
        ticks.insert(0,min_level)


    #Colourbar can be converted to a number of discete segments or a custom
    #colourmap can be defined forcing it to a discrete map
    
    if isinstance(discrete_segments,list):
	if discrete_segments[0] in globals():
            for i in range(0,len(discrete_segments)):
		discrete_segments[i] = globals()[discrete_segments[i]]

    if isinstance(discrete_segments,list):
        if len(discrete_segments) != (len(ticks)-1):
	    print 'Number of input colour segments does not match number of ticks - check extension setting'
	    sys.exit(1)
	colourmap = matplotlib.colors.ListedColormap(discrete_segments[:], 'indexed')
    elif discrete_segments:
        if discrete_segments != (len(ticks)-1):
	    print 'Number of input colour segments does not match number of ticks - check extension setting'
	    sys.exit(1)
	colourmap = generate_colourmap(colourmap,discrete_segments)
    elif not continuous_colourbar:
	colourmap = generate_colourmap(colourmap,len(ticks))        
	

    #Remove added elements as we dont wont these displayed
    if extend == 'both':
        ticks = ticks[1:-1]
    
    if extend == 'max':
        ticks = ticks[0:-1]

    if extend == 'min':
        ticks = ticks[1:]
    
    ## Define the contour plot ticks, if required ##
    
    if draw_contours:
        if contour_ticks == None:
            contour_min_level,contour_max_level = get_min_max(contour_files,contour_variables,timmean,region,plot='contour')
	    contour_diff = contour_max_level - contour_min_level
	    contour_step = contour_diff/10.0

	    contour_ticks = list(numpy.arange(contour_min_level,contour_max_level+(contour_step/2),contour_step))
            if contour_max_level > 0 and contour_min_level < 0:
		contour_ticks[5] = 0.0
	else:
	    contour_min_level,contour_max_level = [contour_ticks[0],contour_ticks[-1]]
	    
	contour_dec = decimal_places(contour_max_level - contour_min_level)
    
    ## Define the image size and padding ##
    
    #Image size in inches
    iwidth = float(image_size)
    iheight =  ((maxlat - minlat)/((maxlon - minlon)*1.0))*float(image_size)

    #Item sizes in inches
    title_size        = 0.3
    col_heading_size  = 0.25
    img_heading_size  = 0.2
    if row_headings and not inline_row_headings:
        row_heading_size  = max(0.16 * max(len(rt) for rt in row_headings),
                                0.4)
    else:
        row_heading_size  = 0.1

    colourbar_size    = 0.25  
    hpadding_size     = 0.2
    
    if img_headings is not None:
        vpadding_size = 0.4
    else:
        vpadding_size = hpadding_size
	
    text_padding_size = 0.05

    #Image headings
    img_heading_size = 0.2
    rowcolfsize = textsize
    
    #Total page dimensions
    height = title_size + vpadding_size*2 + col_heading_size + (img_heading_size+text_padding_size)*nrows + nrows*iheight + (nrows+2)*vpadding_size + colourbar_size    # used to be vpadding_size*2
    width = hpadding_size + row_heading_size + ncols*iwidth + (ncols+1)*hpadding_size
 
    #Dimensions in percentages
    pwidth      = iwidth/width
    pheight     = iheight/height
    titlepos    = title_size/height
    hpadding    = hpadding_size/width
    vpadding    = vpadding_size/height
    tpadding    = text_padding_size/height
    row_heading = row_heading_size/width
    col_heading = col_heading_size/height
    img_heading = img_heading_size/height
    colourbar   = colourbar_size/height

    if img_headings is not None:
        cbarbuffer = 3*vpadding
    else:
        cbarbuffer = 4*vpadding


    ## Create the plot, one thumbnail at a time ##

    fig=plt.figure(figsize=(width,height))
    if title:
        fig.suptitle(title.replace('_',' '),y=(1-titlepos),size=16)

    #for row,ifile in enumerate(ifiles):
    for row in range(nrows):
        for col in range(ncols):
	
            # Open file and extract data #

            #Skip image if blank or set to "N/A or n/a"
            if (not os.path.exists(ifiles[row][col])) or (not variables[row,col]) or variables[row,col].lower() == "n/a" :
                if (ifiles[row][col] and ifiles[row][col].lower() != "n/a") or variables[row,col].lower() != "n/a":
                    print "WARNING skipping position '(%s,%s)' : file '%s' and variable '%s'" % (row,col,ifiles[row][col],variables[row,col])
                continue

            #Otherwise open
	    tVar,tVar_lon,tVar_lat = extract_data(ifiles,variables,row,col,timmean=timmean,region=None)
	   
	    #White mask for stippling disagreement
	    if draw_stippling:
	        fin_stip = cdms2.open(stipple_files[row,col],'r')
	        stipple = fin_stip(stipple_variables[row,col])
		
		mask = numpy.where(stipple == 100.0, 1, 0)
		tVar = ma.masked_array(tVar, mask=mask)
	   
	        fin_stip.close()
	    
	    
	    # Plot the axes and map #
	    
	    if projection == 'cyl':
		map = Basemap(llcrnrlon=minlon,llcrnrlat=minlat,urcrnrlon=maxlon,urcrnrlat=maxlat,\
                              resolution=res,area_thresh=area_threshold,projection='cyl')
		#tVar,tVar_lon = shiftgrid(0.,tVar,tVar_lon,start=True)
            elif projection == 'nsper':
	        h = 3000000  #height of satellite
		map = Basemap(projection='nsper',lon_0=lonX,lat_0=latX,satellite_height=h*1000.,resolution=res,area_thresh=area_threshold)
		tVar,tVar_lon = shiftgrid(180.,tVar,tVar_lon,start=False)
	    else:
	        print 'Map projection not recognised'
		sys.exit(0)
		

            #Setup axis and draw figure
            xres = 100
            yres = 100
            ax = fig.add_axes([row_heading+(col*(pwidth+hpadding)),colourbar+cbarbuffer+(row*(pheight+vpadding)),pwidth,pheight]) 
            
	    
            datout = map.transform_scalar(tVar.data, 
                                          tVar_lon[:],
                                          tVar_lat[:],
                                          xres, yres,
                                          order=0)
	      
					  
            # Plot the primary data (i.e. the data that uses the colourbar) #
	                
	    if contour: 
	        x,y = map(*numpy.meshgrid(tVar_lon,tVar_lat))
		im = map.contourf(x,y,tVar,ticks,cmap=colourmap,extend=extend)

	    else:
                if draw_stippling:
		    maskout = map.transform_scalar(mask.data, 
                                          tVar_lon,
                                          tVar_lat,
                                          xres, yres,
                                          order=0)
		
		    datout_masked = ma.masked_array(datout, mask=maskout)
		
		else:
		
		    datout_masked = datout
		
		im = map.imshow(datout_masked,colourmap,vmin=min_level,vmax=max_level)
#                im = map.imshow(datout,colourmap,vmin=min_level,vmax=max_level)
	    
            map.drawcoastlines()


            # Plot the secondary data #
    
            if draw_contours:
		contour_data,contour_lon,contour_lat = extract_data(contour_files,contour_variables,row,col,timmean=timmean,scale=contour_scale)

		if projection == 'nsper':
		    contour_data,contour_lon = shiftgrid(180.,contour_data,contour_lon,start=False)
		    
		x,y = map(*numpy.meshgrid(contour_lon,contour_lat))
		im2 = map.contour(x,y,contour_data,contour_ticks,colors='k')
		plt.clabel(im2, fontsize=5, inline=1, fmt='%.'+str(contour_dec)+'f')      #fmt='%1.1f'  #levels[1::2] for label every second level
	    
	        #Thicken the zero contour
		try:
		    index = contour_ticks.index(0)
		    zc = im2.collections[index]
                    plt.setp(zc, linewidth=1.5)
	        except ValueError:
		    print 'no zero contour'
	  
	    if draw_vectors:
		uas_data,uas_lon,uas_lat = extract_data(uwnd_files,uwnd_variables,row,col,timmean=timmean)
		vas_data,vas_lon,vas_lat = extract_data(vwnd_files,vwnd_variables,row,col,timmean=timmean)
		
	        #latsq2.units = 'degrees_north'
		#lonsq2.units = 'degrees_east'
                
		if projection == 'nsper':
		    uas_data,uas_lon = shiftgrid(180.,uas_data,uas_lon,start=False)
		    vas_data,vas_lon = shiftgrid(180.,vas_data,vas_lon,start=False)
		
        	x,y = map(*numpy.meshgrid(uas_lon,uas_lat))
        	t = int(thin)
		Q = map.quiver(x[::t,::t],y[::t,::t],uas_data[::t,::t],vas_data[::t,::t],units='height',scale=quiver_scale,
		width=quiver_width,headwidth=quiver_headwidth,headlength=quiver_headlength)
		
		if vector_type == 'wind':
		    key_units = 'm\, s^{-1}'
		elif vector_type == 'waf':   # wave activity flux
		    key_units = 'm^{2}\, s^{-2}'
		else:
		    print 'Vector type not recognised'
		    sys.exit(0)
		
		qk = pylab.quiverkey(Q, 0.9, 0.95, key_value, r'$%s\; %s$' %(key_value,key_units), labelpos='E',coordinates='figure',fontproperties={'weight': 'bold'})
	    
	    if draw_stippling:
	        stipple_data,stipple_lon,stipple_lat = extract_data(stipple_files,stipple_variables,row,col) #region=region
		
	        #latsq3.units = 'degrees_north'
		#lonsq3.units = 'degrees_east'
		
		if projection == 'nsper':
		    stipple_data,stipple_lon = shiftgrid(180.,stipple_data,stipple_lon,start=False)
				            
		for iy, lat in enumerate(stipple_lat[:]):
        	    for ix, lon in enumerate(stipple_lon[:]):
                        agreement = stipple_data[iy,ix]
			x,y = map(*numpy.meshgrid(numpy.array([lon]),numpy.array([lat])))
			if agreement == 1:
	                    map.plot(x,y,marker='o',markersize=2.0,markerfacecolor='black',markeredgecolor='black',markeredgewidth=0.2) 
	                elif agreement == 2:
	                    map.plot(x,y,marker='o',markersize=2.0,markerfacecolor='red',markeredgecolor='red',markeredgewidth=0.2)  
			elif agreement == 10:
	                    map.plot(x,y,marker=7,markersize=3.0,markeredgewidth=0.6,markerfacecolor='black',markeredgecolor='black') 
			    #map.plot(x,y,marker='x',markersize=3.5,markeredgecolor='black') # markeredgewidth=0.3,markerfacecolor='None',)
			elif agreement == 20:
	                    map.plot(x,y,marker=7,markersize=3.0,markeredgewidth=0.6,markerfacecolor='red',markeredgecolor='red')
#	                elif agreement == 100:
#	                    map.plot(x,y,marker='|',markersize=3.0,markeredgewidth=0.6,markerfacecolor='black',markeredgecolor='black')
	   

	    # Print the headings #
	    
	    if img_headings is not None:
	    
		if(col == 0 and row_headings):
                    fig.text(hpadding,colourbar+cbarbuffer+(row*(pheight+vpadding))+pheight/2.,row_headings[row],size=rowcolfsize,rotation='vertical',horizontalalignment='left',verticalalignment="center")

        	if(row == nrows-1 and col_headings):
                    fig.text(row_heading+(col*(pwidth+hpadding))+pwidth/2.,
                             colourbar+cbarbuffer+vpadding+(row*(pheight+vpadding))+pheight,
                             col_headings[col],
                             size=rowcolfsize,
                             rotation='horizontal',
                             horizontalalignment='center')

                plt.title(img_headings[row][col],size=14)
            
	    else:
		
		if(row == nrows-1 and col_headings):
        	    plt.title(col_headings[col],size=18)

        	if(col == 0 and row_headings):
                    if inline_row_headings:
                        plt.title(row_headings[row],size=14)
                    else:
                        plt.ylabel(row_headings[row],size=18)
	    
	    
            # Draw the gridlines #
	    
	    if(draw_axis):
                labels=[0,0,0,0]

                if(col == ncols-1):
                    labels[1] = 1
                if (row == 0):
                    labels[3]=1

                #draw parallels
                if delat: 
                    circles = numpy.arange(minlat,maxlat,delat).tolist()
                    map.drawparallels(circles,labels=labels,fontsize=8,linewidth=0.5)
		    if equator==True:
		        map.drawparallels([0],dashes=[5,2],linewidth=0.4)

                #draw meridians
                if delon:
                    meridians = numpy.arange(minlon,maxlon,delon)
                    map.drawmeridians(meridians,labels=labels,fontsize=8,linewidth=0.5)
            
            if enso:
	        if projection == 'cyl':
		    E125,E145,E160,E165,E180,W180,W170,W150,W140,W120,W110,W90,W80,W70=[125,145,160,165,180,180,190,210,220,240,250,270,280,290]
		else:
		    E125,E145,E160,E165,E180,W180,W170,W150,W140,W120,W110,W90,W80,W70=[125,145,160,165,180,-180,-170,-150,-140,-120,-110,-90,-80,-70]

		#IEMI-A
		map.plot([W180,W140],[-10,-10],linestyle='-',color='0.5')   #bottom
		map.plot([E165,E180],[-10,-10],linestyle='-',color='0.5')
		map.plot([W180,W140],[10,10],linestyle='-',color='0.5')     #top
		map.plot([E165,E180],[10,10],linestyle='-',color='0.5')	
		map.plot([E165,E165],[-10,10],linestyle='-',color='0.5')    #right
		map.plot([W140,W140],[-10,10],linestyle='-',color='0.5')    #left
                #IEMI-B
                map.plot([W70,W110],[-15,-15],linestyle='-',color='0.5')    #bottom
		map.plot([W70,W110],[5,5],linestyle='-',color='0.5')        #top
		map.plot([W70,W70],[-15,5],linestyle='-',color='0.5')       #right
		map.plot([W110,W110],[-15,5],linestyle='-',color='0.5')     #left
	        #IEMI-C
                map.plot([E125,E145],[-10,-10],linestyle='-',color='0.5')   #bottom
		map.plot([E125,E145],[20,20],linestyle='-',color='0.5')     #top
		map.plot([E125,E125],[-10,20],linestyle='-',color='0.5')    #right
		map.plot([E145,E145],[-10,20],linestyle='-',color='0.5')    #left
		#nino4
                map.plot([E160,E180],[-5,-5],linestyle='--',color='green',lw=1)   #bottom
		map.plot([W180,W150],[-5,-5],linestyle='--',color='green',lw=1)
		map.plot([E160,E180],[5,5],linestyle='--',color='green',lw=1)     #top
		map.plot([W180,W150],[5,5],linestyle='--',color='green',lw=1)
		map.plot([E160,E160],[-5,5],linestyle='--',color='green',lw=1)    #right
		map.plot([W150,W150],[-5,5],linestyle='--',color='green',lw=1)    #left
		#nino3.4
                map.plot([W120,W170],[-5,-5],linestyle='-',color='orange',lw=1)  #bottom
		map.plot([W120,W170],[5,5],linestyle='-',color='orange',lw=1)    #top
		map.plot([W120,W120],[-5,5],linestyle='-',color='orange',lw=1)   #right
		map.plot([W170,W170],[-5,5],linestyle='-',color='orange',lw=1)   #left
		#nino3
                map.plot([W90,W150],[-5,-5],linestyle='--',color='aqua',lw=1)     #bottom
		map.plot([W90,W150],[5,5],linestyle='--',color='aqua',lw=1)       #top
		map.plot([W90,W90],[-5,5],linestyle='--',color='aqua',lw=1)       #right
		map.plot([W150,W150],[-5,5],linestyle='--',color='aqua',lw=1)     #left
		#nino1+2
                map.plot([W80,W90],[-10,-10],linestyle='--',color='0.5',lw=1)     #bottom
		map.plot([W80,W90],[0,0],linestyle='--',color='0.5',lw=1)         #top
		map.plot([W80,W80],[-10,0],linestyle='--',color='0.5',lw=1)       #right
		map.plot([W90,W90],[-10,0],linestyle='--',color='0.5',lw=1)       #left


    ## Plot the colour bar ##
    
    cax = plt.axes([0.15,vpadding*2,0.7,colourbar])
    plt.xticks(fontsize=12)

    cb = plt.colorbar(mappable=im,cax=cax,orientation='horizontal',ticks=ticks,extend=extend,format='%.'+str(dec)+'f') # draw colorbar
    if units:
        cb.set_label(units)

#    plt.axes(ax)  # make the original axes current again
    
    if ofile:
        plt.savefig(ofile)#,dpi=300)
    else:
	plt.savefig('test.png')
	#plt.show()


def reshape_list(input_list,dimensions):
    """Reshapes a list according to the matrix dimensions"""
    if input_list:
	correct_format_list = numpy.array(str2list(input_list))
	output_list = numpy.reshape(correct_format_list,(dimensions))
    else:
	output_list = input_list

    return output_list


def extract_data(file_list,variable_list,row,col,timmean=None,region=None,convert=False,scale=False):
    """Extracts data from the file"""
   
    fin = cdms2.open(file_list[row,col],'r')
    if timmean and region:
	tVar = fin(variable_list[row,col],region,time=(timmean[0],timmean[1]),squeeze=1)
    elif timmean: 
        tVar = fin(variable_list[row,col],time=(timmean[0],timmean[1]),squeeze=1)
    elif region:
        tVar = fin(variable_list[row,col],region,squeeze=1)
    else:
	tVar = fin(variable_list[row,col],squeeze=1)
    
    tVar_lon = tVar.getLongitude()[:]
    tVar_lat = tVar.getLatitude()[:]

    #Unit conversion
    if convert:
	if tVar.units == 'kg m-2 s-1' and units[0] == 'm':
	    tVar = tVar*86400
	if tVar.units[0] == 'K' and units[0] == 'C' and ma.max(tVar) > 70.0:
	    tVar = tVar - 273.16

    #Apply scale factor
    if scale:
	tVar = tVar*scale

    #Data must be two dimensional 
    if (re.match('^t',tVar.getOrder())):
	print "WARNING data has a time axis, results displayed will be the temporal average"
        #tVar = tVar[0,:,:]
        tVar = numpy.mean(tVar,axis=0)

    fin.close()

    return tVar,tVar_lon,tVar_lat
    

def decimal_places(diff):
    """Determines the decimal place rounding for a given difference between min and max ticks"""
    
    if diff > 100.0:
        dec = 0
    elif diff > 5.0:
        dec = 1
    else:
        dec = math.floor(math.fabs(math.log10(diff)) + 2)
    
    return int(dec)


def get_min_max(files,variables,timmean,region,plot='primary'):

    min_level = 1.0e20
    max_level = -1.0e20

    #rows/cols
    nrows = len(files[:,0])
    ncols = len(files[0,:])

    #Check Files
    for row in range(nrows):
        for col in range(ncols):

            ifile = files[row][col]
            var = variables[row][col]
            fin = cdms2.open(ifile,'r')

            tVar = extract_data(files,variables,row,col,timmean=timmean,region=region)[0]
	    tmax = tVar.max()
            tmin = tVar.min()
            if tmax > max_level:
                max_level = tmax

            if tmin < min_level:
                min_level = tmin

            fin.close()

    print plot, 'plot'
    print 'Minimum value = ',min_level
    print 'Maximum value = ',max_level
    
    #For ranges that straddle zero, make magnitude of min and max equal
    if max_level > 0 and min_level < 0:
        if abs(max_level) > abs(min_level):
	    min_level = -1 * max_level
	else:
	    max_level = abs(min_level)
        
    
    return min_level,max_level


def generate_colourmap(colourmap, nsegs):
    """Returns a discrete colormap from the continuous colormap (cmap),
       according to the number of segments (nsegs)"""
        
    segs = []
    for i in range(0,nsegs):
	c = colourmap(float(float(i)/float(nsegs)),1)
	segs.append(c)
    colourmap = matplotlib.colors.ListedColormap(segs[:], 'indexed')
    
    return colourmap


def str2list(s):
    if(isinstance(s,basestring)):
        if(s.count(' ')):
            s = s.split(' ')
        elif(s.count(',')):
            s = s.split(',')
        else:
            s = [s]

    return s


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


if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("--dimensions",dest="dimensions",type='int',nargs=2,default=None,help="Matrix dimensions (two arguments - rows columns) [default=None]")
    parser.add_option("--title",dest="title",type='string',default=None,help="plot title [default = None]")
    parser.add_option("--ofile",dest="ofile",type='string',default=None,help="name of output file [default = test.png]")
    parser.add_option("--contour",action="store_true",dest="contour",default=False,help="Switch for drawing contour plot [default = False]")
    parser.add_option("--timmean",dest="timmean",default=None,nargs=2,type='str',help="Period over which to calculate time mean [default = entire time period]")
    #Map details
    parser.add_option("--region",dest="region",type='string',default='WORLD_DATELINE',help="name of region to plot [default = WORLD_DATELINE]")
    parser.add_option("--minlat", dest="minlat",type='float',default=None,help="Minimum latitude [defualt = none]")
    parser.add_option("--minlon", dest="minlon",type='float',default=None,help="Minimum longitude [defualt = none]")
    parser.add_option("--maxlat", dest="maxlat",type='float',default=None,help="Maximun latitude [defualt = none]")
    parser.add_option("--maxlon", dest="maxlon",type='float',default=None,help="Maximum longitude [defualt = none]")
    parser.add_option("--latX", dest="latX",type='float',default=-20.,help="Latitude centre point of map projection [defualt = -20]")
    parser.add_option("--lonX", dest="lonX",type='float',default=-125.,help="Longitude centre point of map projection [defualt = -125]")
    parser.add_option("--resolution", dest="resolution",type='string',default='c',help="Resolution of the background map [default='l']")
    parser.add_option("--area_threshold", dest="area_threshold",type='float',default=1.,help="Threshold (in km) for the smallest resolved feature [default = 1]")	
    parser.add_option("--draw_axis",action="store_true",dest="draw_axis",default=False,help="Switch for drawing lat/lon gridlines on plot [default = False]")
    parser.add_option("--delat", dest="delat",type='float',default=30.,help="Interval between meridional gridlines [default = 30]")
    parser.add_option("--delon", dest="delon",type='float',default=30.,help="Interval between zonal gridlines [default = 30]")
    parser.add_option("--equator",action="store_true",dest="equator",default=False,help="Switch for drawing an extra grid line marking the equator [default = False]")
    parser.add_option("--enso",action="store_true",dest="enso",default=False,help="Switch for drawing an extra grid lines marking ENSO regions [default = False]")
    parser.add_option("--image_size", dest="image_size",type='float',default=6.,help="Size of image [default = 6]")
    parser.add_option("--projection",dest="projection",type='string',default='cyl',help="map projection [default = cyl]")
    #Colourbar
    parser.add_option("--colourbar_colour", dest="colourbar_colour",type='string',default='jet',help="Colourbar name [defualt = jet]")
    parser.add_option("--units", dest="units",type='string',default=None,help="Units")
    parser.add_option("--ticks", dest="ticks",type='string',default=None,help="List of comma seperataed tick marks to appear on the colour bar")
    parser.add_option("--discrete_segments", dest="discrete_segments",type='string',default=None,help="List of comma seperated colours to appear on the colour bar")
    parser.add_option("--convert",action="store_true",dest="convert",default=False,help="Unit converstion [default = False]")
    parser.add_option("--scale", dest="scale",type='float',default=None,help="Scale (or multiplication) factor [defualt = None]")
    parser.add_option("--extend", dest="extend",type='string',default='neither',help="Selector for arrow points at either end of colourbar [default = 'neither']")
    #Contours
    parser.add_option("--draw_contours",action="store_true",dest="draw_contours",default=False,help="Switch for drawing contours on the plot [default = False]")
    parser.add_option("--contour_files", dest="contour_files",type='string',default=None,help="List of input contour files")
    parser.add_option("--contour_variables", dest="contour_variables",type='string',default=None,help="List of input contour variables")
    parser.add_option("--contour_ticks", dest="contour_ticks",type='string',default=None,help="List of comma seperataed tick marks, or just the number of contour lines")
    parser.add_option("--contour_scale", dest="contour_scale",type='float',default=None,help="Scale (or multiplication) factor for contour data [defualt = None]")
    #Wind
    parser.add_option("--draw_vectors",action="store_true",dest="draw_vectors",default=False,help="Switch for drawing wind vectors on the plot [default = False]")
    parser.add_option("--vector_type", dest="vector_type",type='string',default='wind',help="Type of vector being plotted [defualt = wind]")
    parser.add_option("--uwnd_files", dest="uwnd_files",type='string',default=None,help="List of input zonal wind files")
    parser.add_option("--uwnd_variables", dest="uwnd_variables",type='string',default=None,help="List of input zonal wind variables")
    parser.add_option("--vwnd_files", dest="vwnd_files",type='string',default=None,help="List of input zonal wind files")
    parser.add_option("--vwnd_variables", dest="vwnd_variables",type='string',default=None,help="List of input zonal wind variables")
    parser.add_option("--thin", dest="thin",type='int',default=1,help="Thinning factor for plotting wind vectors [defualt = 1]")
    parser.add_option("--key_value", dest="key_value",type='float',default=1.0,help="Size of the wind vector in the key (plot is not scaled to this) [defualt = 1]")
    parser.add_option("--quiver_scale",dest="quiver_scale",type='float',default=170,help="Data units per arrow length unit (smaller means longer arrow) [defualt = 170]")
    parser.add_option("--quiver_width",dest="quiver_width",type='float',default=0.0015,help="Shaft width in arrow units [default = 0.0015, i.e. 0.0015 times the width of the plot]")
    parser.add_option("--quiver_headwidth",dest="quiver_headwidth",type='float',default=3.5,help="Head width as multiple of shaft width [default = 3.5]")
    parser.add_option("--quiver_headlength",dest="quiver_headlength",type='float',default=4.0,help="Head length as multiple of shaft width [default = 4.0]")
    #Stippling
    parser.add_option("--draw_stippling",action="store_true",dest="draw_stippling",default=False,help="Switch for drawing stippling on the plot [default = False]")
    parser.add_option("--stipple_files", dest="stipple_files",type='string',default=None,help="List of input stippling files")
    parser.add_option("--stipple_variables", dest="stipple_variables",type='string',default=None,help="List of input stippling variables")
    #Headings
    parser.add_option("--row_headings", dest="row_headings",type='string',default=None,help="List of comma seperated row headings")
    parser.add_option("--inline_row_headings", dest="inline_row_headings",type='string',default=None,help="List of comma seperated inline row headings")
    parser.add_option("--col_headings", dest="col_headings",type='string',default=None,help="List of comma seperated column headings")
    parser.add_option("--img_headings", dest="img_headings",type='string',default=None,help="List of comma seperated image headings")
    parser.add_option("--textsize", dest="textsize",type='float',default=18.,help="Size of the column and row headings")
    
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            python plot_map.py [-M] [-h] [options] {ifile1,ifile2,...} {variable1,variable2,...}

	General Options
            -M  -> Display this on-line manual page and exit
            -h  -> Display a help/usage message and exit
        	    		
	Options for the multiplot function
            ifiles                List of comma separated input files, in an order such that positions in the matrix start bottom left and fill row by row [required] 
            variables             List of comma seperated variable names corresponding to the input files [required]
            --dimensions          Matrix dimensions (two arguments - rows columns) [default=None]
            --ofile               Name of output file [default = test.png]
            --title               Title of plot [default = None]
	    --timmean             Period over which to calculate time mean [default = entire time period]
	    --region              Selector defining a region (for cylindrical projection). Inbuilt regions are WORLD_GRENEWICH, WORLD_DATELINE, AUSTRALIA, AUS_NZ [default = WORLD_DATELINE]
            --minlat              User can override the pre-defined region by specifying bounds
            --minlon              " "
            --maxlat              " "
            --maxlon              " " 
	    --latX                Latitude centre point of map projection (for near-sided perspective projection) [default = -25]
	    --lonX                Longitude centre point of map projection (for near-sided perspective projection) [default = -120]
	    --projection          Map projection. Inbuilt options are equidistant cylindrical ('cyl') and near-sided perspective ('nsper') [default = cyl]
            --colourbar_colour    Selector defining a matplotlib colorbar (e.g. 'jet','jet_r','hot','Blues') [default = 'jet']
            --units               Units of the data - appears as a label below the colourbar
            --ticks               List of comma seperataed tick marks to appear on the colour bar
            --discrete_segments   List of comma seperated hexadecimal segment colours (e.g. #FF0B0B,#D5BA00,...) to appear on the colour bar
                                  (this will override colourbar_colour and there must be one less discrete segment than number of ticks), OR
				  A single integer specifing how many segments you want (the program will figure out the rest)
            --convert             Selector for automatic unit conversion (it will convert 'kg m-2 s-1' to 'mm day-1' or 'K' to 'C')
	    --scale               Scale (or multiplication) factor for input data [default = None]
            --extend              Selector for arrow points at either end of colourbar. Can be 'both', 'neither, 'min' or 'max' [default = 'neither']
            --resolution          Resolution of the background map. Can be 'h' (high), 'm' (medium), 'l' (low) or 'c' (coarse) [default='l']
            --area_threshold      Threshold (in km) for the smallest resolved feature on the background map [default = 1]
	    --draw_contours       Switch for drawing contours on the plot [default = False]
            --contour_files       List of input contour files, in an order such that positions in the matrix start bottom left and fill row by row [defualt = None]
            --contour_variables   List of comma seperated variable names corresponding to the input contour files [default = None] 
            --contour_ticks       List of comma seperataed tick marks, or just the number of contour lines
            --contour_scale       Scale (or multiplication) factor for contour data [default = None]
	    --draw_vectors        Switch for drawing wind vectors on the plot [default = False]
            --vector_type         Type of vector being plotted (determines units for quiver key). Can be 'wind' or 'waf' (wave activity flux) [default = 'wind']
	    --uwnd_files          List of input zonal surface wind files, in an order such that positions in the matrix start bottom left and fill row by row [defualt = None]
            --uwnd_variables      List of comma seperated variable names corresponding to the input zonal surface wind files [default = None] 
            --vwnd_files          List of input meridional surface wind files, in an order such that positions in the matrix start bottom left and fill row by row [defualt = None]
            --vwnd_variables      List of comma seperated variable names corresponding to the input meridional surface wind files [default = None] 
	    --thin                Thinning factor for plotting wind vectors (e.g. 2 = every second vector; 3 = every third) [default = 1]
            --key_value           Magnitude of the vector shown in the legend (plot vectors are not scaled to this) [default = 1]
	    --quiver_scale        Data units per arrow length unit, e.g. m/s per plot width; a smaller scale parameter makes the arrow longer. If None, autoscaling algorithm used [default = 170]
	    --quiver_width        Shaft width in arrow units [default = 0.0015, i.e. 0.0015 times the width of the plot]
	    --quiver_headwidth    Head width as multiple of shaft width [default = 3.5]
	    --quiver_headlength   Head length as multiple of shaft width [default = 4.0]
	    --draw_stippling      Switch for drawing stippling on the plot [default = False]
            --stipple_files       List of input stippling files, in an order such that positions in the matrix start bottom left and fill row by row [defualt = None]
            --stipple_variables   List of comma seperated variable names corresponding to the input stippling files [default = None] 
            --row_headings        List of comma seperated row headings (order bottom to top) [default = None]
	    --inline_row_headings List of comma seperated inline row headings for each individual plot, in an order such that positions in the matrix start bottom left and fill row by row [defualt = None] 
            --col_headings        List of comma seperated column headings (order left to right) [default = None]
            --img_headings        List of comma seperated headings for each individual plot, in an order such that positions in the matrix start bottom left and fill row by row [defualt = None]
            --draw_axis           Switch for drawing lat/lon gridlines on plot [default = False]
            --delat               Interval (in degrees latitude) between meridional gridlines [default = 30]
            --delon               Interval (in degrees longitude) between zonal gridlines [default = 30]
            --equator             Switch for drawing an extra grid line marking the equator [default = False]
	    --enso                Switch for drawing an extra grid line marking enso regions [default = False]
            --contour             Switch for drawing a contour plot [default = False, which simply fills each grid cell with the appropriate shading]
            --image_size          Width of individual images (in inches) [default = 6]
	    --textsize            Size of the row and column headers [default = 18]

	Environment
	    abyss.earthsci.unimelb.edu.au
	        /opt/cdat/bin/cdat
	    dcc.nci.org.au
                module use /projects/r87/public/modulefiles;
		module load python/2.7.1 python-cdat-lite/6.0rc2-py2.7 python-basemap/0.99.4-py2.7
		module load cct
	    cherax
	        module load opendap;
                module load python/2.5.1;
                export PYTHONPATH=/tools/cdat/5.0.0/lib/python2.5/site-packages/;
                export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tools/cdat/5.0.0/Externals/lib

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    else:
    
	file_list = [str(s) for s in args[0].split(',')]
	var_list = [str(s) for s in args[1].split(',')]
        

	multiplot(file_list,var_list,
        	  dimensions=options.dimensions,
		  ofile=options.ofile,title=options.title,timmean=options.timmean,
		  region=options.region,minlat=options.minlat,minlon=options.minlon,maxlat=options.maxlat,maxlon=options.maxlon,latX=options.latX,lonX=options.lonX,projection=options.projection,
        	  colourbar_colour=options.colourbar_colour,ticks=unpack_comma_list(options.ticks,'float'),discrete_segments=unpack_comma_list(options.discrete_segments),
		  units=options.units,convert=options.convert,scale=options.scale,extend=options.extend,
        	  res=options.resolution,area_threshold=options.area_threshold,
		  draw_contours=options.draw_contours,contour_files=unpack_comma_list(options.contour_files),contour_variables=unpack_comma_list(options.contour_variables),
		  contour_ticks=unpack_comma_list(options.contour_ticks,'float'),contour_scale=options.contour_scale,
		  draw_vectors=options.draw_vectors,vector_type=options.vector_type,uwnd_files=unpack_comma_list(options.uwnd_files),uwnd_variables=unpack_comma_list(options.uwnd_variables),
		  vwnd_files=unpack_comma_list(options.vwnd_files),vwnd_variables=unpack_comma_list(options.vwnd_variables),thin=options.thin,key_value=options.key_value,
		  quiver_scale=options.quiver_scale,quiver_width=options.quiver_width,quiver_headwidth=options.quiver_headwidth,quiver_headlength=options.quiver_headlength,
		  draw_stippling=options.draw_stippling,stipple_files=unpack_comma_list(options.stipple_files),stipple_variables=unpack_comma_list(options.stipple_variables),
        	  row_headings=unpack_comma_list(options.row_headings),inline_row_headings=unpack_comma_list(options.inline_row_headings),
        	  col_headings=unpack_comma_list(options.col_headings),img_headings=unpack_comma_list(options.img_headings),
        	  draw_axis=options.draw_axis,delat=options.delat,delon=options.delon,equator=options.equator,enso=options.enso,
		  contour=options.contour,
        	  image_size=options.image_size,
		  textsize=options.textsize)

