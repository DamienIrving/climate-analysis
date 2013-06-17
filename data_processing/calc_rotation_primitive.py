"""Implementation of the rotation theory outlined at
http://gis.stackexchange.com/questions/10808/lon-lat-transformation"""


### Import required modules ###

import numpy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


def spherical_to_cartesian(lat, lon):
    """Take the latitude and longitude from a spherical coordinate
    system and convert to x, y, z of cartesian system"""
    
    x = numpy.cos(lon) * numpy.cos(lat)
    y = numpy.sin(lon) * numpy.cos(lat)
    z = numpy.sin(lat)
    
    return x, y, z


def cartesian_to_spherical(x, y, z):
    """Take the x, y ,z values from the cartesian coordinate system 
    and convert to a latitude and longitude of spherical system"""
    
    lat = numpy.arcsin(z)
    lon = numpy.arctan2(y, x)
    
    return lat, lon


def rotated_to_geographic_cartesian(ydeg, zdeg, xrot, yrot, zrot):
    """Covert from rotated cartestian coordinates (xrot, yrot, zrot) to
    geographic cartesian coordinates (x, y, z), according to the rotation 
    about the y axis (ydeg) and z axis (zdeg)"""
    
    x = (numpy.cos(ydeg) * numpy.cos(zdeg) * xrot) + (numpy.sin(zdeg) * yrot) + (numpy.sin(ydeg) * numpy.cos(zdeg) * zrot)
    y = -(numpy.cos(ydeg) * numpy.sin(zdeg) * xrot) + (numpy.cos(zdeg) * yrot) - (numpy.sin(ydeg) * numpy.sin(zdeg) * zrot)
    z = -(numpy.sin(ydeg) * xrot) + (numpy.cos(ydeg) * zrot)
    
    return x, y, z


def rotated_to_geographic_spherical(latrot, lonrot, ydeg, zdeg):
    """Convert from rotated spherical coordinates (latrot, lonrot) to
    geographic spherical coordinates (lat, lon). The rotation is specified
    by ydeg, zdeg."""
    
    xrot, yrot, zrot = spherical_to_cartesian(latrot, lonrot)
    x, y, z = rotated_to_geographic_cartesian(ydeg, zdeg, xrot, yrot, zrot)
    lat, lon = cartesian_to_spherical(x, y, z)
    
    return lat, lon 
          

def south_pole_to_rotation_angles(latsp, lonsp):
    """Convert position of south pole to rotation about the
    y and z axes (ydeg, zdeg)"""

    ydeg = -(90 + latsp)
    zdeg = -lonsp

    return ydeg, zdeg    
    

lonrot = numpy.arange(0, 360, 5) 
latrot = numpy.zeros(len(lonrot))
#lonrot = numpy.array([0.0, 0.0])
#latrot = numpy.array([90.0, -90.0])

ydeg, zdeg = south_pole_to_rotation_angles(-30.0, 80.0)

latgeo, longeo = rotated_to_geographic_spherical(numpy.deg2rad(latrot), numpy.deg2rad(lonrot), numpy.deg2rad(ydeg), numpy.deg2rad(zdeg))

for i in range(0, len(latgeo)):
    print '(%s, %s) rotated becomes (%s, %s) geographic'  %(latrot[i], lonrot[i], numpy.rad2deg(latgeo[i]), numpy.rad2deg(longeo[i]))


### Define globals ###

res='c'
area_threshold = 1.0

# Zoom out for PSA
h = 12000  #height of satellite, 
lon_central = 235
lat_central = -60


### Plot the map ###

#map = Basemap(projection='spaeqd',boundinglat=-40,lon_0=180,resolution='l')  # Polar Azimuthal Equidistant Projection
#map = Basemap(projection='splaea',boundinglat=-10,lon_0=90,resolution='l')  # Polar Lambert Azimuthal Projection
#map = Basemap(projection='mill',lon_0=180)
#map = Basemap(projection='nsper',lon_0=lon_central,lat_0=lat_central,satellite_height=h*1000.,resolution=res,area_thresh=area_threshold)
map = Basemap(llcrnrlon=-180, llcrnrlat=-90, urcrnrlon=180, urcrnrlat=90, projection='cyl')

#plot coastlines, draw label meridians and parallels.
map.drawcoastlines()
map.drawparallels(numpy.arange(-90,90,30), labels=[1,0,0,0], color='grey', dashes=[1,3])
map.drawmeridians(numpy.arange(0,360,30), labels=[0,0,0,1], color='grey', dashes=[1,3])


## Simple plot (no data) ##

# fill continents 'coral' (with zorder=0), color wet areas 'aqua'
map.drawmapboundary(fill_color='#99ffff')
map.fillcontinents(color='#cc9966',lake_color='#99ffff')

lats = numpy.rad2deg(latgeo)
lons = numpy.rad2deg(longeo)
x, y = map(lons, lats)
map.scatter(x, y, linewidth=1.5, color='r')


plt.show()
