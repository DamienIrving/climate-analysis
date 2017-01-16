"""
Filename:     calc_climate_index.py
Author:       Damien Irving, irving.damien@gmail.com
Description:  Calculate common climate indices

"""

# Import general Python modules

import sys, os
import argparse
import numpy
import xarray
import pdb

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
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')


# Define functions

def calc_asl(ifile, var_id, ofile):
    """Calculate the Amundsen Sea Low index.

    Ref: Turner et al (2013). The Amundsen Sea Low. 
      International Journal of Climatology. 33(7), 1818-1829
      doi:10.1002/joc.3558.

    Expected input: Mean sea level pressure data.

    Concept: Location and value of minimum MSLP is the region
      bounded by 60-75S and 180-310E.   

    """

    # Read data
    dset_in = xarray.open_dataset(ifile)
    gio.check_xarrayDataset(dset_in, var_id)

    south_lat, north_lat, west_lon, east_lon = gio.regions['asl']
    darray = dset_in[var_id].sel(latitude=slice(south_lat, north_lat), 
                                 longitude=slice(west_lon, east_lon))

    assert darray.dims == ('time', 'latitude', 'longitude'), \
    "Order of the data must be time, latitude, longitude"

    # Get axis information
    lat_values = darray['latitude'].values
    lon_values = darray['longitude'].values
    lats, lons = uconv.coordinate_pairs(lat_values, lon_values)

    # Reshape data
    ntimes, nlats, nlons = darray.values.shape
    darray_reshaped = numpy.reshape(darray.values, (ntimes, nlats*nlons))

    # Get the ASL index info (min value for each timestep and its lat/lon)
    min_values = numpy.amin(darray_reshaped, axis=1)
    min_indexes = numpy.argmin(darray_reshaped, axis=1)
    min_lats = numpy.take(lats, min_indexes)
    min_lons = numpy.take(lons, min_indexes)

    # Write the output file
    d = {}
    d['time'] = darray['time']
    d['asl_value'] = (['time'], min_values)
    d['asl_lat'] = (['time'], min_lats)
    d['asl_lon'] = (['time'], min_lons)    
    dset_out = xarray.Dataset(d)
    
    ref = 'Ref: Turner et al (2013). Int J Clim. 33, 1818-1829. doi:10.1002/joc.3558.'
    dset_out['asl_value'].attrs = {'long_name': 'asl_minimum_pressure',
                                   'standard_name': 'asl_minimum_pressure',
                                   'units': 'Pa',
                                   'notes': ref}
    dset_out['asl_lat'].attrs = {'long_name': 'asl_latitude',
                                 'standard_name': 'asl_latitude',
                                 'units': 'degrees_north',
                                 'notes': ref}
    dset_out['asl_lon'].attrs = {'long_name': 'asl_longitude',
                                 'standard_name': 'asl_longitude',
                                 'units': 'degrees_east',
                                 'notes': ref}
    
    gio.set_global_atts(dset_out, dset_in.attrs, {ifile: dset_in.attrs['history']})
    dset_out.to_netcdf(ofile, format='NETCDF3_CLASSIC')


def calc_nino(index, ifile, var_id, base_period, ofile):
    """Calculate a Nino index.

    Expected input: Sea surface temperature data.

    """

    index_name = 'nino'+index[4:]

    # Read the data
    dset_in = xarray.open_dataset(ifile)
    gio.check_xarrayDataset(dset_in, var_id)

    # Calculate the index
    south_lat, north_lat, west_lon, east_lon = gio.regions[index_name]
    darray = dset_in[var_id].sel(latitude=slice(south_lat, north_lat), 
             longitude=slice(west_lon, east_lon)).mean(dim=['latitude', 'longitude'])
    
    groupby_op = get_groupby_op(darray['time'].values)
    clim = darray.sel(time=slice(base_period[0], base_period[1])).groupby(groupby_op).mean()
    anom = darray.groupby(groupby_op) - clim

    # Write output
    if ofile:
	d = {}
	d['time'] = darray['time']
	d[index_name] = (['time'], anom.values) 
	dset_out = xarray.Dataset(d)

	hx = 'lat: %s to %s, lon: %s to %s, base: %s to %s' %(south_lat, north_lat,
                                                              west_lon, east_lon,
                                                              base_period[0], base_period[1])

	dset_out[index_name].attrs = {'long_name': index_name+'_index',
                                      'standard_name': index_name+'_index',
                                      'units': 'Celsius',
                                      'notes': hx}

	gio.set_global_atts(dset_out, dset_in.attrs, {ifile: dset_in.attrs['history']})
	dset_out.to_netcdf(ofile, format='NETCDF3_CLASSIC')
    else:
        return dset_in, anom.values


def calc_nino_new(index, ifile, var_id, base_period, ofile):
    """Calculate a new Nino index.

    Ref: Ren & Jin (2011). Nino indices for two types of ENSO. 
      Geophysical Research Letters, 38(4), L04704. 
      doi:10.1029/2010GL046031.

    Expected input: Sea surface temperature data.

    """
    
    # Calculate the traditional NINO3 and NINO4 indices
    regions = ['NINO3','NINO4']
    anomaly_timeseries = {}
    for reg in regions: 
        dset_in, anomaly_timeseries[reg] = calc_nino(reg, ifile, var_id, base_period, None)             
 
    # Calculate the new Ren & Jin index
    ntime = len(anomaly_timeseries['NINO3'])
    
    nino_new_timeseries = numpy.ma.zeros(ntime)
    for i in range(0, ntime):
        nino3_val = anomaly_timeseries['NINO3'][i]
        nino4_val = anomaly_timeseries['NINO4'][i]
        product = nino3_val * nino4_val
    
        alpha = 0.4 if product > 0 else 0.0
    
        if index == 'NINOCT':
            nino_new_timeseries[i] = numpy.ma.subtract(nino3_val, (numpy.ma.multiply(nino4_val, alpha)))
        elif index == 'NINOWP':
            nino_new_timeseries[i] = numpy.ma.subtract(nino4_val, (numpy.ma.multiply(nino3_val, alpha)))
    
    # Write output
    d = {}
    d['time'] = dset_in['time']
    d['nino'+index[4:]] = (['time'], nino_new_timeseries) 
    dset_out = xarray.Dataset(d)

    hx = 'Ref: Ren & Jin 2011, GRL, 38, L04704. Base period: %s to %s'  %(base_period[0], base_period[1])
    long_name = {}
    long_name['ninoCT'] = 'nino_cold_tongue_index'
    long_name['ninoWP'] = 'nino_warm_pool_index' 
    dset_out['nino'+index[4:]].attrs = {'long_name': long_name['nino'+index[4:]],
                                        'standard_name': long_name['nino'+index[4:]],
                                        'units': 'Celsius',
                                        'notes': hx}

    gio.set_global_atts(dset_out, dset_in.attrs, {ifile: dset_in.attrs['history']})
    dset_out.to_netcdf(ofile, format='NETCDF3_CLASSIC')


def calc_pwi(ifile, var_id, ofile):
    """Calculate the Planetary Wave Index.

    Ref: Irving & Simmonds (2015). A novel approach to diagnosing Southern 
      Hemisphere planetary wave activity and its influence on regional 
      climate variability. Journal of Climate. 28, 9041-9057. 
      doi:10.1175/JCLI-D-15-0287.1.
      
    Expected input: Wave envelope.   

    """
    
    # Read data
    dset_in = xarray.open_dataset(ifile)
    gio.check_xarrayDataset(dset_in, var_id)

    # Calculate index
    darray = dset_in[var_id].sel(latitude=slice(-70, -40))
    mermax = darray.max(dim='latitude')
    pwi_timeseries = mermax.median(dim='longitude')

    # Write output file
    d = {}
    d['time'] = darray['time']
    d['pwi'] = (['time'], pwi_timeseries.values)
    dset_out = xarray.Dataset(d)
    
    dset_out['pwi'].attrs = {'long_name': 'planetary_wave_index',
                             'standard_name': 'planetary_wave_index',
                             'units': darray.attrs['units'],
                             'notes': 'Ref: PWI of Irving and Simmonds (2015)'}
    
    gio.set_global_atts(dset_out, dset_in.attrs, {ifile: dset_in.attrs['history']})
    dset_out.to_netcdf(ofile, format='NETCDF3_CLASSIC')


def calc_sam(ifile, var_id, ofile):
    """Calculate an index of the Southern Annular Mode.

    Ref: Gong & Wang (1999). Definition of Antarctic Oscillation index. 
      Geophysical Research Letters, 26(4), 459-462.
      doi:10.1029/1999GL900003

    Expected input: Mean sea level pressure data.

    Concept: Difference between the normalised zonal mean pressure 
      at 40S and 65S.

    """
 
    # Read data
    dset_in = xarray.open_dataset(ifile)
    gio.check_xarrayDataset(dset_in, var_id)
 
    # Calculate index
    north_lat = uconv.find_nearest(dset_in['latitude'].values, -40)
    south_lat = uconv.find_nearest(dset_in['latitude'].values, -65)
    darray = dset_in[var_id].sel(latitude=(south_lat, north_lat)).mean(dim='longitude')

    groupby_op = get_groupby_op(darray['time'].values)
    clim = darray.groupby(groupby_op).mean(dim='time')
    anom = darray.groupby(groupby_op) - clim
    stdev = darray.groupby(groupby_op).std(dim='time')
    norm = anom.groupby(groupby_op) / stdev

    sam_timeseries = norm.sel(latitude=north_lat).values - norm.sel(latitude=south_lat).values

    # Write output file
    d = {}
    d['time'] = darray['time']
    d['sam'] = (['time'], sam_timeseries)
    dset_out = xarray.Dataset(d)
    
    hx = 'Ref: Gong & Wang (1999). GRL, 26, 459-462. doi:10.1029/1999GL900003'
    dset_out['sam'].attrs = {'long_name': 'Southern_Annular_Mode_Index',
                             'standard_name': 'Southern_Annular_Mode_Index',
                             'units': '',
                             'notes': hx}
    
    gio.set_global_atts(dset_out, dset_in.attrs, {ifile: dset_in.attrs['history']})
    dset_out.to_netcdf(ofile, format='NETCDF3_CLASSIC')


def calc_zw3(ifile, var_id, ofile):
    """Calculate an index of the Southern Hemisphere ZW3 pattern.
    
    Ref: Raphael (2004). A zonal wave 3 index for the Southern Hemisphere. 
      Geophysical Research Letters, 31(23), L23212. 
      doi:10.1029/2004GL020365.

    Expected input: Raphael (2004) uses is the 500hPa geopotential height, 
      sea level pressure or 500hPa zonal anomalies which are constructed by 
      removing the zonal mean of the geopotential height from each grid point 
      (preferred). The running mean (and zonal mean too if using it) should 
      have been applied to the input data beforehand. Raphael (2004) uses a 
      3-month running mean.

    Design notes: This function uses cdo instead of CDAT because the
      cdutil library doesn't have routines for calculating the daily 
      climatology or stdev.
    
    """

    # Read data
    dset_in = xarray.open_dataset(ifile)
    gio.check_xarrayDataset(dset_in, var_id)
    
    # Calculate the index
    groupby_op = get_groupby_op(dset_in['time'].values)
    index = {}
    for region in ['zw31', 'zw32', 'zw33']: 
        south_lat, north_lat, west_lon, east_lon = gio.regions[region]
        darray = dset_in[var_id].sel(latitude=slice(south_lat, north_lat), longitude=slice(west_lon, east_lon)).mean(dim=['latitude', 'longitude'])

        clim = darray.groupby(groupby_op).mean(dim='time')
        anom = darray.groupby(groupby_op) - clim
        stdev = darray.groupby(groupby_op).std(dim='time')
        norm = anom.groupby(groupby_op) / stdev

        index[region] = norm.values

    zw3_timeseries = (index['zw31'] + index['zw32'] + index['zw33']) / 3.0
 
    # Write output file
    d = {}
    d['time'] = darray['time']
    d['zw3'] = (['time'], zw3_timeseries)
    dset_out = xarray.Dataset(d)
    
    dset_out['zw3'].attrs = {'id': 'zw3',
                             'long_name': 'zonal_wave_3_index',
                             'standard_name': 'zonal_wave_3_index',
                             'units': '',
                             'notes': 'Ref: ZW3 index of Raphael (2004)'}
    
    gio.set_global_atts(dset_out, dset_in.attrs, {ifile: dset_in.attrs['history']})
    dset_out.to_netcdf(ofile, format='NETCDF3_CLASSIC')


def get_groupby_op(time_array):
    """Find timescale of data and return groupby function.

    Args:
      indata (numpy array): Array of numpy.datetime64 instances

    Returns:
      'time.dayofyear' or 'time.month' for xarray climatology calculation

    """

    tscale = gio.get_timescale(time_array)
        
    assert tscale in ['daily', 'monthly']
    groupby_op = 'time.dayofyear' if tscale == 'daily' else 'time.month'

    return groupby_op


def main(inargs):
    """Run the program."""

    function_for_index = {'ASL': calc_asl,
                          'NINO': calc_nino,
			  'SAM': calc_sam,
			  'PWI': calc_pwi,
                          'ZW3': calc_zw3,
                          'NINO_new': calc_nino_new,}
                       
    if inargs.index[0:4] == 'NINO':
        if inargs.index == 'NINOCT' or inargs.index == 'NINOWP':
            calc_index = function_for_index['NINO_new']
        else:
            calc_index = function_for_index['NINO']
        calc_index(inargs.index, inargs.infile, inargs.variable, inargs.base, inargs.outfile)            
    else:
        calc_index = function_for_index[inargs.index]
        calc_index(inargs.infile, inargs.variable, inargs.outfile)
    

if __name__ == '__main__':

    extra_info ="""

example:
  python calc_climate_index.py NINO34 
  /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly_native-ocean.nc ts 
  /work/dbirving/processed/indices/data/ts_Merra_surface_NINO34_monthly_native-ocean.nc
        
author:
  Damien Irving, d.irving@student.unimelb.edu.au

planned enhancements:
  Confidence intervals will be calculated for any SST indices calculated 
  using the ERSSTv3b data (as this contains an additional error variance
  variable, which is the standard error squared). To calculate the error 
  for a region (like a Nino region) you need to average the error variance
  and divide by the effective number of degrees of freedom for the area.
  Then take the square root of that for the standard error for the region.
  A simple way to estimate the effective number of degrees of freedom is 
  to use the S method described by Wang & Shen (1999). J Clim, 12, 1280-91.
  Once you get the standard error for the area average, you can use it to
  define confidence intervals. For example, 1.96 times stardard error for 
  the 95% confidence.       

    """

    description = 'Calculate climate index'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info,
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("index", type=str, help="Index to calculate",
                        choices=['NINO12', 'NINO3', 'NINO4', 'NINO34', 'NINOCT',
                                 'NINOWP', 'SAM', 'ZW3', 'MEX', 'ASL', 'MI', 'PWI'])
    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
    
    parser.add_argument("--base", nargs=2, type=str, default=('1981-01-01', '2010-12-31'), 
                        metavar=('START_DATE', 'END_DATE'), 
                        help="Start and end date for base period [default: %(default)s]")
  
    args = parser.parse_args()
                
    print 'Index:', args.index
    print 'Input file:', args.infile
    print 'Output file:', args.outfile

    main(args)
