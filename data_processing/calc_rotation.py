"""Implementation of the rotation theory outlined at
http://www.ocgy.ubc.ca/~yzq/books/MOM3/s4node19.html"""


### Import required modules ###

import numpy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


# Coordinate system transforms ##

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


## Coordinate system rotations ##

def get_matrix(phir, thetar, psir, inverse=False):
    """Get the rotation matrix or its inverse."""
    
    A = numpy.zeros([3, 3])
    
    A[0,0] = (numpy.cos(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.sin(psir))
    A[0,1] = (numpy.cos(psir) * numpy.sin(phir)) - (numpy.cos(thetar) * numpy.cos(phir) * numpy.sin(psir))
    A[0,2] = numpy.sin(psir) * numpy.sin(thetar)
    
    A[1,0] = -(numpy.sin(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.cos(psir))
    A[1,1] = -(numpy.sin(psir) * numpy.sin(phir)) - (numpy.cos(thetar) * numpy.cos(phir) * numpy.cos(psir))
    A[1,2] = numpy.cos(psir) * numpy.sin(thetar)
    
    A[2,0] = numpy.sin(thetar) * numpy.sin(phir)
    A[2,1] = -numpy.sin(thetar) * numpy.cos(phir)
    A[2,2] = numpy.cos(thetar)

    if inverse:
        output = numpy.linalg.inv(A)
    else:
        output = A
	
    return output


def geographic_to_rotated_cartesian(x, y, z, phir, thetar, psir):
    """Covert from unrotated geographic cartestian coordinates (x, y, z) to
    rotated cartesian coordinates (xrot, yrot, zrot), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir)."""

    unrot_matrix = numpy.array([x, y, z])
    A = get_matrix(phir, thetar, psir)
    
#    A = numpy.zeros([3, 3])
#    
#    A[0,0] = (numpy.cos(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.sin(psir))
#    A[0,1] = (numpy.cos(psir) * numpy.sin(phir)) - (numpy.cos(thetar) * numpy.cos(phir) * numpy.sin(psir))
#    A[0,2] = numpy.sin(psir) * numpy.sin(thetar)
#    
#    A[1,0] = -(numpy.sin(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.cos(psir))
#    A[1,1] = -(numpy.sin(psir) * numpy.sin(phir)) - (numpy.cos(thetar) * numpy.cos(phir) * numpy.cos(psir))
#    A[1,2] = numpy.cos(psir) * numpy.sin(thetar)
#    
#    A[2,0] = numpy.sin(thetar) * numpy.sin(phir)
#    A[2,1] = -numpy.sin(thetar) * numpy.cos(phir)
#    A[2,2] = numpy.cos(thetar)
    
    dot_product = numpy.dot(A, unrot_matrix)
    xrot = dot_product[0, :]
    yrot = dot_product[1, :]
    zrot = dot_product[2, :]
    
    return xrot, yrot, zrot
    

def geographic_to_rotated_spherical(lat, lon, phir, thetar, psir=0):
    """Convert from geographic spherical coordinates (lat, lon) to
    rotated spherical coordinates (latrot, lonrot), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir)."""
    
    x, y, z = spherical_to_cartesian(lat, lon)
    xrot, yrot, zrot = geographic_to_rotated_cartesian(x, y, z, phir, thetar, psir)
    latrot, lonrot = cartesian_to_spherical(xrot, yrot, zrot)
    
    return latrot, lonrot 


def rotated_to_geographic_cartesian(xrot, yrot, zrot, phir, thetar, psir):
    """Covert from rotated cartestian coordinates (xrot, yrot, zrot) to
    geographic cartesian coordinates (x, y, z), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir)."""
    
    rot_matrix = numpy.array([xrot, yrot, zrot])
    A_inverse_numpy = get_matrix(phir, thetar, psir, inverse=True)
    
    A_inverse = numpy.zeros([3, 3])
    
    A_inverse[0,0] = (numpy.cos(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.sin(psir))
    A_inverse[0,1] = -(numpy.sin(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.cos(psir))
    A_inverse[0,2] = numpy.sin(thetar) * numpy.sin(phir)
    
    A_inverse[1,0] = (numpy.cos(psir) * numpy.sin(phir)) - (numpy.cos(thetar) * numpy.cos(phir) * numpy.sin(psir))
    A_inverse[1,1] = -(numpy.sin(psir) * numpy.sin(phir)) - (numpy.cos(thetar) * numpy.cos(phir) * numpy.cos(psir))
    A_inverse[1,2] = -numpy.sin(thetar) * numpy.cos(phir)
    
    A_inverse[2,0] = numpy.sin(thetar) * numpy.sin(psir)
    A_inverse[2,1] = numpy.sin(thetar) * numpy.cos(psir)
    A_inverse[2,2] = numpy.cos(thetar)
    
    dot_product = numpy.dot(A_inverse, rot_matrix)
    x = dot_product[0, :]
    y = dot_product[1, :]
    z = dot_product[2, :]
    
    return x, y, z


def rotated_to_geographic_spherical(latrot, lonrot, phir, thetar, psir=0):
    """Convert from rotated spherical coordinates (latrot, lonrot) to
    geographic spherical coordinates (lat, lon), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir)."""
    
    xrot, yrot, zrot = spherical_to_cartesian(latrot, lonrot)
    x, y, z = rotated_to_geographic_cartesian(xrot, yrot, zrot, phir, thetar, psir)
    lat, lon = cartesian_to_spherical(x, y, z)
    
    return lat, lon 


## Miscellaneous ##

def north_pole_to_rotation_angles(latnp, lonnp):
    """Convert position of rotated north pole to rotation about the
    original z axis (phir) and new z axis after the first rotation (thetar)"""

    phir = 90 - lonnp
    thetar = 90 - latnp

    return phir, thetar    
    
#lonrot = numpy.array([0.0, 0.0])
#latrot = numpy.array([90.0, -90.0])
lonrot = numpy.arange(0, 360, 1) 
latrot = numpy.zeros(len(lonrot))
phir, thetar = north_pole_to_rotation_angles(10,20)   #30.0, -100.0)

latgeo, longeo = rotated_to_geographic_spherical(numpy.deg2rad(latrot), numpy.deg2rad(lonrot), numpy.deg2rad(phir), numpy.deg2rad(thetar), psir=numpy.deg2rad(45.0))

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
map.drawparallels(numpy.arange(-90,90,30),labels=[1,0,0,0],color='grey',dashes=[1,3])
map.drawmeridians(numpy.arange(0,360,30),labels=[0,0,0,1],color='grey',dashes=[1,3])


## Simple plot (no data) ##

# fill continents 'coral' (with zorder=0), color wet areas 'aqua'
map.drawmapboundary(fill_color='#99ffff')
map.fillcontinents(color='#cc9966',lake_color='#99ffff')

lats = numpy.rad2deg(latgeo)
lons = numpy.rad2deg(longeo)
x, y = map(lons, lats)
map.scatter(x, y, linewidth=1.5, color='r')


plt.show()
