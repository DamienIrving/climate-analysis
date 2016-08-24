"""
Filename:     calc_drift_coefficients.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate the polynomial coefficents that characterise model drift 

"""

# Import general Python modules

import sys, os, pdb
import argparse, copy
import numpy
import iris
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

history = []

def save_history(cube, field, filename):
    """Save the history attribute when reading the data.

    (This is required because the history attribute differs between input files 
    and is therefore deleted upon equilising attributes)  

    """ 

    history.append(cube.attributes['history'])


def polyfit(data, time_axis):
    """Fit polynomial to data."""    

    if type(data) == numpy.ndarray:
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 3)
    elif data.mask[0]:
        return numpy.array([data.fill_value]*4) 
    else:    
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 3)


def calc_coefficients(cube, coord_names, time_axis):
    """Calculate the polynomial coefficients."""

    if 'depth' in coord_names:
        assert coord_names[1] == 'depth', 'coordinate order must be time, depth, ...'
        slice_dims = copy.copy(coord_names)
        slice_dims.remove('depth')
        out_shape = list(cube.shape)
        out_shape[0] = 4
        coefficients = numpy.zeros(out_shape, dtype=numpy.float32)
        for i, x_slice in enumerate(cube.slices(slice_dims)):
            coefficients[:,i,::] = numpy.ma.apply_along_axis(polyfit, 0, x_slice.data, time_axis)
        fill_value = x_slice.data.fill_value 
        coefficients = numpy.ma.masked_values(coefficients, fill_value)
    elif cube.ndim == 1:
        coefficients = polyfit(cube.data, time_axis)
    else:    
        coefficients = numpy.ma.apply_along_axis(polyfit, 0, cube.data, time_axis)
        fill_value = cube.data.fill_value 
        coefficients = numpy.ma.masked_values(coefficients, fill_value)
    
    return coefficients


def set_global_atts(inargs, cube):
    """Set global attributes."""

    atts = copy.copy(cube.attributes)
    atts['polynomial'] = 'a + bx + cx^2 + dx^3'
    atts['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history[0]}) 

    return atts


def main(inargs):
    """Run the program."""

    # Read the data

    cubes = iris.load(inargs.infiles, inargs.var, callback=save_history)
    global_atts = set_global_atts(inargs, cubes[0])

    iris.util.unify_time_units(cubes)

    nvars = len(cubes) / len(inargs.infiles)
    out_cubes = []
    for var_index in range(0, nvars):
        cube = cubes[var_index::nvars]
        equalise_attributes(cube)
        cube = cube.concatenate_cube()
       
        coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]
        assert coord_names[0] == 'time', "First axis must be time"
        time_axis = cube.coord('time').points.astype(numpy.float32)
       
        coefficients = calc_coefficients(cube, coord_names, time_axis)

        # Write the output file

        iris.std_names.STD_NAMES['drift_coefficient'] = {'canonical_units': cube.units}
        coefficient_coord = iris.coords.DimCoord(numpy.array([1, 2, 3, 4]), 
                                                 standard_name='drift_coefficient', long_name='drift coefficient', 
                                                 var_name='coefficient', attributes=None)

        dim_coords = [(coefficient_coord, 0)]
        for i, coord_name in enumerate(coord_names[1:]):
            dim_coords.append((cube.coord(coord_name), i + 1))

        if cube.aux_coords:
            assert len(cube.aux_coords) == 2, "Script can only deal with two auxillary coordinates"
            dims = range(0, coefficients.ndim)
            aux_coords = [(cube.aux_coords[0], [dims[-2], dims[-1]]), (cube.aux_coords[1], [dims[-2], dims[-1]])]
        else:
            aux_coords = None

        iris.std_names.STD_NAMES[cube.var_name] = {'canonical_units': cube.units}
        new_cube = iris.cube.Cube(coefficients,
                                  standard_name=cube.standard_name,
                                  long_name=cube.long_name,
                                  var_name=cube.var_name,
                                  units=cube.units,
                                  attributes=global_atts,
                                  dim_coords_and_dims=dim_coords,
                                  aux_coords_and_dims=aux_coords)
        new_cube.attributes['time_unit'] = str(cube.coord('time').units)
        new_cube.attributes['time_calendar'] = str(cube.coord('time').units.calendar)
        new_cube.attributes['time_start'] = time_axis[0]
        new_cube.attributes['time_end'] = time_axis[-1]
        out_cubes.append(new_cube)

    cube_list = iris.cube.CubeList(out_cubes)
    out_cube = cube_list.concatenate()

    assert out_cube[0].data.dtype == numpy.float32
    iris.save(out_cube, inargs.outfile, netcdf_format='NETCDF3_CLASSIC')


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    If there's a vertical coordinate is must have the standard_name "depth"
    The input files may contain multiple variables    

"""

    description='Calculate the polynomial coefficents that characterise model drift'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--var", type=str, default=None,
                        help="Input variable [default = None, which means all input variables are done]")

    args = parser.parse_args()
    main(args)

