"""
Filename:     calc_envelope.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Extracts the envelope of atmospheric wave packets
Reference:    Zimin et al. 2003. Mon. Wea. Rev. 131, 1011-1017

Updates | By | Description
--------+----+------------
12 June 2013 | Damien Irving | Initial version.

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

module_dir = os.path.join(os.environ['HOME'], 'data_processing')
sys.path.insert(0, module_dir)
import calc_rotation as rot


#########################
## Envelope extraction ##
#########################

def constants(inwave):
    """Define the constants required to perform the Fourier & Hilbert transforms"""

    N = len(inwave)
    l = numpy.arange(1, N+1)
    k = numpy.arange(-N/2.0 + 1.0, N/2.0 + 1.0) 

    return N, l, k


def fourier_transform(inwave):
    """Produce Fourier transform of input wave as per Zimin et al (2003, eq. 3)"""

    N, ll, kk = constants(inwave)
    inwave_hat = numpy.zeros(N, dtype=numpy.cfloat)
    for index in xrange(0,N):
        exptmp = numpy.exp(-2.0 * numpy.pi * complex(0,1) * kk[index] * ll / N)
        inwave_hat[index] = (1.0 / N) * numpy.sum(inwave * exptmp)

    return inwave_hat


def hilbert_transform(inwave_hat, kmin, kmax):
    """Apply the inverse Fourier transform to a selected band
       of the positive wavenumber half of the Fourier spectrum"""

    N, ll, kk = constants(inwave_hat)    
    selection = (kk < kmin) + (kk > kmax)
    ffilter = numpy.where(selection == True, 0, 1)

    envelope = numpy.zeros(N, dtype=numpy.cfloat)
    for index in xrange(0,N):
        exptmp_hat = numpy.exp(2.0 * numpy.pi * complex(0,1) * kk * ll[index] / N)
        envelope[index] = 2.0 * numpy.sum(inwave_hat * ffilter * exptmp_hat)

    return envelope
    

def envelope(inwave, kmin, kmax):
    """Extract the wave envelope"""
    
    inwave_hat = fourier_transform(inwave)
    envelope = hilbert_transform(inwave_hat, kmin, kmax)
    
    return numpy.abs(envelope) 


###########################
## Wind data preparation ##
###########################

def rotate_vwind(dataU, dataV, new_np):
    """Define the new meridional wind field, according to the 
    position of the new north pole."""

    if new_np == [90.0, 0.0]:
        new_vwind = dataV
    else:
        dataU_rot_uniform = switch_axes(dataU, new_np)
        dataV_rot_uniform = switch_axes(dataV, new_np)	
        new_vwind = calc_vwind(dataU_rot_uniform, dataV_rot_uniform, new_np) 

    return new_vwind    
        

def reset_axes(data_rot, grid, new_north_pole):
    """Take data on a rotated spherical grid and return it
    to a regular grid with the north pole at 90N, 0E."""

    if new_north_pole == [90.0, 0.0]:
        data = data_rot
    else:
        data = switch_axes(data_rot, grid, invert=True)
	
    return data


def switch_axes(data, new_np, invert=False):
    """Take some data, rotate the axes (according to the position
    of the new north pole), and regrid to uniform grid """

    psi = 0.0
    phi, theta = rot.north_pole_to_rotation_angles(new_np[0], new_np[1])   

    lats = data.getLatitude()[:]
    lons = data.getLongitude()[:]

    lats_rot, lons_rot = rot.rotate_spherical(lats, lons, phi, theta, psi, invert=invert)
    
    lat_axis_rot = cdms2.createAxis(lats_rot)
    lat_axis_rot.designateLatitude()
    lon_axis_rot = cdms2.createAxis(lons_rot)
    lon_axis_rot.designateLongitude()

    #grid_rot = cdms2.createGenericGrid(lats_rot, lons_rot)

    if (re.match('^t', data.getOrder())):
        axis_list = [data.getTime(), lat_axis_rot, lon_axis_rot]
        order = 'tyx'
    else: 
        axis_list = [lat_axis_rot, lon_axis_rot]
	order = 'yx'    
    data_rot = cdms2.createVariable(data[:], axes=axis_list, order=order)  #grid=grid_rot

    data_rot_uniform = nio.regrid_uniform(data_rot, data.getGrid())
    
    hello
    
    return data_rot_uniform


def calc_vwind(dataU, dataV, new_np, old_np=(90.0, 0.0)):
    """Calculate the new meridional wind field, according to the
    new position of the north pole"""
    
    lats = dataU.getLatitude()[:]
    lons = dataU.getLongitude()[:]
    theta = numpy.zeros([len(lats), len(lons)])
    for iy, lat in enumerate(lats):
        for ix, lon in enumerate(lons):
	    theta[iy, ix] = rotation_angle(old_np[0], old_np[1], new_np[0], new_np[1], lat, lon)
    
    wsp = numpy.sqrt(numpy.square(dataU) + numpy.square(dataV))
    alpha = numpy.arctan2(dataV / dataU) - theta
    dataV_rot = wsp * numpy.sin(alpha)

    return dataV_rot  


##########
## Main ##
##########

def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indataU = nio.InputData(inargs.infileU, inargs.variableU, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    indataV = nio.InputData(inargs.infileV, inargs.variableV, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude', 'grid']))
    
    vwind = rotate_vwind(indataU, indataV, inargs.north_pole)

    # Extract the wave envelope #

    outdata_rot = numpy.zeros(list(indata.data.shape))
    ntime, nlat, nlon = indata.data.shape
    kmin, kmax = inargs.wavenumbers
    
    for time in xrange(0, ntime):
        for lat in xrange(0, nlat):
            outdata_rot[time, lat, :] = envelope(vwind[time, lat, :], kmin, kmax)
    
    # Write output file #

    outdata = reset_axes(outdata_rot, indataV.getGrid(), inargs.north_pole)

    var_atts = {'id': 'env',
                'name': 'Amplitude of wave envelope',
                'long_name': 'Extracted envelope of atmospheric wave packet, obtained using Hiltbert transform',
                'units': 'm s-1',
                'history': 'Ref: Zimin et al. 2003. Mon. Wea. Rev. 131, 1011-1017. Wavenumber range: %s to %s' %(kmin, kmax)}

    indata_list = [indataU, indataV,]
    outdata_list = [outdata,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [indataU.data.getAxisList(),]

    nio.write_netcdf(inargs.outfile, 'Amplitude of wave envelope', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
reference:
  Zimin et al. 2003. Mon. Wea. Rev. 131, 1011-1017

example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_envelope.py 
  /work/dbirving/datasets/Merra/data/va_Merra_250hPa_daily_native.nc va 
  /work/dbirving/processed/indices/data/env_Merra_250hPa_daily_native.nc

note:

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Extract envelope of atmospheric wave packets'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infileU", type=str, help="Input file name, containing the zonal wind")
    parser.add_argument("variableU", type=str, help="Input file variable, for the zonal wind")
    parser.add_argument("infileV", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variableV", type=str, help="Input file variable, for the meridional wind")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--wavenumbers", type=int, nargs=2, metvar=('LOWER', 'UPPER'), default=[2, 4],
                        help="Wavenumber range [default = (2, 4)]")			
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
                        help="Uniform regular grid to regrid data to [default = None]")
    parser.add_argument("--north_pole", type=float, nargs=2, metavar=('LAT', 'LON'), default=[90.0, 0.0],
                        help="Location of north pole [default = (90, 0)]")	
    
    args = parser.parse_args()            


    print 'Input files: ', args.infileU, args.infileV
    print 'Output file: ', args.outfile  

    main(args)
