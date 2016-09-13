"""
Filename:     calc_global_metric.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate global metric

"""

# Import general Python modules

import sys, os, pdb
import argparse
import numpy
import iris
import matplotlib.pyplot as plt
import seaborn

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
    import convenient_universal as uconv
    import timeseries
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

basins = {'atlantic': 2, 
          'pacific': 3,
          'indian': 5}

experiment_names = {('CSIRO-Mk3-6-0', 'historicalMisc', 3): 'noAA',
                    ('CSIRO-Mk3-6-0', 'historicalMisc', 4): 'AA',
                    ('IPSL-CM5A-LR', 'historicalMisc', 3): 'AA',
                    ('IPSL-CM5A-LR', 'historicalMisc', 4): 'noAA'}

experiment_colors = {'noAA': 'r',
                     'AA': 'b',
                     'historical': 'y',
                     'piControl': '0.5',
                     'Argo': 'g',
                     '1pctCO2': 'k'}


def read_basin(basin_file):
    """Read the optional basin file."""

    if basin_file:
        basin_cube = iris.load_cube(basin_file)
    else:
        basin_cube = None

    return basin_cube


def set_attributes(inargs, data_cube, area_cube):
    """Set the attributes for the output cube."""
    
    atts = data_cube.attributes

    infile_history = {}
    infile_history[inargs.infile] = data_cube.attributes['history']
 
    if area_cube:                  
        infile_history[inargs.area_file] = area_cube.attributes['history']
    
    atts['history'] = gio.write_metadata(file_info=infile_history)

    return atts


def calc_trend(x_data, y_data, experiment):
    """Calculate linear trend.
    polyfit returns [a, b] corresponding to y = a + bx
    """

    x_unmasked = x_data.compressed()
    y_unmasked = y_data.compressed()

    a_coefficient, b_coefficient = numpy.polynomial.polynomial.polyfit(x_unmasked, y_unmasked, 1)
    step = x_data.max() / 50.
    x_trend = numpy.arange(x_data.min(), x_data.max(), step)
    y_trend = a_coefficient + b_coefficient * x_trend
    print experiment, 'trend:', b_coefficient

    return x_trend, y_trend


def calc_zonal_stats(cube, basin_array, basin_name):
    """Calculate the zonal mean climatology and trend for a given ocean basin."""

    cube.data.mask = numpy.where((cube.data.mask == False) & (basin_array == basins[basin_name]), False, True)

    zonal_mean_cube = cube.collapsed('longitude', iris.analysis.MEAN)
    zonal_mean_cube.remove_coord('longitude')

    zonal_climatology = zonal_mean_cube.collapsed('time', iris.analysis.MEAN)
    zonal_trend = timeseries.calc_trend(zonal_mean_cube, running_mean=True, per_yr=True, remove_scaling=False)

    return zonal_climatology.data, zonal_trend * 50


def get_experiment_details(cube):
    """Get the experiment details."""

    model = cube.attributes['model_id']
    experiment = cube.attributes['experiment_id']
    physics = cube.attributes['physics_version']

    atts = (model, experiment, float(physics))

    if atts in experiment_names.keys():
        experiment = experiment_names[atts]

    return model, experiment


def main(inargs):
    """Run the program."""

    data_dict = {}
    for experiment in experiment_colors.keys():
        data_dict[(experiment, 'x_data')] = numpy.ma.array([]) 
        data_dict[(experiment, 'y_data')] = numpy.ma.array([])

    metadata_dict = {}
    for data_file, basin_file in inargs.file_pair:
        try:
            time_constraint = gio.get_time_constraint(inargs.time)
        except AttributeError:
            time_constraint = iris.Constraint()

        with iris.FUTURE.context(cell_datetime_objects=True):
            cube = iris.load_cube(data_file, 'sea_surface_salinity' & time_constraint)
    
        basin_cube = read_basin(basin_file) 
        ndim = cube.ndim
        basin_array = uconv.broadcast_array(basin_cube.data, [ndim - 2, ndim - 1], cube.shape) 

        metadata_dict[data_file] = cube.attributes['history']
        metadata_dict[basin_file] = basin_cube.attributes['history']

        model, experiment = get_experiment_details(cube)

        for basin in basins.keys():
            zonal_climatology, zonal_trends = calc_zonal_stats(cube.copy(), basin_array, basin)
            data_dict[(experiment, 'x_data')] = numpy.ma.append(data_dict[(experiment, 'x_data')], zonal_climatology)
            data_dict[(experiment, 'y_data')] = numpy.ma.append(data_dict[(experiment, 'y_data')], zonal_trends)


    fig = plt.figure(figsize=(12,8))
    for experiment, color in experiment_colors.iteritems():
        x_data = data_dict[(experiment, 'x_data')]
        y_data = data_dict[(experiment, 'y_data')]

        if numpy.any(x_data):
            plt.scatter(x_data[::inargs.thin], y_data[::inargs.thin], facecolors='none', edgecolors=color, label=experiment)
            if experiment in ['AA', 'noAA']:
                x_trend, y_trend = calc_trend(x_data, y_data, experiment)
                plt.plot(x_trend, y_trend, color=color)

    plt.legend(loc=4)
    plt.xlabel('Climatological mean salinity')
    plt.ylabel('Salinity trend (per 50 years)')
    plt.title(model)

    # Write output
    plt.savefig(inargs.outfile, bbox_inches='tight')
    gio.write_metadata(inargs.outfile, file_info=metadata_dict)



if __name__ == '__main__':

    extra_info =""" 
author:
    Damien Irving, irving.damien@gmail.com

"""

    description='Calculate a global metric'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--file_pair", type=str, action='append', default=[], nargs=2,
                        metavar=('DATA_FILE', 'BASIN_FILE'), help="data/basin file pair")

    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period [default = entire]")
    parser.add_argument("--thin", type=int, default=1,
                        help="Stride for thinning the data (e.g. 3 will keep one-third of the data) [default: 1]")

    args = parser.parse_args()            

    main(args)
