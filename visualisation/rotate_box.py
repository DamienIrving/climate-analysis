"""


"""

# Import general Python modules

import os, sys, pdb
import argparse

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




phi, theta, psi = crot.north_pole_to_rotation_angles(np[0], np[1])
rot_lats, rot_lons = crot.rotate_spherical(borders[side+'_lats'], borders[side+'_lons'], phi, theta, psi, invert=False)
rot_lons_adjust = uconv.adjust_lon_range(rot_lons, radians=False, start=0.0)



if __name__ == '__main__':

    extra_info = """
example:
  
  
"""

    description='Take a box or line from the rotated world and return conventional coordinates.'
    parser = argparse.ArgumentParser(description=description, 
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("corners", type=float, help="corners of the shape")
    parser.add_argument("outfile", type=str, help="output file name")

    parser.add_argument("--resolution", type=float, default=1.0,
                        help="resolution of the shape (i.e. spacing between plotted points)")

    args = parser.parse_args()              
    main(args)
