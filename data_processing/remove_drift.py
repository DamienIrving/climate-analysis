"""
Filename:     remove_drift.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Remove drift from a data series

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import cf_units
from iris.experimental.equalise_cubes import equalise_attributes

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def apply_polynomial(x_data, coefficient_data):
    """Evaluate cubic polynomial.

    Args:
      x_data (numpy.ndarray): One dimensional x-axis data
      coefficient_data (numpy.ndarray): Multi-dimensional coefficient array (e.g. lat, lon, depth)

    """
    
    coefficient_dict = {}
    if coefficient_data.ndim == 1:
        coefficient_dict['a'] = coefficient_data[0]    
        coefficient_dict['b'] = coefficient_data[1]
        coefficient_dict['c'] = coefficient_data[2]    
        coefficient_dict['d'] = coefficient_data[3]  
    else:
        while x_data.ndim < coefficient_data.ndim:
            x_data = x_data[..., numpy.newaxis]
        for index, coefficient in enumerate(['a', 'b', 'c', 'd']):
            coef = coefficient_data[index, ...]
            coef = numpy.repeat(coef[numpy.newaxis, ...], x_data.shape[0], axis=0)
            assert x_data.ndim == coef.ndim
            coefficient_dict[coefficient] = coef

    result = coefficient_dict['a'] + coefficient_dict['b'] * x_data + coefficient_dict['c'] * x_data**2 + coefficient_dict['d'] * x_data**3  
    
    return result 


def check_attributes(data_attrs, control_attrs):
    """Make sure the correct control run has been used."""

    assert data_attrs['parent_experiment_id'] in [control_attrs['experiment_id'], 'N/A']

    control_rip = 'r%si%sp%s' %(control_attrs['realization'],
                                control_attrs['initialization_method'],
                                control_attrs['realization'])
    assert data_attrs['parent_experiment_rip'] in [control_rip, 'N/A']


def time_adjustment(first_data_cube, coefficient_cube):
    """Determine the adjustment that needs to be made to time axis."""

    branch_time_value = first_data_cube.attributes['branch_time'] #FIXME: Add half a time step?
    branch_time_unit = coefficient_cube.attributes['time_unit']
    branch_time_calendar = coefficient_cube.attributes['time_calendar']
    data_time_coord = first_data_cube.coord('time')

    new_unit = cf_units.Unit(branch_time_unit, calendar=branch_time_calendar)  
    data_time_coord.convert_units(new_unit)

    first_experiment_time = data_time_coord.points[0]
    time_diff = first_experiment_time - branch_time_value 

    return time_diff, first_experiment_time, new_unit

    
def main(inargs):
    """Run the program."""
    
    first_data_cube = iris.load_cube(inargs.data_files[0])
    coefficient_cube = iris.load_cube(inargs.coefficient_file)

    time_diff, first_experiment_time, new_time_unit = time_adjustment(first_data_cube, coefficient_cube)
    del first_data_cube

    new_cubelist = []
    for filename in inargs.data_files:
        
        data_cube = iris.load_cube(filename)
        check_attributes(data_cube.attributes, coefficient_cube.attributes)

        # Sync the data time axis with the coefficient time axis        
        time_coord = data_cube.coord('time')
        time_coord.convert_units(new_time_unit)
        
        assert time_coord.points[0] >= first_experiment_time
        time_values = time_coord.points - time_diff

        # Remove the drift
        drift_signal = apply_polynomial(time_values, coefficient_cube.data)
        new_cube = data_cube - drift_signal
        new_cube.metadata = data_cube.metadata

        if inargs.outfile[-3:] == '.nc':
            new_cubelist.append(new_cube)
        elif inargs.outfile[-1] == '/':        
            infile = filename.split('/')[-1]
            outfile = inargs.outfile + infile
            metadata_dict = {infile: data_cube.attributes['history'], 
                             inargs.coefficient_file: coefficient_cube.attributes['history']}
            new_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

            iris.save(new_cube, outfile)
            print 'output:', outfile
        
    if inargs.outfile[-3:] == '.nc':
        new_cubelist = iris.cube.CubeList(new_cubelist)
        equalise_attributes(new_cubelist)
        new_cubelist = new_cubelist.concatenate_cube()

        metadata_dict = {inargs.data_files[0]: data_cubelist[0].attributes['history'], 
                        inargs.coefficient_file: coefficient_cube.attributes['history']}
        new_cubelist.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

        iris.save(new_cubelist, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    Generate the polynomial coefficients first from calc_drift_coefficients.py
    
"""

    description='Remove drift from a data series'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("data_files", type=str, nargs='*', help="Input data files, in chronological order (needs to include whole experiment to get time axis correct)")
    parser.add_argument("coefficient_file", type=str, help="Input coefficient file")
    parser.add_argument("outfile", type=str, help="Give a path instead of a file name if you want an output file corresponding to each input file")
    
    args = parser.parse_args()            

    main(args)
