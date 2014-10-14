# Import general Python modules #

import os, sys, pdb

import numpy
import pandas
import argparse


# Import my modules #

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'phd':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)

try:
    import convenient_anaconda as aconv
except ImportError:
    raise ImportError('Must run this script from anywhere within the phd git repo')


# Define functions #

def normalise_series(series):
    """Normalise a Pandas data series by subtracting the
    mean and dividing by the stdev"""

    ave = series.mean()
    stdev = series.std()
    
    return (series - ave) / stdev

     
def scatter_plot(x_data, y_data, outfile, c_data=None, normalised=False, thin=1, trend=False, cmap='jet'):
    """Create scatterplot"""

    plt.figure()

    if normalised:
        plt.axhline(y=0, linestyle='-', color='0.5')
        plt.axvline(x=0, linestyle='-', color='0.5')

    x = x_data[::thin]
    y = y_data[::thin]
    c = c_data[::thin] if c_data else 'k'
    
    plt.scatter(x, y, c=c, cmap=cmap)

    if trend:
        p = numpy.polyfit(x, y, 1)
        print p
        plt.plot(x, p[0]*x+p[1], 'r')
    
    plt.xlabel("Blah")
    plt.ylabel("Blah")

    plt.savefig(outfile)


def main(inargs):
    """Run program."""

    # Read input data into a single pandas DataFrame

    x_dataframe, x_metadata = aconv.wavestats_to_df(inargs.xfile, [inargs.xvar])
    y_dataframe, y_metadata = aconv.wavestats_to_df(inargs.yfile, [inargs.yvar])
    dataframe_list = [y_dataframe]
    metadata_list = [x_metadata, y_metadata]

    if inargs.colours:
        c_dataframe, c_metadata = aconv.wavestats_to_df(inargs.colours[0], [inargs.colours[1]])
        dataframe_list.append(c_dataframe)
        metadata_list.append(c_metadata)
        
    dataframe =  x_dataframe.join(dataframe_list)

    # Normalise data 

    if inargs.normalise:
        target_xvar = inargs.xvar+'_norm'
        target_yvar = inargs.yvar+'_norm'
        dataframe[target_xvar] = normalise_series(dataframe[inargs.xvar])
        dataframe[target_yvar] = normalise_series(dataframe[inargs.yvar])
    else:
        target_xvar = inargs.xvar
        target_yvar = inargs.yvar

    # Filter data

    if inargs.filter:
        

    # Generate plot
    
    scatter_plot(dataframe[target_xvar], dataframe[target_yvar], 
                 inargs.ofile, c_data=None, 
                 normalised=inargs.normalise, thin=inargs.thin, 
                 trend=inargs.trend_line, cmap=inargs.cmap)

    gio.write_metadata(inargs.ofile, file_info=metadata_list)












if __name__ == '__main__':

    extra_info =""" 
example:
  env_amp_mean

author:
    Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Create a scatterplot'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # Required data
    parser.add_argument("xfile", type=str, help="Input file for the x-axis")
    parser.add_argument("xvar", type=str, help="Variable name in x-axis input file")
    parser.add_argument("yfile", type=str, help="Input file for the x-axis")
    parser.add_argument("yvar", type=str, help="Variable name in x-axis input file")
    parser.add_argument("ofile", type=str, help="Output file name")
    
    # Optional data
    parser.add_argument("--colour", type=str, nargs=2, metavar=('FILE', 'VAR'),  
                        help="Input file and variable for colouring the dots")
 
    # Data options
    parser.add_argument("--filter", type=str, nargs=2, metavar=('METRIC', 'THRESHOLD'), default=None, 
                        help="Remove values where metric is below threshold. Threshold can be percentile (e.g. 90pct) or raw value.")
    parser.add_argument("--normalise", action="store_true", default=False,
                        help="switch for normalising the x and y input data [default: False]")
    parser.add_argument("--trend_line", action="store_true", default=False,k
                        help="switch for a linear line of best fit [default: False]")


    args = parser.parse_args()            
    main(args)
