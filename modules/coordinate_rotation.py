"""Collection of functions for changing spherical coordinate system.

Functions:
  rotation_matrix  --  Get the rotation matrix or its inverse
  rotate_cartesian --  Convert from geographic cartestian coordinates (x, y, z) to
                       rotated cartesian coordinates (xrot, yrot, zrot)  
  rotate_spherical --  Convert from geographic spherical coordinates (lat, lon) to
                       rotated spherical coordinates (latrot, lonrot)
  angular_distance --  Calculate angular distance between two points on a sphere
  rotation_angle   --  Find angle of rotation between the old and new north pole.

"""

# Import general Python libraries

import math
import numpy

import MV2
import css

import sys, os 

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


##########################################
## Switching between coordinate systems ##
##########################################

def switch_regular_axes(data, lats_in, lons_in, lat_axis_out, lon_axis_out, new_np, 
                        pm_point=(0, 0), invert=False, euler=None):
    """Regrid data according to location of the new north pole.
    
    References: The css package (http://www2-pcmdi.llnl.gov/cdat/contrib/csgriddoc) is 
    based on the ngmath library (http://ngwww.ucar.edu/ngmath/)
    
    Args:
      data (numpy.ndarray): Input data
      lats_in, lons_in (list/tuple): Together these lists describe pairs corresponding 
        to each point on the input grid (i.e. each latitude and longitude value is 
        repeated many times). For regular grids, these pairs can be generated using 
        netcdf_io.coordinate_pairs()
      lat_axis_out, lon_axis_in (list/tuple): Axis values for the regular/uniform output 
        grid (i.e. together they do not desribe coordinate pairs for every grid point)
      new_np (list/tuple): Location of new north pole (latitude, longitude)
      pm_point (list/tuple, optional): Prime meridian point
      invert (bool): If true, do the process backward (i.e. regrid from the location of 
        new_np back to a grid where the north pole is at 90N
      euler (list/tuple): Override the calculated rotation angles (phi, theta, psi)
    
    """

    if euler: #override the north_pole_to_rotation_angles function
        phi, theta, psi = euler
    else:
        phi, theta, psi = north_pole_to_rotation_angles(new_np[0], new_np[1], prime_meridian_point=pm_point)
    
    lats_in_rot, lons_in_rot = rotate_spherical(lats_in, lons_in, phi, theta, psi, invert=invert)

    grid_instance = css.Cssgrid(lats_in_rot, lons_in_rot, lat_axis_out, lon_axis_out)
    if numpy.rank(data) == 3:    
        data_rot = numpy.zeros(numpy.shape(data))
        for tstep in xrange(0, numpy.shape(data)[0]):
            regrid = grid_instance.rgrd(data[tstep, :, :].flatten())
            data_rot[tstep, :, :] = numpy.transpose(regrid)
    elif numpy.rank(data) == 2: 
        regrid = grid_instance.rgrd(data.flatten())
        data_rot = numpy.transpose(regrid)
        
    return data_rot


###########################
## Numerical adjustments ##
###########################

def _filter_tiny(data, threshold=0.000001):
    """Convert values of magnitude < threshold to zero."""

    return numpy.where(numpy.absolute(data) < threshold, 0.0, data)
 

#################################
## Coordinate system rotations ##
#################################

def rotation_matrix(phir, thetar, psir, inverse=False):
    """Get the rotation matrix or its inverse.
    
    Input angles are expected in radians.

    Reference: Pacanowski R, & Griffies S (2000). Defining the rotation. The MOM manual.
    http://www.ocgy.ubc.ca/~yzq/books/MOM3/s4node19.html
    
    """
    
    for angle in [phir, thetar, psir]:
        assert 0.0 <= math.fabs(angle) <= 2*math.pi, "Input angles must be in radians [0, 2*pi]" 
    
    matrix = numpy.empty([3, 3])
    if inverse:
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

    return _filter_tiny(matrix)


def rotate_cartesian(x, y, z, phir, thetar, psir, invert=False):
    """Rotate cartestian coordinate system.
    
    Input angles are expected in degrees.
    
    Args:
      x, y, z (list/tuple): cartesian coordinates to be rotated 
      phir (float): rotation angle about the original z axis 
      thetar (float): rotation angle about the new z axis after the first rotation
      psir (float): rotation angle about the final z axis
      invert (bool): If true, do the rotation backward   
   
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
    
    return _filter_tiny(xrot), _filter_tiny(yrot), _filter_tiny(zrot)
    

def rotate_spherical(lats, lons, phi, theta, psi, invert=False):
    """Rotate spherical coordinate system.

    Inputs and outputs are all in degrees.
    
    References: The css package (http://www2-pcmdi.llnl.gov/cdat/contrib/csgriddoc) is 
    based on the ngmath library (http://ngwww.ucar.edu/ngmath/)   
    
    Args:
      lats, lons (list/tuple): Together these lists describe pairs corresponding 
        to each point on the input grid (i.e. each latitude and longitude value is 
        repeated many times). For regular grids, these pairs can be generated using 
        netcdf_io.coordinate_pairs()
      phir (float): rotation angle about the original z axis 
      thetar (float): rotation angle about the new z axis after the first rotation
      psir (float): rotation angle about the final z axis
      invert (bool): If true, do the rotation backward 
    
    Returns:
      Output is a flattened lat and lon array, with element-wise pairs corresponding 
      to every grid point. Longitudes are output [0, 360].
    
    """
    
    lats = uconv.single2list(lats)
    lons = uconv.single2list(lons)
    
    assert len(lats) == len(lons), \
    'lats and lons are pairs corresponding to each grid point'
    
    x, y, z = css.cssgridmodule.css2c(lats, lons)
    x = _filter_tiny(x)    # Filter small values or else they can cause innaccurate
    y = _filter_tiny(y)    # values at poles by moving into wrong quadrant
    z = _filter_tiny(z)    # (lon can end up 180 degrees displaced)
    
    xrot, yrot, zrot = rotate_cartesian(x, y, z, phi, theta, psi, invert=invert)
    
    latrot, lonrot = css.cssgridmodule.csc2s(xrot, yrot, zrot)  # csc2s produces lon values (-180, 180)

    #In cartesian coordinates (x, y, z) the poles are at [0,0,1] and [0,0,-1], which css.cssgridmodule.csc2s
    #always interprets as having a longitude of zero. Could try and fix this with a function like:
    #lonrot = numpy.where(numpy.abs(lats) == 90.0, lons + phi + psi, lonrot)
    #but I haven't. Accuracy at the poles is not important
    
    return latrot, uconv.adjust_lon_range(lonrot, radians=False, start=0.0) 


############################
## Spherical trigonometry ##
############################

def _arccos_check(data):
    """Adjust for precision errors when using numpy.arccos.
    
    numpy.arccos is only defined [-1, 1]. Sometimes due to precision
    you can get values that are very slightly > 1 or < -1, which causes
    numpy.arccos to be undefinded. This function adjusts for this.
    
    """
    
    data = numpy.clip(data, -1.0, 1.0)
    
    return data


def angular_distance(lat1deg, lon1deg, lat2deg, lon2deg):
    """Find the angular distance between two points on the sphere.
    
    Assumes a sphere of unit radius.
    Input in degrees. Output in radians.
    
    Reference: Calculation taken from http://www.movable-type.co.uk/scripts/latlong.html
    
    """

    lat1 = numpy.deg2rad(lat1deg)
    lon1 = numpy.deg2rad(lon1deg)
    lat2 = numpy.deg2rad(lat2deg)
    lon2 = numpy.deg2rad(lon2deg)

    angular_dist = numpy.arccos(numpy.sin(lat1)*numpy.sin(lat2) + numpy.cos(lat1)*numpy.cos(lat2)*numpy.cos(lon2 - lon1))
    #calc taken from http://www.movable-type.co.uk/scripts/latlong.html
    #says it is based on the spherical law of cosines, but I need to verfiy this
      
    return _filter_tiny(angular_dist)
    

def rotation_angle(latA, lonA, latB, lonB, latsC, lonsC, reshape=None):
    """For a given point on the sphere, find the angle of rotation 
    between the old and new north pole.
    
    Formulae make use of spherical triangles and are based 
    on the spherical law of cosines. 
    
    There can be only one specified original and new north pole, 
    but multiple points of interest.
    
    Input in degrees. Output in radians.
    
    ERROR TO FIX: When both the old and new pole are the same and the latitude=90,
    the rotation angle is pi, not zero.
    
    Args:
      latA, lonA (float): Location of original north pole
      latB, lonB (float): Location of new north pole
      latC, lonC (list/tuple): Points of interest
      reshape (list/tuple): Reshaped dimensions of output array
      
    Returns:
      Rotation angle between old and new north pole (in radians)
      
    """
    
    ##Some assertions (e.g. latA, lonA, latB, lonB must be len=1, while latC and lonC do not 
    ##Perhaps change names of latA etc to something more meaningful (e.g. new_np_lat)?

    latsC = uconv.single2list(latsC)
    lonsC = uconv.single2list(lonsC)

    latA_flat = numpy.repeat(latA, len(lonsC))
    lonA_flat = numpy.repeat(lonA, len(lonsC))
    latB_flat = numpy.repeat(latB, len(lonsC))
    lonB_flat = numpy.repeat(lonB, len(lonsC))

    a_vals = angular_distance(latB_flat, lonB_flat, latsC, lonsC)
    b_vals = angular_distance(latA_flat, lonA_flat, latsC, lonsC)
    c_vals = angular_distance(latA_flat, lonA_flat, latB_flat, lonB_flat)

    # Fix to avoid divide by zero error when locationC = locationA or locationB, which makes a or b zero
    # (later on the angle will be defined as zero at these points)
    a_vals_fix = numpy.where(_filter_tiny(numpy.sin(a_vals)) == 0.0, 1.0, a_vals)
    b_vals_fix = numpy.where(_filter_tiny(numpy.sin(b_vals)) == 0.0, 1.0, b_vals)

    #angleA_magnitude = numpy.arccos((numpy.cos(a) - numpy.cos(b)*numpy.cos(c)) / (numpy.sin(b)*numpy.sin(c)))
    #angleB_magnitude = numpy.arccos((numpy.cos(b) - numpy.cos(c)*numpy.cos(a)) / (numpy.sin(c)*numpy.sin(a)))
    angleC_magnitude = numpy.arccos(_arccos_check((numpy.cos(c_vals) - numpy.cos(a_vals_fix)*numpy.cos(b_vals_fix)) / (numpy.sin(a_vals_fix)*numpy.sin(b_vals_fix))))

    # Make the rotation angle 0.0 at points where it is undefined
    angleC_magnitude = numpy.where(_filter_tiny(numpy.sin(a_vals)) == 0.0, 0.0, angleC_magnitude)
    angleC_magnitude = numpy.where(_filter_tiny(numpy.sin(b_vals)) == 0.0, 0.0, angleC_magnitude)
    
    angleC = _rotation_sign(angleC_magnitude, lonB_flat, lonsC)
    
    if reshape:
        angleC = numpy.reshape(angleC, reshape)
    
    return _filter_tiny(angleC)


def _rotation_sign(angleC, lonB, lonC):
    """Determine the sign of the rotation angle.

    The basic premise is that grid points (lonC) with a longitude in the range of
    180 degrees less than the longitude of the new pole (lonB) have a negative angle.

    Not sure if this is a universal rule (i.e. this works for when the original
    north pole was at 90N, 0E).
    
    """
    
    lonB = uconv.single2list(lonB, numpy_array=True)
    lonC = uconv.single2list(lonC, numpy_array=True)

    assert len(lonB) == len(lonC), \
    "Input arrays must be the same length"   

    lonB_360 = uconv.adjust_lon_range(lonB, radians=False, start=0.0)
    lonC_360 = uconv.adjust_lon_range(lonC, radians=False, start=0.0)

    new_start = lonB_360[0] - 180.0

    lonB_360 = uconv.adjust_lon_range(lonB_360, radians=False, start=new_start)
    lonC_360 = uconv.adjust_lon_range(lonC_360, radians=False, start=new_start)

    angleC_adjusted = numpy.where(lonC_360 < lonB_360, -angleC, angleC)

    return angleC_adjusted
   
    
#############################
## North pole manipulation ##
#############################

def north_pole_to_rotation_angles(latnp, lonnp, prime_meridian_point=(0, 0)):
    """Convert position of new north pole to rotation angles. 
    
    Input and output in degrees.
    
    Reference: Pacanowski R, & Griffies S (2000). Defining the rotation. The MOM manual.
    http://www.ocgy.ubc.ca/~yzq/books/MOM3/s4node19.html
    (although my definition of phi differs slightly from theirs)
    
    Args:
      latnp, lonnp (float): Position of the new north pole
      prime_meridian_point (list/tuple): A (lat, lon) point through which the prime 
        meridian should travel.
    
    Returns:
      Rotation angles (in degrees) about the original z axis (phi), new x axis after 
      the first rotation (theta), and about the final z axis (psi).
    
    """

    phi = lonnp + 90       #rotates the y-axis 'underneath' the pole (albeit 180 degrees around from it), 
                           #in preparation for the second rotation, where the latitude will be adjusted
    theta = 90.0 - latnp   #accounts for fact that the original north pole was at 90N

    lat_temp, psi = rotate_spherical(prime_meridian_point[0], prime_meridian_point[1], phi, theta, 0)
    
    return phi, theta, psi
