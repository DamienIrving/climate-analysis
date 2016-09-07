"""
Filename:     plot_delsole.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Recreate plot from DelSole et al (2016)

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import matplotlib.pyplot as plt
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

experiment_names = {('CSIRO-Mk3-6-0', 'historicalMisc', '3'): 'noAA',
                    ('CSIRO-Mk3-6-0', 'historicalMisc', '4'): 'AA'}

colors = {'noAA': 'r',
          'AA':, 'b',
          'historical': 'y':
          'piControl': '0.5',
          'Argo', 'g'}


def check_attributes(x_cube, y_cube):
    """Check that attributes match and return experiment."""

    # FIXME: Need to handle obs attributes

    x_model = x_cube.attributes['model_id']
    x_experiment = x_cube.attributes['experiment_id']
    x_physics = x_cube.attributes['physics_version']

    y_model = y_cube.attributes['model_id']
    y_experiment = y_cube.attributes['experiment_id']
    y_physics = y_cube.attributes['physics_version']

    assert x_model == y_model
    assert x_experiment == y_experiment
    assert x_physics == y_physics

    atts = (x_model, x_experiment, x_physics)

    if atts in experiment_names.keys():
        experiment = experiment_names[atts]
    else:
        experiment = x_experiment

    return experiment


def main(inargs):
    """Run the program."""

    for xfile, xvar, yfile, yvar in inargs.file_pair:
        x_cube = iris.load_cube(xfile, xvar)
        y_cube = iris.load_cube(yfile, yvar)

        experiment = check_attributes(x_cube, y_cube)


    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')

    metadata_dict = get_metadata(inargs, cube, climatology) 
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)


if __name__ == '__main__':

    extra_info =""" 
author:
  Damien Irving, irving.damien@gmail.com
    
"""

    description='Recreate plot from DelSole et al (2016)'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--file_pair", type=str, action='append', default=[], nargs=4,
                        metavar=('X_DATA', 'X_VAR', 'Y_DATA', 'Y_VAR'), help="x and y data pair")


    args = parser.parse_args()            
    main(args)
