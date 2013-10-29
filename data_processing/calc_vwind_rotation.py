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

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio
import coordinate_rotation as rot


def rotate_vwind(dataU, dataV, new_np, pm_point, res=1.0, anomaly=None):
    """Define the new meridional wind field, according to the 
    position of the new north pole.
    
    FIX: Need a more general method of dealing with input axes
    (e.g. what if there is multiple levels)
    
    """

    assert isinstance(dataU, cdms2.tvariable.TransientVariable)
    assert isinstance(dataV, cdms2.tvariable.TransientVariable)

    assert 'yx' in dataU.getOrder(), \
    'Input data must have a latitude and longitude axis'

    lat_axis = dataU.getLatitude()[:]
    lon_axis = dataU.getLongitude()[:]
    lats, lons = nio.coordinate_pairs(lat_axis, lon_axis)

    # Calculate new vwind on the native grid

    vwind_rot = calc_vwind(dataU, dataV, lat_axis, lon_axis, new_np) 

    if anomaly:
        date_pattern = '([0-9]{4})-([0-9]{1,2})-([0-9]{1,2})'
        if re.search(date_pattern, anomaly[0]) and re.search(date_pattern, anomaly[1]):
            period = anomaly
        else:
            print """Input anomaly base period either invalid format or 'all' - base climatology is entire period"""
            period = None
	
	vwind_rot = cdms2.createVariable(vwind_rot, grid=dataU.getGrid(), axes=dataU.getAxisList())
	vwind_rot = nio.temporal_aggregation(vwind_rot, 'ANNUALCYCLE', 'anomaly', time_period=period)  #hard wired to annual cycle

    # Rotate the coordinate axis to desired grid

    nlats = int((180.0 / res) + 1)
    nlons = int(360.0 / res)
    grid = cdms2.createUniformGrid(-90.0, nlats, res, 0.0, nlons, res)
    lat_axis_rot = grid.getLatitude()
    lon_axis_rot = grid.getLongitude()
     
    vwind_rot_switch = rot.switch_regular_axes(vwind_rot, lats, lons, lat_axis_rot[:], lon_axis_rot[:], new_np, pm_point=pm_point, invert=True)
    
    if 't' in dataU.getOrder():
        axis_list = [dataU.getTime(), lat_axis_rot, lon_axis_rot]
    else: 
        axis_list = [lat_axis_rot, lon_axis_rot]
    
    vwind_rot_swtich = cdms2.createVariable(vwind_rot_switch, grid=grid, axes=axis_list)
    

    return vwind_rot, vwind_rot_swtich    
        

def calc_vwind(dataU, dataV, lat_axis, lon_axis, new_np, old_np=(90.0, 0.0)):
    """Calculate the new meridional wind field, according to the
    new position of the north pole"""
    
    lats, lons = nio.coordinate_pairs(lat_axis, lon_axis) 
    theta = rot.rotation_angle(old_np[0], old_np[1], new_np[0], new_np[1], 
                               lats, lons, reshape=[len(lat_axis), len(lon_axis)])
    theta = numpy.resize(theta, numpy.shape(dataU))
    
    dataV_rot = vwind_trig(dataU, dataV, theta) 

    return dataV_rot  
    
    
def vwind_trig(u, v, theta):
    """Do the trigonometry required to calculate new meridional
    wind from the old one.
    
    u      -  zonal wind data
    v      -  meridional wind data
    theta  -  angle through which the x/y coordinate axes must be rotated 
              (measured anticlockwise starting on the original positive x-axis 
	      (i.e. at 90 deg in a 360 circle))
    phi    -  angle that the wind vector makes with original positive x-axis
              (measured anticlockwise starting on the original positive x-axis)
    alpha  -  angle that the wind vector makes with the new positive x-axis
              (measured anticlockwise starting on the new positive x-axis)
               
    """

    wsp = numpy.sqrt(numpy.square(numpy.array(u)) + numpy.square(numpy.array(v)))
    phi = numpy.arctan2(v, u)
    alpha = phi - theta
    
    return wsp * numpy.sin(alpha)

     
def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indataU = nio.InputData(inargs.infileU, inargs.variableU, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    indataV = nio.InputData(inargs.infileV, inargs.variableV, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    
    # Calulate the new vwind #

    vwind_rot, vwind_rot_switch = rotate_vwind(indataU.data, indataV.data, inargs.north_pole, inargs.pm, anomaly=inargs.anomaly)

    # Write the output file #

    if inargs.anomaly:
        standard_name = 'rotated_meridional_wind_anomaly'
	long_name = 'Meridional wind anomaly on a rotated coordinate grid (but the poles have not yet been shifted)'
        clim = 'Base period: %s - %s' %(inargs.anomaly[0], inargs.anomaly[1])
    else:
        standard_name = 'rotated_meridional_wind'
	long_name = 'Meridional wind on a rotated coordinate grid (but the poles have not yet been shifted)'
	clim = ''  

    history = 'Location of north pole: %s N, %s E. Prime meridian point = %s N, %s E. %s' %(str(inargs.north_pole[0]), str(inargs.north_pole[1]), 
											    str(inargs.pm[0]), str(inargs.pm[1]), clim)

    vrot_atts = {'id': 'vrot',
                 'standard_name': standard_name,
                 'long_name': long_name,
                 'units': indataU.data.units,
                 'history': history}
											    
    outdata_list = [vwind_rot,] if inargs.noswitch else [vwind_rot_switch,]
    outvar_atts_list = [vrot_atts,]
    outvar_axes_list = [vwind_rot.getAxisList(),] if inargs.noswitch else [vwind_rot_switch.getAxisList(),]
 
    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     indataU.global_atts, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_vwind_rotation.py 
  /work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc ua
  /work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc va 
  /work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly-anom-wrt-all_y181x360_np30-270.nc
  --north_pole 30 270
  --anomaly all all
  --grid -90.0 181 1.0 0.0 360 1.0

required improvements:
  1. There might be some funny point in the grid switch that need to be looked at. This
     might be able to be fixed by using a higher resolution grid.

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
                        #default=(-90.0, 73, 2.5, 0.0, 144, 2.5),
                        help="Uniform regular grid to regrid data to [default = None]")
    parser.add_argument("--north_pole", type=float, nargs=2, metavar=('LAT', 'LON'), default=[90.0, 0.0],
                        help="Location of north pole [default = (90, 0)] - (30, 270) for PSA pattern")
    parser.add_argument("--pm", type=float, nargs=2, metavar=('LAT', 'LON'), default=(0.0, 0.0),
                        help="Location of the prime meridian point")	
    parser.add_argument("--anomaly", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'), default=None,
                        help="""Output the anomaly timeseries (calculated from annual cycle monthly climatology). Each date can be 'all' or 'YYYY-MM-DD' [default=False]""")
    parser.add_argument("--noswitch", action="store_true", default=False,
                        help="Switch for outputing the vwind on the original grid, as opposed to the switched (or rotated) grid [default: False]") 	
    
    args = parser.parse_args()            


    print 'Input files: ', args.infileU, args.infileV
    print 'Output file: ', args.outfile  

    main(args)
