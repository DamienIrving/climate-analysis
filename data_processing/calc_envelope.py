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

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio

module_dir = os.path.join(os.environ['HOME'], 'data_processing')
sys.path.insert(0, module_dir)
import calc_rotation as rot


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


def rotate_meridional_wind(dataU, dataV, new_north_pole):
    """Define the new meridional wind field, according to the 
    position of the new north pole."""

    if new_north_pole == [90.0, 0.0]:
        new_vwind = dataV
    else:
        
        # Reset axes of input data (i.e. get dataU_rot, dataV_rot) #
        psi = 0.0
        phi, theta = rot.north_pole_to_rotation_angles(new_north_pole[0], new_north_pole[1])   
        
        lats = dataU.getLatitude()[:]
        lons = dataU.getLongitude()[:]
        lats_rot, lons_rot = rot.geographic_to_rotated_spherical(lats, lons, phi, theta, psi)

        lat_axis_rot = cdms2.createAxis(lats_rot).designateLatitude()
        lon_axis_rot = cdms2.createAxis(lons_rot).designateLongitude()

        dataU_rot = cdms2.createVariable(dataU[:], axes=[dataU.getTime(), lat_axis_rot, lon_axis_rot])
        dataV_rot = cdms2.createVariable(dataV[:], axes=[dataV.getTime(), lat_axis_rot, lon_axis_rot])
     
        # Interpolate to a regular grid (SCRIP regridder)#

       
        # Determine new meridional wind #
        


    return new_vwind    
        

def reset_axes(data_rot, lats_orig, lons_orig, new_north_pole):
    """Take data on a rotated spherical grid and return it
    to a regular grid with the north pole at 90N, 0E."""

    if new_north_pole == [90.0, 0.0]:
        data = data_rot
    else:

	# Reset axes #
	lats_rot = data.getLatitude()[:]
	lons_rot = data.getLongitude()[:]
	lats_reset, lons_reset = rotated_to_geographic_spherical(lats_rot, lons_rot, phir, thetar, psir)

	# Interpolate back to original grid (SCRIP regridder) #


    return data


def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indataU = nio.InputData(inargs.infileU, inargs.variableU, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude']))
    indataV = nio.InputData(inargs.infileV, inargs.variableV, 
                           **nio.dict_filter(vars(inargs), ['time', 'region', 'latitude', 'longitude']))
    
    meridional_wind = rotate_meridional_wind(indataU, indataV, inargs.north_pole)

    # Extract the wave envelope #

    outdata_rot = numpy.zeros(list(indata.data.shape))
    ntime, nlat, nlon = indata.data.shape
    kmin, kmax = inargs.wavenumbers
    
    for time in xrange(0, ntime):
        for lat in xrange(0, nlat):
            outdata_rot[time, lat, :] = envelope(meridional_wind[time, lat, :], kmin, kmax)
    
    # Write output file #

    outdata = reset_axes(outdata_rot, indataV.getLatitude(), indataV.getLongitude(), inargs.north_pole)

    var_atts = {'id': 'env',
                'name': 'Amplitude of wave envelope',
                'long_name': 'Extracted envelope of atmospheric wave packet, obtained using Hiltbert transform',
                'units': 'm s-1',
                'history': 'Ref: Zimin et al. 2003. Mon. Wea. Rev. 131, 1011-1017. Wavenumber range: %s to %s' %(kmin, kmax)}

    indata_list = [indata,]
    outdata_list = [outdata,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [indata.data.getAxisList(),]

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
    parser.add_argument("--north_pole", type=float, nargs=2, metavar=('LAT', 'LON'), default=[90.0, 0.0],
                        help="Location of north pole [default = (90, 0)]")		
    
    args = parser.parse_args()            


    print 'Input files: ', args.infileU, args.infileV
    print 'Output file: ', args.outfile  

    main(args)
