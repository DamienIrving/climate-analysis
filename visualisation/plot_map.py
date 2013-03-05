
"""
Filename:     plot_map.py
Description:  Creates a spatial plot     

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

"""

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

import argparse
import re
import sys
import os
from datetime import datetime

import pylab

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as ni


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



def set_colourbar(colourbar_colour, ticks, discrete_segments, extend):
    """Set the colourbar."""

    #Make sure discrete_segments is in the correct format
    if isinstance(discrete_segments, list):
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
    
    if isinstance(discrete_segments, list):
	if discrete_segments[0] in globals():
            for i in range(0, len(discrete_segments)):
		discrete_segments[i] = globals()[discrete_segments[i]]

    if isinstance(discrete_segments, list):
        if len(discrete_segments) != (len(ticks)-1):
	    print 'Number of input colour segments does not match number of ticks - check extension setting'
	    sys.exit(1)
	colourmap = matplotlib.colors.ListedColormap(discrete_segments[:], 'indexed')
    elif discrete_segments:
        if discrete_segments != (len(ticks)-1):
	    print 'Number of input colour segments does not match number of ticks - check extension setting'
	    sys.exit(1)
	colourmap = generate_colourmap(colourmap, discrete_segments)
    elif not continuous_colourbar:
	colourmap = generate_colourmap(colourmap, len(ticks))        
	
    #Remove added elements as we dont wont these displayed
    if extend == 'both':
        ticks = ticks[1:-1]
    
    if extend == 'max':
        ticks = ticks[0:-1]

    if extend == 'min':
        ticks = ticks[1:]
    
    return ticks, colourmap

    
def define_contour_ticks(contour_files, contour_ticks)
    """Set contour ticks."""

    if contour_ticks == None:
        contour_min_level, contour_max_level = get_min_max(contour_files, plot='contour')
	contour_diff = contour_max_level - contour_min_level
	contour_step = contour_diff/10.0

	contour_ticks = list(numpy.arange(contour_min_level, contour_max_level+(contour_step/2), contour_step))
        if contour_max_level > 0 and contour_min_level < 0:
	    contour_ticks[5] = 0.0
    else:
	contour_min_level, contour_max_level = [contour_ticks[0], contour_ticks[-1]]

    contour_dec = decimal_places(contour_max_level - contour_min_level)

    return contour_dec


def set_image_size(image_size, region, row_headings, inline_row_headings, img_headings)
    """Set all parameters related to image size."""

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

    return width, height, title_pos


def multiplot(indata,
              #Variables below here are optional, should give a reasonable image by default
              nrows=1, ncols=len(indata),
              #Output file name and title
              ofile=None, title=None,
              #can use a pre-defined region or override with min/max lat/lon, 
              region=WORLD_DATELINE, corners=None, centre=(-55, -125), projection='cyl',
              #colourbar settings
              colourbar_colour='jet', ticks=None, discrete_segments=None, units=None, convert=False, extend="neither",
              #resolution of image
              res='l', area_threshold=1.,
	      #contours
	      contour_data=None, contour_ticks=None,
	      #wind vectors
	      uwnd_data=None, vwnd_data=None, vector_type='wind', thin=1, key_value=1,
	      quiver_scale=170, quiver_width=0.0015, quiver_headwidth=3.5, quiver_headlength=4.0,
	      #stippling
	      stipple_data=None,
              #Headings if using mutiple plots in a single plot
              row_headings=None, inline_row_headings=False, col_headings=None, img_headings=None,
              #Axis options to draw lat/lon lines
              draw_axis=False, delat=30, delon=30, equator=False, enso=False,
	      #contour plot
	      contour=False,
              #Width of image in inches (individual image)
              #so single imgage would be 6 inches wide or image with two columns would be 12 inches wide etc.)
              image_size=6,
	      textsize=18):

    """Takes all the input arguments and determines the correct call to matrixplot"""


    # Perform initial checks #
 
    assert projection in ['cyl', 'nsper'], \
    'Map projection must be cylindrical (cyl) or near sided perspective (nsper)'

    assert vector_type in ['wind', 'waf'], \
    'Quiver type must me wind or wave activity flux (waf)' 

    for item in ['contour_data', 'uwnd_data', 'vwnd_data', 'stipple_data', 'img_headings']:
	if eval(item):
            if not (numpy.shape(indata) == numpy.shape(eval(item)):
                print "ERROR input data and %s are different sizes"  %(item)
                sys.exit()

    if(row_headings):
        row_headings = str2list(row_headings)
        if not (len(row_headings) == nrows):
            print "Error row headings do not match number of rows, ",
            print "there are %s rows and %s headings" % (nrows, len(row_headings))
            sys.exit(1)

    if(col_headings):
        col_headings = str2list(col_headings)
        if not (len(col_headings) == ncols):
            print "Error column headings do not match number of columns, ",
            print "there are %s columns and %s headings" % (ncols, len(col_headings))
            sys.exit(1)

    if ofile:
        if os.path.exists(ofile):
            print "WARNING replacing output file '%s'" % ofile


    # Define colourbar and contour ticks #

    ticks, colourmap = set_colourbar(colourbar_colour, ticks, discrete_segments, extend)
    if contour_data:
        contour_ticks = set_contour_ticks(contour_data, contour_ticks)

    
    # Determine image size #

    width, height, title_pos = set_image_size(image_size, region, row_headings, inline_row_headings, img_headings, )


    # Create the plot, one thumbnail at a time #

    fig=plt.figure(figsize=(width, height))
    if title:
        fig.suptitle(title.replace('_',' '), y=(1-titlepos), size=16)

    for row in range(nrows):
        for col in range(ncols):
	
            # Open file and extract data #

            if indata[row, col] == '':
                print "WARNING skipping position '(%s,%s)'" % (row, col)
                continue

	    data = indata[row, col]
            data_lon = data.getLongitude()[:]
            data_lat = data.getLatitude()[:]
	   
	    # Plot the axes and map #
	    
	    if projection == 'cyl':
		map = Basemap(llcrnrlon=minlon, llcrnrlat=minlat, urcrnrlon=maxlon, urcrnrlat=maxlat,\
                              resolution=res, area_thresh=area_threshold, projection='cyl')
		#data, data_lon = shiftgrid(0., data, data_lon, start=True)
            elif projection == 'nsper':
	        h = 3000000  #height of satellite
		map = Basemap(projection='nsper', lon_0=centre[0], lat_0=centre[1], satellite_height=h*1000., 
                              resolution=res, area_thresh=area_threshold)
		data, data_lon = shiftgrid(180., data, data_lon, start=False)
	    else:
	        print 'Map projection not recognised'
		sys.exit(0)
		
            # Setup axis and draw figure #

            xres = 100
            yres = 100
            ax = fig.add_axes([row_heading+(col*(pwidth+hpadding)),colourbar+cbarbuffer+(row*(pheight+vpadding)),pwidth,pheight]) 
            
            #is transform scalar needed?????????	    
            datout = map.transform_scalar(data, 
                                          data_lon[:],
                                          data_lat[:],
                                          xres, yres,
                                          order=0)
					  
            # Plot the primary data (i.e. the data that uses the colourbar) #
	                
	    if contour: 
	        x, y = map(*numpy.meshgrid(data_lon, data_lat))
		im = map.contourf(x, y, data, ticks, cmap=colourmap, extend=extend)
	    else:	
		im = map.imshow(datout, colourmap, vmin=min_level, vmax=max_level)
	    
            map.drawcoastlines()

            # Plot the secondary data #
    
            if contour_data:
		cont_data = contour_data[row, col]
                cont_lon = cont_data.getLongitude()[:]
                cont_lat = cont_data.getLatitude()[:] 

		if projection == 'nsper':
		    cont_data, cont_lon = shiftgrid(180., cont_data, cont_lon, start=False)
		    
		x, y = map(*numpy.meshgrid(cont_lon, cont_lat))
		im2 = map.contour(x, y, cont_data, contour_ticks, colors='k')
		plt.clabel(im2, fontsize=5, inline=1, fmt='%.'+str(contour_dec)+'f')      #fmt='%1.1f'  #levels[1::2] for label every second level
	    
	        #thicken the zero contour
		try:
		    index = contour_ticks.index(0)
		    zc = im2.collections[index]
                    plt.setp(zc, linewidth=1.5)
	        except ValueError:
		    print 'no zero contour'
	  
	    if uwnd_data and vwnd_data:
		u_data = uwnd_data[row, col]
                u_lon = u_data.getLongitude()[:]
                u_lat = u_data.getLatitude()[:]
	
		v_data = vwnd_data[row, col]
                v_lon = v_data.getLongitude()[:]
                v_lat = v_data.getLatitude()[:]
                
		if projection == 'nsper':
		    u_data, u_lon = shiftgrid(180., u_data, u_lon, start=False)
		    v_data, v_lon = shiftgrid(180., v_data, v_lon, start=False)
		
        	x, y = map(*numpy.meshgrid(u_lon, u_lat))
        	t = int(thin)
		Q = map.quiver(x[::t,::t], y[::t,::t], 
                               u_data[::t,::t], v_data[::t,::t],
                               units='height',scale=quiver_scale,
		               width=quiver_width, headwidth=quiver_headwidth,
                               headlength=quiver_headlength)
		
		if vector_type == 'wind':
		    key_units = 'm\, s^{-1}'
		elif vector_type == 'waf':   # wave activity flux
		    key_units = 'm^{2}\, s^{-2}'
		else:
		    print 'Vector type not recognised'
		    sys.exit(0)
		
		qk = pylab.quiverkey(Q, 0.9, 0.95, key_value, 
                                     r'$%s\; %s$' %(key_value, key_units), 
                                     labelpos='E', coordinates='figure',
                                     fontproperties={'weight': 'bold'})
	    
	    if stipple_data:
	        stip_data = stipple_data[row, col]
                stip_lon = stip_data.getLongitude()
                stip_lat = stip_data.getLatitude()
		
		if projection == 'nsper':
		    stip_data, stip_lon = shiftgrid(180., stip_data, stip_lon, start=False)
				            
		for iy, lat in enumerate(stip_lat[:]):
        	    for ix, lon in enumerate(stip_lon[:]):
                        agreement = stipple_data[iy, ix]
			x,y = map(*numpy.meshgrid(numpy.array([lon]), numpy.array([lat])))
			if agreement == 1:
	                    map.plot(x, y, marker='o', markersize=2.0, markerfacecolor='black', 
                                     markeredgecolor='black', markeredgewidth=0.2) 
	                elif agreement == 2:
	                    map.plot(x, y, marker='o', markersize=2.0, markerfacecolor='red',
                                     markeredgecolor='red', markeredgewidth=0.2)  
			elif agreement == 10:
	                    map.plot(x, y, marker=7, markersize=3.0, markeredgewidth=0.6,
                                     markerfacecolor='black',markeredgecolor='black') 
			elif agreement == 20:
	                    map.plot(x, y, marker=7, markersize=3.0, markeredgewidth=0.6,
                                     markerfacecolor='red',markeredgecolor='red')
	   
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
    
    cax = plt.axes([0.15, vpadding*2, 0.7, colourbar])
    plt.xticks(fontsize=12)

    cb = plt.colorbar(mappable=im, cax=cax, orientation='horizontal', ticks=ticks, extend=extend, format='%.'+str(dec)+'f') # draw colorbar
    if units:
        cb.set_label(units)

#    plt.axes(ax)  # make the original axes current again
    
    if ofile:
        plt.savefig(ofile)#,dpi=300)
    else:
	plt.savefig('test.png')
	#plt.show()gene
    

def decimal_places(diff):
    """Determines the decimal place rounding for a given difference between min and max ticks"""
    
    if diff > 100.0:
        dec = 0
    elif diff > 5.0:
        dec = 1
    else:
        dec = math.floor(math.fabs(math.log10(diff)) + 2)
    
    return int(dec)


def get_min_max(files, plot='primary'):
    """Set the minimun and maximum value."""

    min_level = float("inf")
    max_level = float("-inf")

    #rows/cols
    nrows = len(files[:,0])
    ncols = len(files[0,:])

    #Check Files
    for row in range(nrows):
        for col in range(ncols):
            data = files[row][col]
	    if data == '':
	        continue
		
            max_level, min_level = nio.hi_lo(data, max_level, min_level)


    print plot, 'plot'
    print 'Minimum value = ',min_level
    print 'Maximum value = ',max_level
    
    #For ranges that straddle zero, make magnitude of min and max equal
    if max_level > 0 and min_level < 0:
        if abs(max_level) > abs(min_level):
	    min_level = -1 * max_level
	else:
	    max_level = abs(min_level)
        
    
    return min_level, max_level


def generate_colourmap(colourmap, nsegs):
    """Returns a discrete colormap from the continuous colormap (cmap),
       according to the number of segments (nsegs)"""
        
    segs = []
    for i in range(0,nsegs):
	c = colourmap(float(float(i)/float(nsegs)),1)
	segs.append(c)
    colourmap = matplotlib.colors.ListedColormap(segs[:], 'indexed')
    
    return colourmap


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


def shuffle(in_list, rows, cols):
    """Put the input list into the correct order for mpltools.multiplot"""

    if not inlist:
        return None

    rows=int(rows)
    cols=int(cols)
    nfiles = len(in_list)
    nblanks = int((rows*cols) - nfiles)
    start = int(1 + cols*(rows-1))

    new_list = []
    for k in range(nfiles+nblanks):
        new_list.append('')

    for i in range(nblanks):
       in_list.insert(cols-nblanks, '')

    for c in range(cols):
        for r in range(rows):
            new_list[c+(r*cols)] = in_list[start+c-(r*cols)-1]

    return new_list


def extract_data(file_list, region, rows, cols, convert=False):
    """Create list of nio.InputData.data instances and 
    shuffle into correct order for plotting."""

    if not file_list:
        return None

    new_list = []
    for item in file_list:
        fname = item[0]
        var = item[1]
        period = (item[2], item[3])
        data = nio.InputData(fname, var, time=period, region=region, convert=convert).data
       
        #Data must be two dimensional 
        if (re.match('^t', data.getOrder())):
	    print "WARNING data has a time axis, results displayed will be the temporal average"
            data = MV2.average(data, axis=0)

        new_list.append(data)

    return shuffle(new_list, nrows, ncols)   
    

def main(inargs):
    """Run program."""

    # Determine dimensions #

    if inargs.dimensions:
        nrows = inargs.dimensions[0]
        ncols = inargs.dimensions[1]
    else:
        nrows = 1
        ncols = len(inargs.infiles)

    # Extract data and shuffle into correct order #

    infile_data = extract_data(inargs.infiles, inargs.region, nrows, ncols, convert=inargs.convert)
    contour_data = extract_data(inargs.contour_file, inargs.region, nrows, ncols, convert=inargs.convert)
    uwnd_data = extract_data(inargs.uwnd_file, inargs.region, nrows, ncols, convert=inargs.convert)
    vwnd_data = extract_data(inargs.vwnd_file, inargs.region, nrows, ncols, convert=inargs.convert)
    stipple_data = extract_data(inargs.stipple_file, inargs.region, nrows, ncols, convert=inargs.convert)
    img_headings = shuffle(inargs.image_headings, nrows, ncols)
      
    # Generate plot #

    multiplot(infile_data, 
              nrows=nrows, ncols=ncols,
              contour_data=contour_data, 
              uwnd_data=uwnd_data,
              vwnd_data=vwnd_data,
              stipple_data=stipple_data,
              img_headings=img_headings,    
              **nio.dict_filter(vars(inargs), nio.list_kwargs(multiplot))


if __name__ == '__main__':

    extra_info="""
file order:
  List inputs in an order such that positions in the matrix start bottom left and fill row by row

improvements:
  The procedure for doing different map projections needs to be more sophisticated (i.e. it could
  first check the characteristics of the longitude axis)

"""

    description='Plot spatial map.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="input file name")
    parser.add_argument("variable", type=str, help="input file variable")
    parser.add_argument("start", type=str,
                        help="input file time start date")
    parser.add_argument("end", type=str,
                        help="input file time end date - let START=END for single time step")

    parser.add_argument("--infiles", type=str, action='append', default=[], nargs=4,
                        metavar=('FILENAME', 'VAR', 'START', 'END'),  
                        help="additional input file name, variable, start date and end date [default: None]")

    parser.add_argument("--dimensions" ,type=int, nargs=2, default=None, metavar=['ROWS', 'COLUMNS'], 
                        help="matrix dimensions [default: 1 row]")
    parser.add_argument("--title", type=str,
                        help="plot title [default: None]")
    parser.add_argument("--ofile", type=str, 
                        help="name of output file [default: test.png]")
    parser.add_argument("--contour", action="store_true",
                        help="switch for drawing contour plot [default: False]")
 
    #Map details
    parser.add_argument("--region", type=str, default='dateline', choices=nio.regions.keys(),
                        help="name of region to plot [default: dateline]")
    parser.add_argument("--centre", type=float, nargs=2, metavar=['LAT', 'LON'],
                        help="centre point of map projection")
    parser.add_argument("--resolution", type=str, choices=['h', 'm', 'l', 'c'],
                        help="resolution of the background map [default: l = low]")
    parser.add_argument("--area_threshold", type=float, 
                        help="threshold (in km) for the smallest resolved feature [default: 1]")	
    parser.add_argument("--draw_axis", action="store_true", 
                        help="switch for drawing lat/lon gridlines on plot [default: False]")
    parser.add_argument("--delat", type=float, 
                        help="interval between meridional gridlines [default: 30]")
    parser.add_argument("--delon", type=float, 
                        help="interval between zonal gridlines [default: 30]")
    parser.add_argument("--equator", action="store_true", 
                        help="switch for drawing an extra grid line marking the equator [default: False]")
    parser.add_argument("--enso", action="store_true",
                        help="switch for drawing an extra grid lines marking ENSO regions [default: False]")
    parser.add_argument("--image_size", type=float, 
                        help="size of image [default: 6]")
    parser.add_argument("--projection", type=str, choices=['cyl', 'nsper'],
                        help="map projection [default: cyl]")
 
    #Headings
    parser.add_argument("--row_headings", type=str, nargs='*',
                        help="list of row headings")
    parser.add_argument("--inline_row_headings", type=str, nargs='*', 
                        help="list of inline row headings")
    parser.add_argument("--col_headings", type=str, nargs='*', 
                        help="list of column headings")
    parser.add_argument("--image_headings", type=str, nargs='*', 
                        help="list of image headings")
    parser.add_argument("--textsize", type=float, default=18., 
                        help="size of the column and row headings")

    #Colourbar
    parser.add_argument("--colourbar_colour", type=str, choices=['jet', 'jet_r', 'hot', 'hot_r', 'Blues', 'RdBu', 'RdBu_r']
                        help="Colourbar name [defualt: jet]")
    parser.add_argument("--units", type=str, 
                        help="Units")
    parser.add_argument("--ticks", type=float, nargs='*',
                        help="list of tick marks to appear on the colour bar")
    parser.add_argument("--discrete_segments", type=str, nargs='*',
                        help="list of comma colours to appear on the colour bar")
    parser.add_argument("--convert", action="store_true", default=False,
                        help="unit converstion [default: False]")
    parser.add_argument("--extend", type=str, choices=['both', 'neither', 'min', 'max'],
                        help="selector for arrow points at either end of colourbar [default: 'neither']")
 
    #Contours
    parser.add_argument("--contour_file", type=str, nargs=4, action='append',
                        metavar=('FILENAME', 'VAR', 'START', 'END'),  
                        help="contour file name, variable, start date and end date [default: None]")
    parser.add_argument("--contour_ticks", type=float, nargs='*', 
                        help="list of tick marks, or just the number of contour lines")
 
    #Wind
    parser.add_argument("--uwnd_file", type=str, nargs=4, action='append',
                        metavar=('FILENAME', 'VAR', 'START', 'END'),  
                        help="zonal wind file name, variable, start date and end date [default: None]"))
    parser.add_argument("--vwnd_file", type=str, nargs=4, action='append',
                        metavar=('FILENAME', 'VAR', 'START', 'END'),  
                        help="zonal wind file name, variable, start date and end date [default: None]"))
    
    parser.add_argument("--vector_type", type=str, choices=['wind', 'waf'],
                        help="type of vector being plotted [defualt: wind]")
    parser.add_argument("--thin", type=int, 
                        help="thinning factor for plotting wind vectors [defualt: 1]")
    parser.add_argument("--key_value", type=float, 
                        help="size of the wind vector in the key (plot is not scaled to this) [defualt: 1]")
    parser.add_argument("--quiver_scale", type=float, 
                        help="data units per arrow length unit (smaller value means longer arrow) [defualt: 170]")
    parser.add_argument("--quiver_width", type=float,
                        help="shaft width in arrow units [default: 0.0015, i.e. 0.0015 times the width of the plot]")
    parser.add_argument("--quiver_headwidth", type=float,
                        help="head width as multiple of shaft width [default: 3.5]")
    parser.add_argument("--quiver_headlength", type=float, 
                        help="head length as multiple of shaft width [default: 4.0]")
 
    #Stippling
    parser.add_argument("--stipple_file", type=str, nargs=4, action='append',
                        metavar=('FILENAME', 'VAR', 'START', 'END'),  
                        help="stipple file name, variable, start date and end date [default: None]")) 

    
    args = parser.parse_args()              

    args.infiles.insert(0, [args.infile, args.variable, args.start, args.end])

    main(args)
