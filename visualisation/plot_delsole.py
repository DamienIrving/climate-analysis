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
import seaborn
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

experiment_names = {('CanESM2', 'historicalMisc', 4): 'historicalAA',
                    ('CSIRO-Mk3-6-0', 'historicalMisc', 3): 'noAA',
                    ('CSIRO-Mk3-6-0', 'historicalMisc', 4): 'historicalAA',
                    ('IPSL-CM5A-LR', 'historicalMisc', 3): 'historicalAA',
                    ('IPSL-CM5A-LR', 'historicalMisc', 4): 'noAA',
                    ('GFDL-CM3', 'historicalMisc', 1): 'historicalAA'}

experiment_colors = {'historicalGHG': 'r',
                     'noAA': 'g',
                     'historicalAA': 'b',
                     'historical': 'y',
                     'piControl': '0.5',
                     '1pctCO2': 'k',
                     'rcp85': 'c',
                     'rcp45': 'm',
                     'rcp26': 'g'}
 

label_dict = {'sea_surface_salinity': 'Salinity amplification (g/kg)',
              'precipitation_flux': 'Global mean precipitation (mm/day)',
              'water_evaporation_flux': 'Global mean evaporation (mm/day)',
              'air_temperature': 'Global mean temperature (K)'}

def get_label(var, pe_metric):
    """Get axis label"""

    if var == 'precipitation minus evaporation flux':
        if pe_metric == 'abs':
            label = 'Global mean $|P-E|$ (mm/day)'
        elif pe_metric == 'amp':
            label = 'P-E amplification'

    else:
        label = label_dict[var]

    return label


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

    atts = (x_model, x_experiment, float(x_physics))

    if atts in experiment_names.keys():
        experiment = experiment_names[atts]
    else:
        experiment = x_experiment

    return experiment, x_model


def calc_trend(x_data, y_data, experiment):
    """Calculate linear trend.

    polyfit returns [a, b] corresponding to y = a + bx

    """

    a_coefficient, b_coefficient = numpy.polynomial.polynomial.polyfit(x_data, y_data, 1)
    x_trend = numpy.arange(x_data.min(), x_data.max(), 0.01)
    y_trend = a_coefficient + b_coefficient * x_trend
    print experiment, 'trend:', b_coefficient

    return x_trend, y_trend


def get_data(data, var):
    """Adjust data units if required"""

    if var in ['precipitation_flux', 'water_evaporation_flux', 'precipitation minus evaporation flux']:
        data = data * 86400

    return data


def fix_var_name(var):
    """Fix variable name.

    Iris won't accept a non-standard standard_name,
      so you have to pass the long_name instead

    """

    if var == 'precipitation_minus_evaporation_flux':
        var = 'precipitation minus evaporation flux'
    
    return var


def main(inargs):
    """Run the program."""
 
    data_dict = {}
    for experiment in experiment_colors.keys():
        data_dict[(experiment, 'x_data')] = numpy.array([]) 
        data_dict[(experiment, 'y_data')] = numpy.array([])

    metadata_dict = {}
    for file_group in inargs.file_group:      
        xfile, xvar, yfile, yvar = file_group
        xvar = fix_var_name(xvar)
        yvar = fix_var_name(yvar)

        x_cube = iris.load_cube(xfile, xvar)
        
        y_cube = iris.load_cube(yfile, yvar)
        experiment, model = check_attributes(x_cube, y_cube)
        metadata_dict[xfile] = x_cube.attributes['history']
        metadata_dict[yfile] = y_cube.attributes['history']

        data_dict[(experiment, 'x_data')] = numpy.append(data_dict[(experiment, 'x_data')], get_data(x_cube.data, xvar))
        data_dict[(experiment, 'y_data')] = numpy.append(data_dict[(experiment, 'y_data')], get_data(y_cube.data, yvar))

    fig = plt.figure(figsize=(12,8))
    for experiment, color in experiment_colors.iteritems():
        x_data = data_dict[(experiment, 'x_data')]
        y_data = data_dict[(experiment, 'y_data')]

        if numpy.any(x_data):
            plt.scatter(x_data[::inargs.thin], y_data[::inargs.thin], facecolors='none', edgecolors=color, label=experiment)
            x_trend, y_trend = calc_trend(x_data, y_data, experiment)
            plt.plot(x_trend, y_trend, color=color)

    plt.legend(loc=4)
    plt.xlabel(get_label(xvar, inargs.pe_metric))
    plt.ylabel(get_label(yvar, inargs.pe_metric))
    plt.title(model)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')
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

    parser.add_argument("--file_group", type=str, action='append', default=[], nargs='*',
                        help="list that goes file, var, file, var...")
    parser.add_argument("--thin", type=int, default=1,
                        help="Stride for thinning the data (e.g. 3 will keep one-third of the data) [default: 1]")
    parser.add_argument("--pe_metric", type=str, choices=('amp', 'abs'), default='amp',
                        help="Precipitation minus evaporation metric")

    args = parser.parse_args()            
    main(args)
