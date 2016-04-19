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

def apply_polynomial(x, axis):
    """Evaluate cubic polynomial.

    The axis argument is not used but is required for the function to be 
      used with numpy.apply_over_axes 

    """

    result = a + b * x + c * x**2 + d * x**3  
    
    return result 


def check_attributes(data_attrs, control_attrs):
    """Make sure the correct control run has been used."""

    assert data_attrs['parent_experiment_id'] in [control_attrs['experiment_id'], 'N/A']

    control_rip = 'r%si%sp%s' %(control_attrs['realization'],
                                control_attrs['initialization_method'],
                                control_attrs['realization'])
    assert data_attrs['parent_experiment_rip'] in [control_rip, 'N/A']

    
def main(inargs):
    """Run the program."""
    
    # Read the data
    data_cube = iris.load(inargs.data_file, inargs.var)
    with iris.FUTURE.context(cell_datetime_objects=True):
        data_cube = iris.load_cube(inargs.data_file, inargs.var)
        a_cube = iris.load_cube(inargs.coefficient_file, 'coefficient a')
        b_cube = iris.load_cube(inargs.coefficient_file, 'coefficient b')
        c_cube = iris.load_cube(inargs.coefficient_file, 'coefficient c')
        d_cube = iris.load_cube(inargs.coefficient_file, 'coefficient d')

    check_attributes(data_cube.attributes, a_cube.attributes)

    # Sync the data time axis with the coefficient time axis    
    #in_time_unit = a_cube.attributes['time_unit']
    #in_calendar = a_cube.attributes['time_calendar']
    #new_unit = cf_units.Unit(in_time_unit, calendar=in_calendar) 
    #data_cube.coord('time').convert_units(new_unit)
    
    time_values = data_cube.coord('time').points + data_cube.attributes['branch_time']

    # Remove the drift
#    polynomial = numpy.poly1d([a,b,c,d])
#    drift_signal = polynomial(time_coord)

#    coefficients = [a_cube.data, b_cube.data, c_cube.data, d_cube.data]
#    drift_signal = numpy.polynomial.polynomial.polyval(time_values, coefficients, tensor=True)
#    drift_signal = numpy.rollaxis(drift_signal, -1)  # move time axis from end to start

    global a
    a = a_cube.data
    global b
    b = b_cube.data
    global c
    c = c_cube.data
    global d
    d = d_cube.data

    drift_signal = numpy.apply_over_axes(apply_polynomial, data_cube.data, 0)
    
    new_cube = data_cube - drift_signal

    # Write the output file

#    iris.std_names.STD_NAMES['ocean_heat_content_in'] = {'canonical_units': units}
    new_cube.standard_name = data_cube.standard_name
    new_cube.long_name = data_cube.long_name
    new_cube.var_name = data_cube.var_name
    new_cube.attributes = data_cube.attributes

    metadata_dict = {inargs.data_file: data_cube.attributes['history'], 
                     inargs.coefficient_file: a_cube.attributes['history']}
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
    
    args = parser.parse_args()            

    main(args)
