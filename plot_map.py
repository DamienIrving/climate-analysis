#!/tools/python/2.5.1/bin/python

"""
SVN INFO: $Id$
Filename:     plot_seasonal_cycle.py
Description:  Creates a spatial plot     

Input:        List of netCDF files to plot
Output:       An image in either bitmap (e.g. .png) or vector (e.g. .svg, .eps) format

"""

__version__= '$Revision$'


### Import required modules ###

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap
from scipy import interpolate
#import pylab

import numpy
import numpy.ma as ma
import cdms2
import re
import sys
import os

from cct.landsea import mask_ocean


### Define globals ###

AUSTRALIA = cdms2.selectors.Selector(latitude=(-45,-10,'cc'),longitude=(110,160,'cc'))
AUS_NZ = cdms2.selectors.Selector(latitude=(-50,0,'cc'),longitude=(100,185,'cc'))
WORLD_GREENWICH = cdms2.selectors.Selector(latitude=(-90,90,'cc'),longitude=(-180,180,'cc'))
WORLD_DATELINE = cdms2.selectors.Selector(latitude=(-90,90,'cc'),longitude=(0,360,'cc'))


### Define functions ###

def quickplot(ifile,ofile=None,variable=None):
    """Function for producing a quick plot using all default values"""
    
    if not os.path.exists(ifile):
        print "ERROR input file %s does not exists" % ifile
        sys.exit(1)

    multiplot(ifile,variable,os.path.basename(ifile))


def multiplot(ifiles,variables,title,
              #Variables below here are optional, should give a reasonable image by default
              dimensions=None,
              #Output file name default is 'title'.png
              ofile=None,
              #can use a pre-defined region or override with min/max lat/lon, 
              region=WORLD_DATELINE,minlat=None,minlon=None,maxlat=None,maxlon=None,projection='cyl'
              #colourbar settings
              colourbar_colour='jet',ticks=None,discrete_segments=None,units=None,convert=False,extend="neither",
              #resolution of image
              res='l',area_threshold=1.,
	      # wind vectors
	      draw_vectors=False,uwnd_files=None,uwnd_variables=None,vwnd_files=None,vwnd_variables=None,
	      # stippling
	      draw_stippling=False,stipple_files=None,stipple_variables=None,
              #Headings if using mutiple plots in a single plot
              row_headings=None,inline_row_headings=False,
              col_headings=None,img_headings=None,
              #Axis options to draw lat/lon lines
              draw_axis=False,delat=20,delon=40,equator=False,
	      #contour plot
	      contour=False,
              #Width of image in inches (individual image)
              #so single imgage would be 6 inches wide or image with two columns would be 12 inches wide etc.)
              image_size=6,
              maskoceans=False,
              shpoverlays=[]):

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

    ## Call matrixplot, accounting for the special cases that require additional data (i.e. wind vectors or stippling) ##

    if draw_vectors:

	uwnd_files = str2list(uwnd_files)
	uwnd_variables = str2list(uwnd_variables)

	ufile_matrix = numpy.array(uwnd_files)
	uvar_matrix = numpy.array(uwnd_variables)
	ufile_matrix = numpy.reshape(ufile_matrix,(dimensions))
	uvar_matrix = numpy.reshape(uvar_matrix,(dimensions))

	vwnd_files = str2list(vwnd_files)
	vwnd_variables = str2list(vwnd_variables)

	vfile_matrix = numpy.array(vwnd_files)
	vvar_matrix = numpy.array(vwnd_variables)
	vfile_matrix = numpy.reshape(vfile_matrix,(dimensions))
	vvar_matrix = numpy.reshape(vvar_matrix,(dimensions))

	matrixplot(file_matrix,var_matrix,title,
        	   ofile,
        	   region,minlat,minlon,maxlat,maxlon,projection,
        	   colourbar_colour,ticks,discrete_segments,units,convert,extend,
        	   res,area_threshold,
		   draw_vectors,ufile_matrix,uvar_matrix,vfile_matrix,vvar_matrix,
		   draw_stippling,stipple_files,stipple_variables,
        	   row_headings,inline_row_headings,col_headings,img_headings,
        	   draw_axis,delat,delon,equator,
		   contour,
        	   image_size,
                   maskoceans,
                   shpoverlays) 
    
    elif draw_stippling:

	stipple_files = str2list(stipple_files)
	stipple_variables = str2list(stipple_variables)

	stipfile_matrix = numpy.array(stipple_files)
	stipvar_matrix = numpy.array(stipple_variables)
	stipfile_matrix = numpy.reshape(stipfile_matrix,(dimensions))
	stipvar_matrix = numpy.reshape(stipvar_matrix,(dimensions))
	
	matrixplot(file_matrix,var_matrix,title,
        	   ofile,
        	   region,minlat,minlon,maxlat,maxlon,projection,
        	   colourbar_colour,ticks,discrete_segments,units,convert,extend,
        	   res,area_threshold,
		   draw_vectors,uwnd_files,uwnd_variables,vwnd_files,vwnd_variables,
		   draw_stippling,stipfile_matrix,stipvar_matrix,
        	   row_headings,inline_row_headings,col_headings,img_headings,
        	   draw_axis,delat,delon,equator,
		   contour,
        	   image_size,
                   maskoceans) 
	
    else:
        
	matrixplot(file_matrix,var_matrix,title,
        	   ofile,
        	   region,minlat,minlon,maxlat,maxlon,projection,
        	   colourbar_colour,ticks,discrete_segments,units,convert,extend,
        	   res,area_threshold,
		   draw_vectors,uwnd_files,uwnd_variables,vwnd_files,vwnd_variables,
		   draw_stippling,stipple_files,stipple_variables,
        	   row_headings,inline_row_headings,col_headings,img_headings,
        	   draw_axis,delat,delon,equator,
		   contour,
        	   image_size,
                   maskoceans,
                   shpoverlays) 


def matrixplot(ifiles,variables,title,
              #Variables below here are optional, should give a reasonable image by default
              #Output file name default is 'title'.png
              ofile=None,
              #can use a pre-defined region or override with min/max lat/lon, 
              region=WORLD_DATELINE,minlat=None,minlon=None,maxlat=None,maxlon=None,projection='cyl',
              #colourbar settings
              colourbar_colour='jet',ticks=None,discrete_segments=None,units=None,convert=False,extend="neither",
              #resolution of image
              res='l',area_threshold=1.,
	      # wind vectors
	      draw_vectors=False,uwnd_files=None,uwnd_variables=None,vwnd_files=None,vwnd_variables=None,
	      # stippling
	      draw_stippling=False,stipple_files=None,stipple_variables=None,
              #Headings if using mutiple plots in a single plot
              row_headings=None,inline_row_headings=False,col_headings=None,img_headings=None,
              #Axis options to draw lat/lon lines
              draw_axis=False,delat=20,delon=40,equator=False,
	      #contour plot
	      contour=False,
              #Width of image in inches (individual image)
              #so single imgage would be 6 inches wide or image with two columns would be 12 inches wide etc.)
              image_size=6,
              #Mask oceans
              maskoceans=False,
              shpoverlays=[],
              #Change text size
              textsize=18):
    """
    Takes all the input arguments and determines the correct call to matrixplot
    @param ifiles: Matrix of files to plot positions in matrix will be positions in image
    @type ifiles: Matrix of coresponding variables of file matrix
    @param variables: Matrix of coresponding variables of file matrix
    @type variables: List or str
    @param title: Title of plot
    @type title: str
    @param ofile: Path and filename of output file, default 'title'.png where title is previous variable
    @type ofile: str
    @param region: cdms.Selector defining a region, inbuilt regions are WORLD, PACIFIC, AUSTRALIA
    @type region: cdms.Selector
    @param minlat: Minimum Latitude (Overrides region param)
    @type minlat: float
    @param minlon: Minimum Longitude (Overrides region param)
    @type minlon: float
    @param maxlat: Maximum Latitude (Overrides region param)
    @type maxlat: float
    @param maxlon: Maximum Longitude (Overrides region param)
    @type maxlon: float

    @param row_headings: List of sub headings for rows
    @type row_headings: List or str
    @param col_headings: List of sub headings for columns
    @type col_headings: List or str
    """

    ## Perform initial checks ##

    #Check size of file and var matrix
    if not (ifiles.size == variables.size):
        print "ERROR file and variable matrix are different sizes"
        sys.exit()

    #rows/cols
    nrows = len(ifiles[:,0])
    ncols = len(ifiles[0,:])

    #Output file
    if not ofile:
        ofile = title + ".png"

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

    #Bounding region
    if isinstance(region, cdms2.selectors.Selector):
        for selector_component in region.components():
            if selector_component.id == 'lat':
                minlat = selector_component.spec[0]
                maxlat = selector_component.spec[1]
            elif selector_component.id == 'lon':
                minlon = selector_component.spec[0]
                maxlon = selector_component.spec[1]
    elif minlat is not None and maxlat is not None and \
         minlon is not None and maxlon is not None:
        region = cdms2.selectors.Selector(latitude=(minlat,maxlat,'cc'),longitude=(minlon,maxlon,'cc'))
    else:
        print "Error could not determine region"
        sys.exit(1)


    ## Define the colourbar ###

    #Setup colour map (unless custom which is created later)
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
	space = abs(ticks[0]-ticks[1])*0.2
    else:
        min_level,max_level = get_min_max(ifiles,variables,region)
	space = 0.1

    if extend == 'both':
        min_level = min_level - space
        max_level = max_level + space
        if ticks:
            ticks.append(max_level)
            ticks.insert(0,min_level)

    if extend == 'max':
        max_level = max_level + space
        if ticks:
            ticks.append(max_level)
	    
    if extend == 'min':
        min_level = min_level - space
        if ticks:
            ticks.insert(0,min_level)


    #Colourbar can be converted to a number of discete segments or a custom
    #colourmap can be defined forcing it to a discrete map
    
    if(discrete_segments):

        #Segments can be non-linear and are scaled to tick options if defined
        if ticks:
            if isinstance(discrete_segments,list):
                #colours = [matplotlib.colors.hex2color(seg) for seg in discrete_segments]
                #colourmap = matplotlib.colors.ListedColormap.from_list('custom', colours, N=len(ticks))
                #nSegments = len(discrete_segments)
                colourmap = custom_colourmap(discrete_segments,ticks)
            else:
                colourmap = nonlinear_colourmap(colourmap,ticks)
        else:     
            if isinstance(discrete_segments,list):
               colourmap = matplotlib.colors.ListedColormap(colors, name='custom_discrete')
               nSegments = len(discrete_segments)
            else:
                nSegments = int(discrete_segments)
                colourmap = cmap_discretize(colourmap,nSegments)

            step = (max_level - min_level)/float(nSegments)
            ticks = numpy.arange(min_level,max_level+step,step)

    #TODO make better ticks if no options selected
    elif not (ticks):
            step = (max_level - min_level)/10.0
            coloutbar_ticks = numpy.arange(min_level,max_level+step,step)

    #Remove added elements as we dont wont these displayed
    if extend == 'both':
        ticks = ticks[1:-1]
    
    if extend == 'max':
        ticks = ticks[0:-1]

    if extend == 'min':
        ticks = ticks[1:]
    
    
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


    ## Create the plot ##

    fig=plt.figure(figsize=(width,height))
    fig.suptitle(title,y=(1-titlepos),size=20)

    #for row,ifile in enumerate(ifiles):
    for row in range(nrows):
        for col in range(ncols):

            ## Print row and column headings, if there are going to be individual image headings as well
	    
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


            #Skip image if blank or set to "N/A or n/a"
            if (not os.path.exists(ifiles[row][col])) or (not variables[row,col]) or variables[row,col].lower() == "n/a" :
                if (ifiles[row][col] and ifiles[row][col].lower() != "n/a") or variables[row,col].lower() != "n/a":
                    print "WARNING skipping position '(%s,%s)' : file '%s' and variable '%s'" % (row,col,ifiles[row][col],variables[row,col])
                continue

            fin = cdms2.open(ifiles[row,col],'r')
	    tVar = fin(variables[row,col],squeeze=1)
	    fin.close()
	    
	    if draw_stippling:
	        fin_stip = cdms2.open(stipple_files[row,col],'r')
	        stipple = fin_stip(stipple_variables[row,col])
		
		mask = numpy.where(stipple == 100.0, 1, 0)
		tVar = ma.masked_array(tVar, mask=mask)
	   
	        fin_stip.close()
	    
	    
	    # Unit conversion
	    if convert:
		if tVar.units == 'kg m-2 s-1' and units[0] == 'm':
	            tVar = tVar*86400
		if tVar.units[0] == 'K' and units[0] == 'C' and ma.max(tVar) > 70.0:
	            tVar = tVar - 273.16
		
            if (re.match('^t',tVar.getOrder())):
                print "WARNING data has a time axis, results displayed will be a mean of time axis"
                tVar = tVar.mean(axis=0)
            

            map = Basemap(llcrnrlon=minlon,llcrnrlat=minlat,urcrnrlon=maxlon,urcrnrlat=maxlat,\
                          resolution=res,area_thresh=area_threshold,projection=projection)
        
            #Setup axis and draw figure
            xres = 100
            yres = 100
            ax = fig.add_axes([row_heading+(col*(pwidth+hpadding)),colourbar+cbarbuffer+(row*(pheight+vpadding)),pwidth,pheight]) 

            datout = map.transform_scalar(tVar.data, 
                                          tVar.getLongitude()[:],     #fin['latitude']
                                          tVar.getLatitude()[:],
                                          xres, yres,
                                          order=0)
					  
            if maskoceans:
                lons, lats = map.makegrid(xres, yres)
                datout = mask_ocean(datout, lats=lats[:, 0],
                                            lons=lons[0])
		im = map.imshow(datout,colourmap,vmin=min_level,vmax=max_level)
            
	    elif contour: 
	        latsq = tVar.getLatitude()
	        lonsq = tVar.getLongitude()
	        x,y = map(*numpy.meshgrid(lonsq,latsq))
	    	im = map.contourf(x,y,tVar,ticks,cmap=colourmap,extend=extend)
		
	    else:
                if draw_stippling:
		    maskout = map.transform_scalar(mask.data, 
                                          tVar.getLongitude()[:],
                                          tVar.getLatitude()[:],
                                          xres, yres,
                                          order=0)
		
		    datout_masked = ma.masked_array(datout, mask=maskout)
		
		else:
		
		    datout_masked = datout
		
		im = map.imshow(datout_masked,colourmap,vmin=min_level,vmax=max_level)
#                im = map.imshow(datout,colourmap,vmin=min_level,vmax=max_level)
	    
	    
            if not shpoverlays:
                map.drawcoastlines()

            for ishp, shpfile in enumerate(shpoverlays):
                ret = map.readshapefile(shpfile, 'shpfile%d' % ishp)
                if ret[1] == 1: # points
                    pts = getattr(map, 'shpfile%d' % ishp)
                    xs = [pt[0] for pt in pts]
                    ys = [pt[1] for pt in pts]
                    map.scatter(xs, ys)
                        

           #Image headings overrides col headings
            if img_headings is not None:
                plt.title(img_headings[row][col],size=14)
    
            if draw_vectors:
                fin = cdms2.open(uwnd_files[row,col],'r')
	        uas = fin(uwnd_variables[row,col],squeeze=1)      # region
	        fin.close()
	    
		fin = cdms2.open(vwnd_files[row,col],'r')
	        vas = fin(vwnd_variables[row,col],squeeze=1)     # region
        	fin.close()

                latsq2=uas.getLatitude()
	        latsq2.units = 'degrees_north'
		
		lonsq2=uas.getLongitude()
	        lonsq2.units = 'degrees_east'

        	x,y = map(*numpy.meshgrid(lonsq2,latsq2))
        	map.quiver(x,y,uas,vas,width=0.001,scale=650,headwidth=2,headlength=3)
	    
	    elif draw_stippling:
	        fin = cdms2.open(stipple_files[row,col],'r')
	        stipple = fin(stipple_variables[row,col],region)   #,region
	        fin.close()
	        
		latsq3=stipple.getLatitude()
	        latsq3.units = 'degrees_north'
		
		lonsq3=stipple.getLongitude()
	        lonsq3.units = 'degrees_east'
		
		ndots = numpy.sum(stipple)
		            
		for iy, lat in enumerate(latsq3[:]):
        	    for ix, lon in enumerate(lonsq3[:]):
                        agreement = stipple[iy,ix]
			if agreement == 1:
			    lons=numpy.array([lon])
			    lats=numpy.array([lat])
			    x,y = map(*numpy.meshgrid(lons,lats))
	                    map.plot(x,y,marker='o',markersize=2.0,markerfacecolor='black',markeredgecolor='black',markeredgewidth=0.2) 
	                elif agreement == 2:
			    lons=numpy.array([lon])
			    lats=numpy.array([lat])
			    x,y = map(*numpy.meshgrid(lons,lats))
	                    map.plot(x,y,marker='o',markersize=2.0,markerfacecolor='red',markeredgecolor='red',markeredgewidth=0.2)  
			elif agreement == 10:
			    lons=numpy.array([lon])
			    lats=numpy.array([lat])
			    x,y = map(*numpy.meshgrid(lons,lats))
	                    map.plot(x,y,marker=7,markersize=3.0,markeredgewidth=0.6,markerfacecolor='black',markeredgecolor='black') 
			    #map.plot(x,y,marker='x',markersize=3.5,markeredgecolor='black') # markeredgewidth=0.3,markerfacecolor='None',)
			elif agreement == 20:
			    lons=numpy.array([lon])
			    lats=numpy.array([lat])
			    x,y = map(*numpy.meshgrid(lons,lats))
	                    map.plot(x,y,marker=7,markersize=3.0,markeredgewidth=0.6,markerfacecolor='red',markeredgecolor='red')
#	                elif agreement == 100:
#			    lons=numpy.array([lon])
#			    lats=numpy.array([lat])
#			    x,y = map(*numpy.meshgrid(lons,lats))
#	                    map.plot(x,y,marker='|',markersize=3.0,markeredgewidth=0.6,markerfacecolor='black',markeredgecolor='black')
#	   
	    # Print individual image headings, or if there are none print the row and clolumn headings
            if img_headings is not None:
                plt.title(img_headings[row][col],size=14)
            
	    else:
		
		if(row == nrows-1 and col_headings):
        	    plt.title(col_headings[col],size=18)

        	if(col == 0 and row_headings):
                    if inline_row_headings:
                        plt.title(row_headings[row],size=14)
                    else:
                        plt.ylabel(row_headings[row],size=18)
	    
           
	    if(draw_axis):
                labels=[0,0,0,0]

                if(col == ncols-1):
                    labels[1] = 1
                if (row == 0):
                    labels[3]=1

                # draw parallels
                if delat: 
                    circles = numpy.arange(minlat,maxlat,delat).tolist()
                    map.drawparallels(circles,labels=labels,fontsize=8,linewidth=0.5)
		    if equator==True:
		        map.drawparallels([0],dashes=[5,2],linewidth=0.4)

                #draw meridians
                if delon:
                    meridians = numpy.arange(minlon,maxlon,delon)
                    map.drawmeridians(meridians,labels=labels,fontsize=8,linewidth=0.5)

    # colour bar
    #cax = plt.axes([0.15,0.035,0.7,0.03]) # setup colorbar axes.
    cax = plt.axes([0.15,vpadding*2,0.7,colourbar])   # used to be vpadding*2
    plt.xticks(fontsize=12)
    #plt.colorbar(cax=cax,orientation='horizontal',ticks=ticks,extend='both',format="%.2f") # draw colorbar
    #cb = plt.colorbar(cax=cax,orientation='horizontal',ticks=ticks,extend=extend,format="%.2f") # draw colorbar
    cb = plt.colorbar(mappable=im,cax=cax,orientation='horizontal',ticks=ticks,extend=extend) # draw colorbar
    if units:
        cb.set_label(units)

    plt.axes(ax)  # make the original axes current again
    plt.savefig(ofile)#,dpi=300)


def get_min_max(files,variables,region):

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

            tVar = fin(var,region)
            tmax = tVar.max()
            tmin = tVar.min()
            if tmax > max_level:
                max_level = tmax

            if tmin < min_level:
                min_level = tmin

            fin.close()

    return min_level,max_level


def cmap_discretize(cmap, N):
    """
    Return a discrete colormap from the continuous colormap cmap.
    
    cmap: colormap instance, eg. cm.jet. 
    N: Number of colors.
     
    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    Code from matplotlib cookbook
    """

    cdict = cmap._segmentdata.copy()
    # N colors
    colors_i = numpy.linspace(0,1.,N)
    # N+1 indices
    indices = numpy.linspace(0,1.,N+1)
    for key in ('red','green','blue'):
        # Find the N colors
        D = numpy.array(cdict[key])
        I = interpolate.interp1d(D[:,0], D[:,1])
        colors = I(colors_i)
        # Place these colors at the correct indices.
        A = numpy.zeros((N+1,3), float)
        A[:,0] = indices
        A[1:,1] = colors
        A[:-1,2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
            L.append(tuple(l))
        cdict[key] = tuple(L)
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


def cmap_map(function,cmap):
    """ 
    Applies function (which should operate on vectors of shape 3:
    [r, g, b], on colormap cmap. This routine will break any discontinuous points in a colormap.

    Code from matplotlib cookbook
    """
    cdict = cmap._segmentdata
    step_dict = {}
    # Firt get the list of points where the segments start or end
    for key in ('red','green','blue'):         step_dict[key] = map(lambda x: x[0], cdict[key])
    step_list = reduce(lambda x, y: x+y, step_dict.values())
    step_list = numpy.array(list(set(step_list)))
    # Then compute the LUT, and apply the function to the LUT
    reduced_cmap = lambda step : numpy.array(cmap(step)[0:3])
    old_LUT = numpy.array(map( reduced_cmap, step_list))
    new_LUT = numpy.array(map( function, old_LUT))
    # Now try to make a minimal segment definition of the new LUT
    cdict = {}
    for i,key in enumerate(('red','green','blue')):
        this_cdict = {}
        for j,step in enumerate(step_list):
            if step in step_dict[key]:
                this_cdict[step] = new_LUT[j,i]
            elif new_LUT[j,i]!=old_LUT[j,i]:
                this_cdict[step] = new_LUT[j,i]
        colorvector=  map(lambda x: x + (x[1], ), this_cdict.items())
        colorvector.sort()
        cdict[key] = colorvector

    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


def custom_colourmap(colours,bounds):

    red = []
    green = []
    blue = []
    cdict = {}

    convert = matplotlib.colors.ColorConverter()

    for c in colours:
        r,g,b = convert.to_rgb(c)
        red.append(r)
        green.append(g)
        blue.append(b)

    indices = bounds[:]
    #indices.append(bounds[-1]+1)
    #indices.insert(0,bounds[0]-1)

    #Normalise
    indices = [i - indices[0] for i in indices]
    indices = [i/(indices[-1]*1.0) for i in indices]
   
    for key in ('red','green','blue'):
        A = numpy.zeros((len(indices),3), float)
        A[:,0] = indices
        if key == "red":
           colors = red
        elif key == "green":
            colors = green
        elif key == "blue":
            colors = blue

        A[1:,1] = colors
        A[:-1,2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
            L.append(tuple(l))
        cdict[key] = tuple(L)
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


def nonlinear_colourmap(cmap, bounds):
    """
    Return a discrete colormap from the continuous colormap cmap.
    
    cmap: colormap instance, eg. cm.jet. 
    N: Number of colors.
     
    Example
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)

    Code from matplotlib cookbook
    """

    cdict = cmap._segmentdata.copy()
    # N colors
    N = len(bounds) - 1
    colors_i = numpy.linspace(0,1.,N)
    
    #Indices    
    indices = bounds[:]

    #Normalise
    indices = [i - indices[0] for i in indices]
    indices = [i/(indices[-1]*1.0) for i in indices]

    for key in ('red','green','blue'):
        # Find the N colors
        D = numpy.array(cdict[key])
        I = interpolate.interp1d(D[:,0], D[:,1])
        colors = I(colors_i)
        # Place these colors at the correct indices.
        A = numpy.zeros((N+1,3), float)
        A[:,0] = indices
        A[1:,1] = colors
        A[:-1,2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
            L.append(tuple(l))
        cdict[key] = tuple(L)
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


def str2list(s):
    if(isinstance(s,basestring)):
        if(s.count(' ')):
            s = s.split(' ')
        elif(s.count(',')):
            s = s.split(',')
        else:
            s = [s]

    return s



if __name__ == '__main__':

    ### Help and manual information ###

    usage = "usage: %prog [options] {}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual",action="store_true",dest="manual",default=False,help="output a detailed description of the program")
    parser.add_option("-r", "--region",dest="region",type='string',default='WORLD360',help="select season")
    parser.add_option("-u", "--units",dest="units",type='string',default=False,help="units [conversion will occur if necessary]")
    parser.add_option("-o", "--obs", dest="obs",default=None,help="List of comma seperated observational data files [defualt = none]")
    parser.add_option("-l", "--legend", dest="legend",default=2,type='int',help="Location of the figure legend [defualt = 2]")
    
    (options, args) = parser.parse_args()            # Now that the options have been defined, instruct the program to parse the command line

    if options.manual == True or len(sys.argv) == 1:
	print """
	Usage:
            python plot_map.py [-M] [-h] [-r] [-u] [-o] [-l] {input file 1} {input file 2} ... {input file N} {output file}

	Options
            -M  -> Display this on-line manual page and exit
            -h  -> Display a help/usage message and exit
	    -r  -> Select region [default = WORLD360] 
	    -u  -> Units (program will automatically convert from 'kg m-2 s-1' to 'mm day-1' and 'K' to 'C')
	    -o  -> List of comma separated observational files 
	    -l  -> Location of the legend [default = 2]
        	    
	Environment
	    abyss.earthsci.unimelb.edu.au
	        /opt/cdat/bin/python
	    dcc.nci.org.au
                module use /projects/r87/public/modulefiles;
		module load python/2.7.1 python-cdat-lite/6.0rc2-py2.7 python-basemap/0.99.4-py2.7
		module load cct
	    cherax
	        module load opendap;
                module load python/2.5.1;
                export PYTHONPATH=/tools/cdat/5.0.0/lib/python2.5/site-packages/;
                export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/tools/cdat/5.0.0/Externals/lib
		
	Options for the multiplot function
            ifiles              List of input files, in an order such that positions in the matrix start bottom left and fill row by row [required] 
            variables           List of comma seperated variable names corresponding to the input files
            title               Title of plot
            dimensions          List of comma seperated matrix dimensions (rows,columns)
            ofile               Name of output file [default = 'title'.png]
            region              Selector defining a region. Inbuilt regions are WORLD_GRENEWICH, WORLD_DATELINE, AUSTRALIA, AUS_NZ [default = WORLD_DATELINE]
            minlat              User can override the pre-defined region by specifying bounds
            minlon              " "
            maxlat              " "
            maxlon              " " 
            colourbar_colour    Selector defining a matplotlib colorbar (e.g. 'jet','jet_r','hot','Blues')
            units               Units of the data - appears as a label below the colourbar
            ticks               List of comma seperataed tick marks to appear on the colour bar
            discrete_segments   List of comma seperated hexadecimal segment colours (e.g. #FF0B0B,#D5BA00,...) to appear on the colour bar
                                This will override colourbar_colour and there must be one less discrete segment than number of ticks
            convert             Selector for automatic unit conversion (it will convert 'kg m-2 s-1' to 'mm day-1' or 'K' to 'C')
            extend              Selector for arrow points at either end of colourbar. Can be 'both', 'neither, 'min' or 'max' [default = 'neither']
            resolution          Resolution of the background map. Can he 'h' (high), 'm' (medium) or 'l' (low)
            area_threshold      Threshold (in km) for the smallest resolved feature on the background map
            draw_vectors        Switch for drawing wind vectors on the plot [default = False]
            uwnd_files          List of input zonal surface wind files, in an order such that positions in the matrix start bottom left and fill row by row [defualt = none]
            uwnd_variables      List of comma seperated variable names corresponding to the input zonal surface wind files [default = none] 
            vwnd_files          List of input meridional surface wind files, in an order such that positions in the matrix start bottom left and fill row by row [defualt = none]
            vwnd_variables      List of comma seperated variable names corresponding to the input meridional surface wind files [default = none] 
            draw_stippling      Switch for drawing stippling on the plot [default = False]
            stipple_files       List of input stippling files (containing 1s and 0s to indicate stippling and no stippling respectively), in an order such that positions in the matrix start bottom left and fill row by row [defualt = none]
            stipple_variables   List of comma seperated variable names corresponding to the input stippling files [default = none] 
            row_headings        List of comma seperated row headings (order bottom to top) [default = none] 
            col_headings        List of comma seperated column headings (order left to right) [default = none]
            img_headings        List of comma seperated headings for each individual plot, in an order such that positions in the matrix start bottom left and fill row by row [defualt = none]
            draw_axis           Switch for drawing lat/lon gridlines on plot [default = False]
            delat               Interval (in degrees latitude) between meridional gridlines [default = 20]
            delon               Interval (in degrees longitude) between zonal gridlines [default = 40]
            equator             Switch for drawing an extra grid line marking the equator [default = False]
            contour             Switch for drawing a contour plot (default = False, which simply fills each grid cell with the appropriate shading)
            image_size          Width of individual images (in inches) [default = 6]

	Example
	
	Note

	Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
	"""
	sys.exit(0)
    
    
    if options.obs:
        obs_list = [str(s) for s in options.obs.split(',')]
    else:
        obs_list = None
        
    model_list = args[0:-1]
    outfile = args[-1]
    
    main(model_list,obs_list,outfile,options.region,options.units,options.legend)



####################
###  Example plot ##
####################
#
##path = '/cs/datastore/csdar/irv033/projections/tas/ann_se/'
##infile_list = [path+'tas_proj.global.ensemble_all.2030.sresa2.ann.nc',path+'tas_proj.global.ensemble_all.2055.sresa2.ann.nc',
##path+'tas_proj.global.ensemble_all.2090.sresa2.ann.nc',path+'tas_proj.global.ensemble_all.2030.sresa1b.ann.nc',
##path+'tas_proj.global.ensemble_all.2055.sresa1b.ann.nc',path+'tas_proj.global.ensemble_all.2090.sresa1b.ann.nc']
##variable_list = ['tas2030','tas2055','tas2090','tas2030','tas2055','tas2090']
##dims = [2,3]
##title = 'Change in surface air temperature relative to 1990 (all model ensemble)'
##outfile = 'example.png'
##tick_list = [0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]
##seg_list = ['#FFFFDF','#FFFF95','#FFFF0B','#FFAA0B','#FF660B','#FF0B0B','#800000','#550000','#350000']
##row_heads = ['A2','A1B']       
##col_heads = ['2030','2055','2099']
##
##multiplot(infile_list,variable_list,title,dimensions=dims,ofile=outfile,region=PACIFIC,res='l',area_threshold=1,units='degrees Celcius',
##ticks=tick_list,discrete_segments=seg_list,row_headings=row_heads,col_headings=col_heads,draw_axis=True,contour=True,image_size=4)
