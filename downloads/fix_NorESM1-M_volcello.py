"""
Filename:     fix_NorESM1-M_volcello.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Correct erroneous NorESM1-M volcello data using the deptho and areacello data

"""

# Import general Python modules

import sys, os, pdb
import argparse, numpy
import iris

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
    import general_io as gio
    import spatial_weights
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def main(inargs):
    """Run the program."""

    volume_cube = iris.load_cube(inargs.volcello_file, 'ocean_volume')
    area_cube = iris.load_cube(inargs.areacello_file, 'cell_area')
    
    dim_coord_names = [coord.name() for coord in volume_cube.dim_coords]

    vert_extents = spatial_weights.calc_vertical_weights_1D(volume_cube.coord('depth'), dim_coord_names, volume_cube.shape)   
    volume_data = area_cube.data * vert_extents
    volume_data = volume_data.astype(numpy.float32)
    volume_cube.data = volume_cube.data * 0.0 + volume_data

    # Write output file
    outfile_metadata = {inargs.volcello_file: volume_cube.attributes['history'],
                        inargs.areacello_file: area_cube.attributes['history']}
    volume_cube.attributes['history'] = gio.write_metadata(file_info=outfile_metadata)
    iris.save(volume_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com
"""

    description='Correct erroneous NorESM1-M volcello data using the deptho and areacello data'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("volcello_file", type=str, help="Input erroneous ocean volume file")
    parser.add_argument("areacello_file", type=str, help="Input ocean area file")
    parser.add_argument("outfile", type=str, help="Output file name")    

    args = parser.parse_args()             
    main(args)
