"""
Filename:     calc_envelope.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Extracts the envelope of atmospheric wave packets
Reference:    Zimin et al. 2003. Mon. Wea. Rev. 131, 1011-1017

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
import coordinate_rotation as crot

module_dir2 = os.path.join(os.environ['HOME'], 'visualisation')
sys.path.insert(0, module_dir2)
import plot_map


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


def apply_lon_filter(data, lon_bounds):
    """Set all values outside of the specified longitude range [lon_bounds[0], lon_bounds[1]] to zero."""
    
    # Convert to common bounds (0, 360) #
 
    lon_min = crot.adjust_lon_range(lon_bounds[0], radians=False, start=0.0)
    lon_max = crot.adjust_lon_range(lon_bounds[1], radians=False, start=0.0)
    lon_axis = crot.adjust_lon_range(data.getLongitude()[:], radians=False, start=0.0)

    # Make required values zero #
    
    ntimes, nlats, nlons = data.shape
    lon_axis_tiled = numpy.tile(lon_axis, (ntimes, nlats, 1))
    
    new_data = numpy.where(lon_axis_tiled < lon_min, 0.0, data)
    
    return numpy.where(lon_axis_tiled > lon_max, 0.0, new_data)


def main(inargs):
    """Run the program."""
    
    # Read input data #
    
    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'latitude']))
    
    assert indata.data.getOrder() == 'tyx', \
    'This script only works if the input data has a time, latitude and longitude axis'
    
    # Apply longitude filter (i.e. set unwanted longitudes to zero) #
    
    data_filtered = apply_lon_filter(indata.data, inargs.longitude) if inargs.longitude else indata.data
 
    # Extract the wave envelope #
    
    kmin, kmax = inargs.wavenumbers
    outdata = numpy.apply_along_axis(envelope, 2, data_filtered, kmin, kmax)
    
    # Write output file #

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
  /work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360_np30-270.nc vrot
  /work/dbirving/datasets/Merra/data/processed/vrot-env-w567_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360_np30-270.nc
  --longitude 195 340

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Extract envelope of atmospheric wave packets'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name, containing the meridional wind")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")

    parser.add_argument("--wavenumbers", type=int, nargs=2, metavar=('LOWER', 'UPPER'), default=[5, 7],
                        help="Wavenumber range [default = (5, 7)]. The upper and lower values are included (i.e. default selection is 2, 3, 4).")			
    parser.add_argument("--latitude", type=float, nargs=2, metavar=('START', 'END'),
                        help="Latitude range over which to extract waves [default = entire]")
    parser.add_argument("--longitude", type=float, nargs=2, metavar=('START', 'END'), default=None,
                        help="Longitude range over which to extract waves [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period [default = entire]")
  
    args = parser.parse_args()            

    print 'Input files: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
