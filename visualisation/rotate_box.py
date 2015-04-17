"""


"""

# Import general Python modules

import os, sys, pdb
import numpy, argparse

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
    import coordinate_rotation as crot
    import convenient_universal as uconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')



def main(inargs):
    """Run the program."""

    fout = open(inargs.outfile, 'w')
    phi, theta, psi = crot.north_pole_to_rotation_angles(inargs.north_pole_lat, inargs.north_plot_lon)

    borders = {}
    for border_number in range(0, len(inargs.corner) - 1):
        start_lat, start_lon = inargs.corner[border_number]
        end_lat, end_lon = inargs.corner[border_number + 1]
        lats = numpy.arange(start_lat, end_lat + inargs.resolution, inargs.resolution)
        lons = numpy.arange(start_lon, end_lon + inargs.resolution, inargs.resolution)
        
        rot_lats, rot_lons = crot.rotate_spherical(lats, lons, phi, theta, psi, invert=True)
        rot_lons_adjust = uconv.adjust_lon_range(rot_lons, radians=False, start=0.0)

        #fout.write(date+'\n')   write to file (maybe mesh lat and lon first?)

    fout.close()


if __name__ == '__main__':

    extra_info = """
example:
  
  
"""

    description='Take a box or line from the rotated world and return conventional coordinates.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="output file name")
    parser.add_argument("north_pole_lat", type=str, "latitude of the rotated world north pole")
    parser.add_argument("north_pole_lon", type=str, "longitude of the rotated world north pole")
    
    parser.add_argument("--corner", type=str, action='append', nargs=2, metavar=('LAT', 'LON'),  
                        help="a corner of the shape")
    parser.add_argument("--resolution", type=float, default=1.0,
                        help="resolution of the shape (i.e. spacing between plotted points)")

    args = parser.parse_args()              
    main(args)
