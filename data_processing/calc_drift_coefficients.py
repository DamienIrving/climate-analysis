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

def edit_attributes(cube, field, filename):
    """Remove the attributes that typically differ between files.

    (i.e. these cause iris to throw a ConstraintMismatchError when you try and merge
    cubes arising from different files)  

    """ 
    cube.attributes.pop('creation_date', None)
    cube.attributes.pop('tracking_id', None)
    history.append(cube.attributes['history'])
    cube.attributes.pop('history', None)


def polyfit(data, time_axis):
    """Fit polynomial to data."""    

    if data.mask[0]:
        return numpy.array([data.fill_value]*4) 
    else:    
        return numpy.polynomial.polynomial.polyfit(time_axis, data, 3)


def main(inargs):
    """Run the program."""

    # Read the data
    cube = iris.load(inargs.infiles, inargs.var, callback=edit_attributes)
    cube = cube.concatenate_cube()

    coord_names = [coord.name() for coord in cube.coords(dim_coords=True)]
    assert coord_names[0] == 'time', "First axis must be time"

    time_axis = cube.coord('time').points

    # Calculate coefficients for cubic polynomial
    if 'depth' in coord_names:
        assert coord_names[1] == 'depth', 'coordinate order must be time, depth, ...'
        slice_dims = copy.copy(coord_names)
        slice_dims.remove('depth')
        out_shape = list(cube.shape)
        out_shape[0] = 4
        coefficients = numpy.zeros(out_shape)
        for i, x_slice in enumerate(cube.slices(slice_dims)):
            coefficients[:,i,::] = numpy.ma.apply_along_axis(polyfit, 0, x_slice.data, time_axis)
        fill_value = x_slice.data.fill_value 
    else:    
        coefficients = numpy.ma.apply_along_axis(polyfit, 0, cube.data, time_axis)
        fill_value = cube.data.fill_value 
    coefficients = numpy.ma.masked_values(coefficients, fill_value)

    # Get all the metadata
    cube.attributes['polynomial'] = 'a + bx + cx^2 + dx^3'
    cube.attributes['time_unit'] = str(cube.coord('time').units)
    cube.attributes['time_calendar'] = str(cube.coord('time').units.calendar)
    cube.attributes['history'] = gio.write_metadata(file_info={inargs.infiles[0]: history[0]})  
    #FIXME: Is there a better way to deal with lots of files?

    # Write the output file
    dim_coords = []
    for i, coord_name in enumerate(coord_names[1:]):
        dim_coords.append((cube.coord(coord_name), i))

    if cube.aux_coords:
        assert len(cube.aux_coords) == 2, "Script can only deal with two auxillary coordinates"
        dims = range(0, len(coefficients.shape) - 1)
        aux_coords = [(cube.aux_coords[0], [dims[-2], dims[-1]]), (cube.aux_coords[1], [dims[-2], dims[-1]])]
    else:
        aux_coords = None
        
    out_cubes = []
    for i, coeff in enumerate(['a', 'b', 'c', 'd']):
        standard_name = 'coefficient_%s' %(coeff)
        iris.std_names.STD_NAMES[standard_name] = {'canonical_units': ' '}
        out_cubes.append(iris.cube.Cube(coefficients[i, ...],
                                        standard_name=standard_name,
                                        long_name='coefficient %s' %(coeff),
                                        var_name=coeff,
                                        units=' ',
                                        attributes=cube.attributes,
                                        dim_coords_and_dims=dim_coords,
                                        aux_coords_and_dims=aux_coords))

    cube_list = iris.cube.CubeList(out_cubes)
    out_cube = cube_list.concatenate()

    iris.save(out_cube, inargs.outfile)


if __name__ == '__main__':

    extra_info =""" 
example:
    
author:
    Damien Irving, irving.damien@gmail.com
notes:
    If there's a vertical coordinate is must have the standard_name "depth"    

"""

    description='Calculate the polynomial coefficents that characterise model drift'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infiles", type=str, nargs='*', help="Input file names")
    parser.add_argument("var", type=str, help="Input file variable (standard_name)")
    parser.add_argument("outfile", type=str, help="Output file name")


    args = parser.parse_args()
    main(args)

