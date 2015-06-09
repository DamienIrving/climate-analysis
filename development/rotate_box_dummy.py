"""
Filename:     rotate_box.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Take a box or line from the rotated world and return conventional coordinates

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
    import convenient_universal as uconv
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')



def main(inargs):
    """Run the program."""

    fout = open(inargs.outfile, 'w')

    for border_number in range(0, len(inargs.corner) - 1):
        start_lat, start_lon = inargs.corner[border_number]
        end_lat, end_lon = inargs.corner[border_number + 1]
        
        end_lon = uconv.adjust_lon_range(end_lon, radians=False, start=start_lon)[0]
        assert start_lat <= end_lat, "Latitude values must go south to north"
        assert start_lon <= end_lon

        lats = numpy.arange(start_lat, end_lat + inargs.resolution, inargs.resolution)
        lons = numpy.arange(start_lon, end_lon + inargs.resolution, inargs.resolution)
        
        lat_mesh, lon_mesh = nio.coordinate_pairs(lats, lons)

        rot_lats, rot_lons = lat_mesh, lon_mesh
        
        for i in range(0, len(rot_lats)):
            pair = '%f, %f' %(rot_lats[i], rot_lons[i])
            fout.write(pair+'\n')

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
    
    parser.add_argument("--corner", type=float, action='append', nargs=2, metavar=('LAT', 'LON'),  
                        help="a corner of the shape")
    parser.add_argument("--resolution", type=float, default=1.0,
                        help="resolution of the shape (i.e. spacing between plotted points)")

    args = parser.parse_args()              
    main(args)
