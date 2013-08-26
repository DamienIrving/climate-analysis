"""
Filename:     calc_rotation_reset.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Take data on a rotated grid and reset the axes to
              a north pole of [0,90]

"""

import sys
import os
import argparse

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio
import coordinate_rotation as rot


def reset_axes(data_rot, lats, lons, new_north_pole):
    """Take data on a rotated spherical grid and return it
    to a regular grid with the north pole at 90N, 0E."""

    if new_north_pole == [90.0, 0.0]:
        data = data_rot
    else:
        data = rot.switch_axes(data_rot, lats, lons, new_north_pole, invert=True)
	
    return data


def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    
    # Rotate the axes #

    outdata = rot.reset_axes(indata, indata.data.getLatitude()[:], indata.data.getLongitude()[:], inargs.north_pole)
    
    # Write output file #

    var_atts = {'id': inargs.variable,
                'name': indata.name,
                'long_name': indata.long_name,
                'units': indata.units,
                'history': 'Coordinate axes reset from a north pole of %s N, %s E to 90 N, 0 E'  %(str(inargs.north_pole[0]), str(inargs.north_pole[1]))}

    indata_list = [indata,]
    outdata_list = [outdata,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [indata.data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, 'Reset coordinate axes', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_envelope.py 
  /work/dbirving/processed/indices/data/vrot-env_Merra_250hPa_monthly_y73x144_np30-270.nc env
  30 270
    
author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Extract envelope of atmospheric wave packets'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    parser.add_argument("north_pole", type=float, nargs=2, metavar=('LAT', 'LON'),
                        help="Location of north pole")

    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region [default = entire]")
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Longitude range [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")

    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
