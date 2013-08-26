"""
Filename:     calc_vwind_rotation.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculate meridional wind according to a new coordinate axis 

"""

import sys
import os

import argparse
import numpy
import re

import cdms2
import css

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio
import coordinate_rotation as rot



def rotate_vwind(dataU, dataV, new_np, anomaly=None):
    """Define the new meridional wind field, according to the 
    position of the new north pole."""

    assert isinstance(dataU, nio.InputData)
    assert isinstance(dataV, nio.InputData)

    if new_np == [90.0, 0.0]:
        new_vwind_data = dataV.data
    else:
        lats = dataU.data.getLatitude()[:]
	lons = dataU.data.getLongitude()[:]
	dataU_rot = rot.switch_axes(dataU.data[:], lats, lons, new_np)
        dataV_rot = rot.switch_axes(dataV.data[:], lats, lons, new_np)	
        new_vwind = calc_vwind(dataU_rot, dataV_rot, lats, lons, new_np) 

    new_vwind = cdms2.createVariable(new_vwind, grid=dataU.data.getGrid(), axes=dataU.data.getAxisList())
    if anomaly:
        date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
        if re.search(date_pattern, anomaly[0]) and re.search(date_pattern, anomaly[1]):
            period = anomaly
        else:
            print """Input anomaly base period either invalid format or 'all' - base climatology is entire period"""
            period = None
	new_vwind = nio.temporal_aggregation(new_vwind, 'ANNUALCYCLE', 'anomaly', time_period=period)  #hard wired to annual cycle

    return new_vwind    
        

def calc_vwind(dataU, dataV, lats, lons, new_np, old_np=(90.0, 0.0)):
    """Calculate the new meridional wind field, according to the
    new position of the north pole"""
    
    theta = rot.rotation_angle(old_np[0], old_np[1], new_np[0], new_np[1], lats, lons)
    theta = numpy.resize(theta, numpy.shape(dataU))
    
    wsp = numpy.sqrt(numpy.square(dataU) + numpy.square(dataV))
    alpha = numpy.arctan2(dataV, dataU) - theta
    dataV_rot = wsp * numpy.sin(alpha)

    return dataV_rot  
    

def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indataU = nio.InputData(inargs.infileU, inargs.variableU, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    indataV = nio.InputData(inargs.infileV, inargs.variableV, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    
    # Calulate the new vwind #

    vwind = rotate_vwind(indataU, indataV, inargs.north_pole, anomaly=inargs.anomaly)

    # Write the output file #

    var_atts = {'id': 'vrot',
                'name': 'Rotated meridional wind',
                'long_name': 'Meridional wind on a rotated coordinate grid (i.e. the poles are shifted)',
                'units': 'm s-1',
                'history': 'Location of north pole: %s N, %s E' %(str(inargs.north_pole[0]), str(inargs.north_pole[1]))}

    indata_list = [indataU, indataV,]
    outdata_list = [vwind,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [vwind.getAxisList(),]

    nio.write_netcdf(inargs.outfile, 'Rotated meridional wind', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_vwind_rotation.py 
  /work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc ua
  /work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc va 
  /work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly_y73x144_np30-270.nc
  --north_pole 30 270

required improvements:
  1. There might be some funny point in the grid switch that need to be looked at. This
     might be able to be fixed by using a higher resolution grid
  2. Testing indicates that the regridding is accurate everywhere except at 
     the poles. This may relate to the problems with csc2s and css2c, which
     I logged as an issue on the UVCDAT Github page. They responded that it's not
     their package, so I might need to contact someone else.
  3. Look for opportunities to process data as multidimensional arrays, instead
     of using mesh/flatten or looping.

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Rotate grid and calculate new meridional wind'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infileU", type=str, help="Input file name, containing the zonal wind")
    parser.add_argument("variableU", type=str, help="Input file variable, for the zonal wind")
    parser.add_argument("infileV", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variableV", type=str, help="Input file variable, for the meridional wind")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region [default = entire]")
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Longitude range [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")
    parser.add_argument("--grid", type=float, nargs=6, metavar=('START_LAT', 'NLAT', 'DELTALAT', 'START_LON', 'NLON', 'DELTALON'),
                        default=(-90.0, 73, 2.5, 0.0, 144, 2.5),
                        help="Uniform regular grid to regrid data to [default = 2.5 by 2.5 deg]")
    parser.add_argument("--north_pole", type=float, nargs=2, metavar=('LAT', 'LON'), default=[90.0, 0.0],
                        help="Location of north pole [default = (90, 0)] - (30, 270) for PSA pattern")
    parser.add_argument("--anomaly", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="""Extract envelope from anomaly timeseries (calculated from annual cycle monthly climatology). Each date can be 'all' or 'YYYY-MM-DD' [default=False]""") 	
    
    args = parser.parse_args()            


    print 'Input files: ', args.infileU, args.infileV
    print 'Output file: ', args.outfile  

    main(args)
