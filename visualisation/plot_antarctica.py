
### Import required modules ###

import numpy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

#import cdms2

### Define globals ###

res='c'
area_threshold = 1.0

# Zoom out for PSA
h = 12000  #height of satellite, 
lon_central = 265
lat_central = -60


### Plot the map ###

#map = Basemap(projection='spaeqd',boundinglat=-40,lon_0=180,resolution='l')  # Polar Azimuthal Equidistant Projection
#map = Basemap(projection='splaea',boundinglat=-10,lon_0=90,resolution='l')  # Polar Lambert Azimuthal Projection
map = Basemap(projection='nsper',lon_0=lon_central,lat_0=lat_central,satellite_height=h*1000.,resolution=res,area_thresh=area_threshold)

#plot coastlines, draw label meridians and parallels.
map.drawcoastlines()
map.drawparallels(numpy.arange(-90,90,30),labels=[1,0,0,0],color='grey',dashes=[1,3])
map.drawmeridians(numpy.arange(0,360,30),labels=[0,0,0,1],color='grey',dashes=[1,3])


## Simple plot (no data) ##

# fill continents 'coral' (with zorder=0), color wet areas 'aqua'
map.drawmapboundary(fill_color='#99ffff')
map.fillcontinents(color='#cc9966',lake_color='#99ffff')
 
### More complex plot ##
#
#fin = cdms2.open(,'r')
#tVar = fin(variable_list[row,col],time=(timmean[0],timmean[1]),squeeze=1)
#tVar_lon = tVar.getLongitude()[:]
#tVar_lat = tVar.getLatitude()[:]
#
#tVar = tVar - 273.16
#
## make 2-d grid of lons, lats
#lons, lats = np.meshgrid(longitudes,latitudes)
#
##set desired contour levels
#clevs = np.arange(960,1061,5)
#
## compute native x,y coordinates of grid.
#x, y = m(lons, lats)
#
#CS2 = m.contourf(x,y,slp,clevs,cmap=plt.cm.RdBu_r,animated=True)
#


#plt.show()
plt.savefig('Antarctica_zoomed_out.eps')
