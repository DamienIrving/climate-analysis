"""Implementation of the rotation theory outlined at
http://www.ocgy.ubc.ca/~yzq/books/MOM3/s4node19.html

To select psir, you are supposed to 

"""


### Import required modules ###

import numpy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


# Coordinate system transforms ##

def lat_adjust(inlat):
   """Switch latitude between a typical spherical system and
   one where the latitude is 90 (pi/2) at the north pole
   and -90 (-pi/2) at the south pole (i.e. a geographic system).
   
   Radians expected.
   """
   
   return numpy.deg2rad(90) - inlat 
   

def spherical_to_cartesian(lat_geographic, lon):
    """Take the latitude and longitude from a geographic spherical 
    coordinate system and convert to x, y, z of cartesian system.
    
    Radians expected.
    """
    
    lat_spherical = lat_adjust(lat_geographic)
    
    x = numpy.cos(lon) * numpy.sin(lat_spherical)
    y = numpy.sin(lon) * numpy.sin(lat_spherical)
    z = numpy.cos(lat_spherical)
 
    return x, y, z


def cartesian_to_spherical(x, y, z):
    """Take the x, y ,z values from the cartesian coordinate system 
    and convert to a latitude and longitude of geographic spherical 
    system.
    
    Output is in radians.
    """
    
    y = numpy.where(numpy.absolute(y) < 0.000001, 0.0, y)
    x = numpy.where(numpy.absolute(x) < 0.000001, 0.0, x)
    
    lat_spherical = numpy.arccos(z)
    lon = numpy.arctan2(y, x)
    #S = numpy.sqrt(numpy.square(x) + numpy.square(y))
    #lon = numpy.where(x < 0, numpy.pi - numpy.arcsin(y/S), numpy.arcsin(y/S))
    
    lat_geographic = lat_adjust(lat_spherical)
    
    return lat_geographic, lon


## Coordinate system rotations ##

def rotation_matrix(phir, thetar, psir, inverse=False):
    """Get the rotation matrix or its inverse.
    
    It appears that the inverse matrix is inverse in the sense 
    that it repeats the rotations backwards, but it does not
    always (particularly when the rotated poles have a new longitude)
    represent the matrix inverse (i.e. A*A-1 = I). The latter can be 
    calculated using numpy.linalg.inv(A).
    
    Inputs angles are expected in radians.
    """
    
    matrix = numpy.zeros([3, 3])
    if not inverse:
	matrix[0,0] = (numpy.cos(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.sin(psir))
	matrix[0,1] = (numpy.cos(psir) * numpy.sin(phir)) + (numpy.cos(thetar) * numpy.cos(phir) * numpy.sin(psir))
	matrix[0,2] = numpy.sin(psir) * numpy.sin(thetar)

	matrix[1,0] = -(numpy.sin(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.cos(psir))
	matrix[1,1] = -(numpy.sin(psir) * numpy.sin(phir)) + (numpy.cos(thetar) * numpy.cos(phir) * numpy.cos(psir))
	matrix[1,2] = numpy.cos(psir) * numpy.sin(thetar)

	matrix[2,0] = numpy.sin(thetar) * numpy.sin(phir)
	matrix[2,1] = -numpy.sin(thetar) * numpy.cos(phir)
	matrix[2,2] = numpy.cos(thetar)

    else:
	matrix[0,0] = (numpy.cos(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.sin(psir))
	matrix[0,1] = -(numpy.sin(psir) * numpy.cos(phir)) - (numpy.cos(thetar) * numpy.sin(phir) * numpy.cos(psir))
	matrix[0,2] = numpy.sin(thetar) * numpy.sin(phir) 

	matrix[1,0] = (numpy.cos(psir) * numpy.sin(phir)) + (numpy.cos(thetar) * numpy.cos(phir) * numpy.sin(psir))
	matrix[1,1] = -(numpy.sin(psir) * numpy.sin(phir)) + (numpy.cos(thetar) * numpy.cos(phir) * numpy.cos(psir))
	matrix[1,2] = -numpy.sin(thetar) * numpy.cos(phir)

	matrix[2,0] = numpy.sin(thetar) * numpy.sin(psir)
	matrix[2,1] = numpy.sin(thetar) * numpy.cos(psir)
	matrix[2,2] = numpy.cos(thetar)

    return matrix


def geographic_to_rotated_cartesian(x, y, z, phir, thetar, psir):
    """Covert from unrotated geographic cartestian coordinates (x, y, z) to
    rotated cartesian coordinates (xrot, yrot, zrot), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir).
    
    Input angles are expected in radians.
    """

    input_matrix = numpy.array([x, y, z])
    A = rotation_matrix(phir, thetar, psir)
        
    dot_product = numpy.dot(A, input_matrix)
    xrot = dot_product[0, :]
    yrot = dot_product[1, :]
    zrot = dot_product[2, :]
    
    return xrot, yrot, zrot
    

def geographic_to_rotated_spherical(lat, lon, phir, thetar, psir):
    """Convert from geographic spherical coordinates (lat, lon) to
    rotated spherical coordinates (latrot, lonrot), according to the rotation 
    about the origial z axis (phir), new x axis after the first rotation (thetar),
    and about the final z axis (psir).
    
    Inputs and outputs are all in radians.
    """
    
    x, y, z = spherical_to_cartesian(lat, lon)
    xrot, yrot, zrot = geographic_to_rotated_cartesian(x, y, z, phir, thetar, psir)
    latrot, lonrot = cartesian_to_spherical(xrot, yrot, zrot)
    
    return latrot, lonrot 


def rotated_to_geographic_cartesian(xrot, yrot, zrot, phir, thetar, psir):
    """Covert from rotated cartestian coordinates (xrot, yrot, zrot) to
    geographic cartesian coordinates (x, y, z), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir).
    
    Input angles expected in radians.
    """
    
    input_matrix = numpy.array([xrot, yrot, zrot])
    A_inverse = rotation_matrix(phir, thetar, psir, inverse=True)
        
    dot_product = numpy.dot(A_inverse, input_matrix)
    x = dot_product[0, :]
    y = dot_product[1, :]
    z = dot_product[2, :]
    
    return x, y, z


def rotated_to_geographic_spherical(latrot, lonrot, phir, thetar, psir):
    """Convert from rotated spherical coordinates (latrot, lonrot) to
    geographic spherical coordinates (lat, lon), according to the rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir).
    
    Input and output angles are in radians.
    """
    
    xrot, yrot, zrot = spherical_to_cartesian(latrot, lonrot)
    x, y, z = rotated_to_geographic_cartesian(xrot, yrot, zrot, phir, thetar, psir)    
    lat, lon = cartesian_to_spherical(x, y, z)
    
    return lat, lon 


## Miscellaneous ##

def north_pole_to_rotation_angles(latnp, lonnp):
    """Convert position of rotated north pole to a rotation about the
    original z axis (phir) and new z axis after the first rotation (thetar).
    
    Inputs expected in degrees. Output in radians.
    """

    phir = numpy.deg2rad(lonnp)
    thetar = numpy.deg2rad(90.0 - latnp)

    return phir, thetar    


## Testing ##

def print_pairs(data1, data2):
    """Print pairs of data values"""
    
    assert len(data1) == len(data2), \
    "Input vectors must be same length"
    
    for i in range(0, len(data1)):
        print data1[i], data2[i]
	

def test_inversion(npole_lat, npole_lon, psir_deg):
    """Rotate and restore data to check if you get
    back what you put in"""
    
    phir, thetar = north_pole_to_rotation_angles(npole_lat, npole_lon)   #30.0, 0.0 gives a nice PSA line
    psir = numpy.deg2rad(psir_deg)  

    print phir, thetar, psir
    
    start_lats = numpy.arange(-90, 105, 15)
    start_lons = numpy.arange(0, 390, 30)

    print 'start'
    print_pairs(start_lats, start_lons)

    rotated_lats, rotated_lons = geographic_to_rotated_spherical(numpy.deg2rad(start_lats), numpy.deg2rad(start_lons), phir, thetar, psir)
    print 'rotated'
    print_pairs(numpy.rad2deg(rotated_lats), numpy.rad2deg(rotated_lons))

    restored_lats, restored_lons = rotated_to_geographic_spherical(rotated_lats, rotated_lons, phir, thetar, psir)
    print 'restored'
    print_pairs(numpy.rad2deg(restored_lats), numpy.rad2deg(restored_lons))


def plot_equator(npole_lat, npole_lon, psir_deg, projection='cyl', ofile=False):
    """Plot the rotated equator"""

    phir, thetar = north_pole_to_rotation_angles(npole_lat, npole_lon)   #30.0, 0.0 gives a nice PSA line
    psir = numpy.deg2rad(psir_deg) 

    lonrot = numpy.arange(0, 360, 1) 
    latrot = numpy.zeros(len(lonrot))

    latgeo, longeo = rotated_to_geographic_spherical(numpy.deg2rad(latrot), numpy.deg2rad(lonrot), phir, thetar, psir)

    #print values to screen

    for i in range(0, len(latgeo)):
        print '(%s, %s) rotated becomes (%s, %s) geographic'  %(latrot[i], lonrot[i], numpy.rad2deg(latgeo[i]), numpy.rad2deg(longeo[i]))

    #create the plot
    if projection == 'nsper':
        h = 12000  #height of satellite, 
        lon_central = 235
        lat_central = -60
        map = Basemap(projection='nsper', lon_0=lon_central, lat_0=lat_central, satellite_height=h*1000.)
    else:
        map = Basemap(llcrnrlon=-180, llcrnrlat=-90, urcrnrlon=180, urcrnrlat=90, projection='cyl')

    map.drawcoastlines()
    map.drawparallels(numpy.arange(-90,90,30),labels=[1,0,0,0],color='grey',dashes=[1,3])
    map.drawmeridians(numpy.arange(0,360,45),labels=[0,0,0,1],color='grey',dashes=[1,3])
    #map.drawmapboundary(fill_color='#99ffff')

    lats = numpy.rad2deg(latgeo)
    lons = numpy.rad2deg(longeo)
    x, y = map(lons, lats)
    map.scatter(x, y, linewidth=1.5, color='r')

    if ofile:
        plt.savefig(ofile)
    else:
        plt.show()




