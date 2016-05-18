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

def apply_polynomial(x_data, coefficient_data, anomaly=False):
    """Evaluate cubic polynomial.

    Args:
      x_data (numpy.ndarray): One dimensional x-axis data
      coefficient_data (numpy.ndarray): Multi-dimensional coefficient array (e.g. lat, lon, depth)
      anomaly (bool): 
        True: provide entire polynomial
        False: provide only the temporal deviations from the initial value (a_data)

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

    if anomaly:
        result = coefficient_dict['a'] + coefficient_dict['b'] * x_data + coefficient_dict['c'] * x_data**2 + coefficient_dict['d'] * x_data**3  
    else:
        result = coefficient_dict['b'] * x_data + coefficient_dict['c'] * x_data**2 + coefficient_dict['d'] * x_data**3 

    return result 


def check_attributes(data_attrs, control_attrs):
    """Make sure the correct control run has been used."""

    assert data_attrs['parent_experiment_id'] in [control_attrs['experiment_id'], 'N/A']

    control_rip = 'r%si%sp%s' %(control_attrs['realization'],
                                control_attrs['initialization_method'],
                                control_attrs['realization'])
    assert data_attrs['parent_experiment_rip'] in [control_rip, 'N/A']


def dedrift(data_cubelist, coefficient_cubelist, anomaly=False):
    """De-drift the input data.

    Args:
      data (iris.cube.CubeList): List of data cubes to be de-drifted
      coefficients (iris.cube.CubeList): Cubic polynomial coefficients describing the control run drift
        (these are generated using calc_drift_coefficients.py)
      anomaly (bool, optional): Output the anomaly rather than restored full values

    """

    new_cubelist = []
    for data_cube in data_cubelist:
        coefficient_cube = coefficient_cubelist.extract(data_cube.long_name)[0]
        check_attributes(data_cube.attributes, coefficient_cube.attributes)

        # Sync the data time axis with the coefficient time axis        
        time_values = data_cube.coord('time').points + data_cube.attributes['branch_time']
        # Remove the drift
        drift_signal = apply_polynomial(time_values, coefficient_cube.data, anomaly=anomaly)
        new_cube = data_cube - drift_signal
        new_cube.metadata = data_cube.metadata

        new_cubelist.append(new_cube)

    new_cubelist = iris.cube.CubeList(new_cubelist)

    return new_cubelist

    
def main(inargs):
    """Run the program."""
    
    data_cubelist = iris.load(inargs.data_file)
    coefficient_cubelist = iris.load(inargs.coefficient_file)

    new_cubelist = dedrift(data_cubelist, coefficient_cubelist, anomaly=inargs.anomaly)

    # Write the output file
    metadata_dict = {inargs.data_file: data_cubelist[0].attributes['history'], 
                     inargs.coefficient_file: coefficient_cubelist[0].attributes['history']}
    for cube in new_cubelist:
        cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

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

    parser.add_argument("data_file", type=str, help="Input data file")
    parser.add_argument("coefficient_file", type=str, help="Input coefficient file")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--anomaly", action="store_true", default=False,
                        help="output the anomaly rather than restored full values [default: False]")
    
    args = parser.parse_args()            

    main(args)
