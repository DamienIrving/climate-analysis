## Simple plotting example ## 

import cdms2
import numpy
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, shiftgrid

# read in data #

ufile = cdms2.open('/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc')
vfile = cdms2.open('/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc')

u = ufile('ua')
v = vfile('va')

# calculate wind speed #

wsp = (u**2 + v**2)**0.5

# make cylindrical basemap 
m = Basemap(llcrnrlon=-180, llcrnrlat=-90,  
            urcrnrlon=180, urcrnrlat=90,
	    resolution='c', projection='cyl')

# shift the longitude grid to be -180 to 180
datout, lon_axis = shiftgrid(180., wsp[0, ::], u.getLongitude()[:], start=False)
lat_axis = u.getLatitude()[:]

# create figure, add axes
fig1 = plt.figure(figsize=(8,10))
ax = fig1.add_axes([0.1,0.1,0.8,0.8])

# make 2-d grid of lons, lats
# compute native x,y coordinates of grid
lons, lats = numpy.meshgrid(lon_axis, lat_axis)
x, y = m(lons, lats)

# set desired contour levels.
clevs = numpy.arange(0, 80, 10)
parallels = numpy.arange(-90., 90, 30.)
meridians = numpy.arange(0., 360., 30.)

# re-project the data onto the map
#transfor_scalar fails if lon isn't -180 to 180
#transform_scalar not needed for cyl plots
#datout = m.transform_scalar(datout,   
#                            lon_axis, 
#                            lat_axis, 
#                            200, 200) 
#                            #order=0)

# create the contour plot
cs1 = m.contourf(x, y, datout, clevs)

# draw coastlines, parallels, meridians.
m.drawcoastlines(linewidth=1.5)
labels = [0, 1, 0, 1] #designate sides for labels
m.drawparallels(parallels, labels=labels, fontsize=8, linewidth=0.5)
m.drawmeridians(meridians, labels=labels, fontsize=8, linewidth=0.5)

# add colorbar
cb = m.colorbar(cs1, "bottom", pad="10%")
cb.set_label('m s-1')

# add title
ax.set_title('250 hPa wind speed, January 1979')

plt.show()
