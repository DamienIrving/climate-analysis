"""Collection of functions for changing spherical
coordinate system.

To import:
module_dir = os.path.join(os.environ['HOME'], 'data_processing')
sys.path.insert(0, module_dir)

Included functions:

rotation_matrix  
  -- Get the rotation matrix or its inverse
rotate_cartesian  
  --  Convert from geographic cartestian coordinates (x, y, z) to
      rotated cartesian coordinates (xrot, yrot, zrot)  
rotate_spherical
  --  Convert from geographic spherical coordinates (lat, lon) to
      rotated spherical coordinates (latrot, lonrot)

angular_distance
  --  Calculate angular distance between two points on a sphere
rotation_angle
  --  Find angle of rotation between the old and new north pole.

plot_equator
  --  Plot the rotated equator

Reference:
Rotation theory: http://www.ocgy.ubc.ca/~yzq/books/MOM3/s4node19.html
"""

#############################
## Import required modules ##
#############################

import numpy
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

import MV2
import css


##########################################
## Switching between coordinate systems ##
##########################################

def _filter_tiny(data, threshold=0.000001):
    """Convert values of magnitude < threshold to zero"""

    return numpy.where(numpy.absolute(data) < threshold, 0.0, data)
 

def _adjust_lon_range(lons):
    """Express longitude values in the range [0, 2pi]
    
    Input and output in radians.
    """
    
    return numpy.where(lons < 0.0, lons + 2.0*numpy.pi, lons)


#################################
## Coordinate system rotations ##
#################################

def rotation_matrix(phir, thetar, psir, inverse=False):
    """Get the rotation matrix or its inverse.
    Inputs angles are expected in radians.
    Reference: http://www.ocgy.ubc.ca/~yzq/books/MOM3/s4node19.html
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


def rotate_cartesian(x, y, z, phir, thetar, psir, invert=False):
    """Rotate cartestian coordinate system (x, y, z) according to a rotation 
    about the origial z axis (phir), new z axis after the first rotation (thetar),
    and about the final z axis (psir).
    
    Invert can be true or false.
    Input angles are expected in degrees.
    """

    phir_rad = numpy.deg2rad(phir)
    thetar_rad = numpy.deg2rad(thetar)
    psir_rad = numpy.deg2rad(psir)

    input_matrix = numpy.array([x.flatten(), y.flatten(), z.flatten()])
    A = rotation_matrix(phir_rad, thetar_rad, psir_rad, inverse=invert)
        
    dot_product = numpy.dot(A, input_matrix)
    xrot = dot_product[0, :]
    yrot = dot_product[1, :]
    zrot = dot_product[2, :]
    
    return xrot, yrot, zrot
    

def rotate_spherical(lat, lon, phir, thetar, psir, invert=False):
    """Rotate spherical coordinate system (lat, lon) according to the rotation 
    about the origial z axis (phir), new x axis after the first rotation (thetar),
    and about the final z axis (psir).
    
    Inputs and outputs are all in degrees. Longitudes are output [0, 360]
    Output is a flattened lat and lon array, with element-wise pairs corresponding 
    to every grid point.
    """
    
    lon_mesh, lat_mesh = numpy.meshgrid(lon, lat)  # This is the correct order
    
    x, y, z = css.cssgridmodule.css2c(lat_mesh.flatten(), lon_mesh.flatten())
    xrot, yrot, zrot = rotate_cartesian(x, y, z, phir, thetar, psir, invert=invert)
    latrot, lonrot = css.cssgridmodule.csc2s(xrot, yrot, zrot)
    
    #### At the poles, csc2s produces longitude values that are 180 degrees out of
    #### phase with the original data.
    #### It also outputs lons that are (-180, 180), but this is not really a problem.

    
    return latrot, _adjust_lon_range(lonrot) 


############################
## Spherical trigonometry ##
############################

def _arccos_check(data):
    """Adjust for precision errors when usinmg numpy.arccos
    
    numpy.arccos is only defined [-1, 1]. Sometimes due to precision
    you can get values that are very slightly > 1 or < -1, which causes
    numpy.arccos to be undefinded. This function adjusts for this. 
    
    """
    
    data = numpy.where(data < -1.0, -1.0, data)
    data = numpy.where(data > 1.0, 1.0, data)
    
    return data


def angular_distance(lat1deg, lon1deg, lat2deg, lon2deg):
    """Find the angular distance between two points on
    the sphere.
    
    Calculation taken from http://www.movable-type.co.uk/scripts/latlong.html
    
    Assumes a sphere of unit radius.
    
    Input in degrees. Output in radians.
    """

    lat1 = numpy.deg2rad(lat1deg)
    lon1 = numpy.deg2rad(lon1deg)
    lat2 = numpy.deg2rad(lat2deg)
    lon2 = numpy.deg2rad(lon2deg)

    angular_dist = numpy.arccos(numpy.sin(lat1)*numpy.sin(lat2) + numpy.cos(lat1)*numpy.cos(lat2)*numpy.cos(lon2 - lon1))
    #calc taken from http://www.movable-type.co.uk/scripts/latlong.html
    #says it is based on the spherical law of cosines, but I need to verfiy this
    
    return _filter_tiny(angular_dist)
    

def rotation_angle(latA, lonA, latB, lonB, latC, lonC):
    """For a given point on the sphere, find the angle of rotation 
    between the old and new north pole.
    
    Formulae make use of spherical triangles and are based 
    on the spherical law of cosines. 
    
    Inputs:
      Point A = Location of original north pole
      Point B = Location of new north pole
      Point C = Point of interest
      Input in degrees
    
    Output:
      Angle C = Rotation angle between old and new north pole
      Output in radians
    """

    a = angular_distance(latB, lonB, latC, lonC)
    b = angular_distance(latA, lonA, latC, lonC)
    c = angular_distance(latA, lonA, latB, lonB)

    #angleA = numpy.arccos((numpy.cos(a) - numpy.cos(b)*numpy.cos(c)) / (numpy.sin(b)*numpy.sin(c)))
    #angleB = numpy.arccos((numpy.cos(b) - numpy.cos(c)*numpy.cos(a)) / (numpy.sin(c)*numpy.sin(a)))
    angleC = numpy.arccos(_arccos_check((numpy.cos(c) - numpy.cos(a)*numpy.cos(b)) / (numpy.sin(a)*numpy.sin(b))))

    rot_angle = _rotation_sign(angleC, latA, latC, lonA, lonB)
    
    return rot_angle


def _rotation_sign(angleC, latA, latC, lonA, lonB):
   """Determine the sign of the rotation angle.
   
   The basic premise that that if the lon of the new pole (lonB) 
   is greater than the lon of the original pole (lonA), then the 
   sign of the angle is negative.
   
   However, if the latitude of the original north pole (latA) is less
   than the latitude of the new north pole (latC) (which can't happen if
   the original pole was at 90N) then the reverse is true. 
   
   if latA > latC:
       rot_angle = -angleC if (lonB > lonA) else angleC
   else:
       rot_angle = angleC if (lonB > lonA) else -angleC      
   
   """
   
   angleC_lon_adjust = numpy.where(lonB > lonA, -angleC, angleC)
   angleC_lat_adjust = numpy.where(latA < latC, -angleC_lon_adjust, angleC_lon_adjust)
   
   return angleC_lat_adjust
   

#############################
## North pole manipulation ##
#############################

def north_pole_to_rotation_angles(latnp, lonnp, prime_meridian_point=None):
    """Convert position of rotated north pole to a rotation about the
    original z axis (phir) and new z axis after the first rotation (thetar).
    
    Input and output in degrees.
    
    The prime meridian point should be a list of length 2 (lat, lon), representing a
    point through which the prime meridian should travel.
    
    """

    psir = 90.0 - lonnp
    thetar = 90.0 - latnp 

    if prime_meridian_point:
        ## I don't fully understand the setting of phir
        assert len(prime_meridian_point) == 2, \
	'The prime point must be a list of length 2'
	pm_lat = prime_meridian_point[0] 
	pm_lon = prime_meridian_point[1] 
        lat_temp, phir = rotate_spherical(numpy.array([pm_lat,]), numpy.array([pm_lon,]), 0.0, thetar, psir)
    else:
        phir = 0.0
    
    return phir, thetar, psir    
			
              
#############    
## Testing ##
#############

def print_pairs(data1, data2):
    """Print pairs of data values"""
    
    assert len(data1) == len(data2), \
    "Input vectors must be same length"
    
    for i in range(0, len(data1)):
        print data1[i], data2[i]
	

def test_inversion(npole_lat, npole_lon, psir):
    """Rotate and restore data to check if you get
    back what you put in"""
    
    phir, thetar = north_pole_to_rotation_angles(npole_lat, npole_lon)   #30.0, 0.0 gives a nice PSA line  

    print phir, thetar, psir
    
    start_lats = numpy.arange(-90, 105, 15)
    start_lons = numpy.arange(0, 390, 30)

    print 'start'
    print_pairs(start_lats, start_lons)

    rotated_lats, rotated_lons = rotate_spherical(start_lats, start_lons, phir, thetar, psir)
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
        map = Basemap(llcrnrlon=0, llcrnrlat=-90, urcrnrlon=360, urcrnrlat=90, projection='cyl')

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
