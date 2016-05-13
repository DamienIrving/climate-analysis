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

    Anomaly = True: provide entire polynomial
    Anomaly = False: provide only the temporal deviations from the initial value (a_data)

    """

    x_data = x_data[..., numpy.newaxis, numpy.newaxis, numpy.newaxis]
    a_data = coefficient_data[0, ...]
    b_data = coefficient_data[1, ...]
    c_data = coefficient_data[2, ...]
    d_data = coefficient_data[3, ...]

    a_data = numpy.repeat(a_data[numpy.newaxis, ...], x_data.shape[0], axis=0)
    b_data = numpy.repeat(b_data[numpy.newaxis, ...], x_data.shape[0], axis=0)
    c_data = numpy.repeat(c_data[numpy.newaxis, ...], x_data.shape[0], axis=0)
    d_data = numpy.repeat(d_data[numpy.newaxis, ...], x_data.shape[0], axis=0)

    assert x_data.ndim == a_data.ndim

    if anomaly:
        result = a_data + b_data * x_data + c_data * x_data**2 + d_data * x_data**3  
    else:
        result = b_data * x_data + c_data * x_data**2 + d_data * x_data**3 

    return result 


def check_attributes(data_attrs, control_attrs):
    """Make sure the correct control run has been used."""

    assert data_attrs['parent_experiment_id'] in [control_attrs['experiment_id'], 'N/A']

    control_rip = 'r%si%sp%s' %(control_attrs['realization'],
                                control_attrs['initialization_method'],
                                control_attrs['realization'])
    assert data_attrs['parent_experiment_rip'] in [control_rip, 'N/A']


def dedrift(data, coefficients, anomaly=False):
    """De-drift the input data.

    Args:
      data (iris.cube): Data to be de-drifted
      coefficients (iris): Cubic polynomial coefficients describing the control run drift
        (these are generated using calc_drift_coefficients.py)
      anomaly (bool, optional): Output the anomaly rather than restored full values

    """

    check_attributes(data.attributes, coefficients.attributes)

    # Sync the data time axis with the coefficient time axis        
    time_values = data.coord('time').points + data.attributes['branch_time']

    # Remove the drift
    drift_signal = apply_polynomial(time_values, coefficients.data, anomaly=anomaly)
    new_cube = data - drift_signal

    return new_cube

    
def main(inargs):
    """Run the program."""
    
    data_cube = iris.load(inargs.data_file, inargs.var)
    coefficient_cube = iris.load_cube(inargs.coefficient_file, inargs.var)

    new_cube = dedrift(data_cube, coefficient_cube, anomaly=inargs.anomaly)

    # Write the output file
    new_cube.standard_name = data_cube.standard_name
    new_cube.long_name = data_cube.long_name
    new_cube.var_name = data_cube.var_name
    new_cube.attributes = data_cube.attributes

    metadata_dict = {inargs.data_file: data_cube.attributes['history'], 
                     inargs.coefficient_file: coefficient_cube.attributes['history']}
    new_cube.attributes['history'] = gio.write_metadata(file_info=metadata_dict)

    iris.save(new_cube, inargs.outfile)


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
    parser.add_argument("var", type=str, help="Input data variable name (i.e. the standard_name)")
    parser.add_argument("coefficient_file", type=str, help="Input coefficient file")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--anomaly", action="store_true", default=False,
                        help="output the anomaly rather than restored full values [default: False]")
    
    args = parser.parse_args()            

    main(args)
