"""
Filename:     calc_climate_index.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Calculate common climate indices

"""

# Import general Python modules

import sys, os
import argparse
import numpy
from cdo import *
cdo = Cdo()
import pdb
import cdms2, cdutil, MV2

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
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions

def calc_asl(ifile, var_id):
    """Calculate the Amundsen Sea Low index.

    Ref: Turner et al (2013). The Amundsen Sea Low. 
      International Journal of Climatology. 33(7), 1818-1829
      doi:10.1002/joc.3558.

    Expected input: Mean sea level pressure data.

    Concept: Location and value of minimum MSLP is the region
      bounded by 60-75S and 180-310E.   

    """

    # Read data
    indata = nio.InputData(ifile, var_id, region='asl')
    assert indata.data.getOrder() == 'tyx', "Order of the data must be time, lon, lat"

    # Get axis information
    lat_axis = indata.data.getLatitude()[:]
    lon_axis = indata.data.getLongitude()[:]
    time_axis = indata.data.getTime()
    lats, lons = nio.coordinate_pairs(lat_axis, lon_axis)

    # Reshape data
    ntimes, nlats, nlons = indata.data.shape
    indata_reshaped = numpy.reshape(indata.data, (ntimes, nlats*nlons))

    # Get the ASL index info (min value for each timestep and its lat/lon)
    min_values = numpy.amin(indata_reshaped, axis=1)
    min_indexes = numpy.argmin(indata_reshaped, axis=1)
    min_lats = numpy.take(lats, min_indexes)
    min_lons = numpy.take(lons, min_indexes)

    # Output file info
    values_atts = {'id': 'asl_value',
                   'long_name': 'asl_minimum_pressure',
                   'standard_name': 'asl_minimum_pressure',
                   'units': 'Pa',
                   'notes': 'Ref: Turner et al (2013). Int J Clim. 33, 1818-1829. doi:10.1002/joc.3558.'}
    lats_atts = {'id': 'asl_lat',
                 'long_name': 'asl_latitude',
                 'standard_name': 'asl_latitude',
                 'units': 'degrees_north',
                 'notes': 'Ref: Turner et al (2013). Int J Clim. 33, 1818-1829. doi:10.1002/joc.3558.'}
    lons_atts = {'id': 'asl_lon',
                 'long_name': 'asl_longitude',
                 'standard_name': 'asl_longitude',
                 'units': 'degrees_east',
                 'notes': 'Ref: Turner et al (2013). Int J Clim. 33, 1818-1829. doi:10.1002/joc.3558.'}

    outdata_list = [min_values, min_lats, min_lons]
    outvar_atts_list = [values_atts, lats_atts, lons_atts]
    outvar_axes_list = [(time_axis,), (time_axis,), (time_axis,)]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def calc_mex(ifile, var_id):
    """Calculate the mid-latitude extreme index (MEX).
    
    Ref: Coumou et al (2014). Quasi-resonant circulation regimes and hemispheric 
      synchronization of extreme weather in boreal summer. 
      Proceedings of the National Academy of Sciences. 
      doi:10.1073/pnas.1412797111
      (Only difference between their method and that implemented here is that 
      they detrend their data first.) 
    
    Expected input: Any running mean should have been applied to the 
      input data beforehand. 
    
    Design notes: This function uses cdo instead of CDAT because the
      cdutil library doesn't have routines for calculating the daily 
      climatology or standard deviation.
    
    Possible improvements: A weighted mean?
        
    """

    west_lon = 0
    east_lon = 360
    south_lat = -75
    north_lat = -40

    # Determine the timescale
    indata_complete = nio.InputData(ifile, var_id, latitude=(south_lat, north_lat)) 
    tscale_abbrev = get_timescale(indata.data) 

    # Calculate the index
    div_operator_text = 'cdo y%sdiv ' %(tscale_abbrev)
    div_operator_func = eval(div_operator_text.replace(' ', '.', 1))
    sub_operator_text = ' -y%ssub ' %(tscale_abbrev)
    avg_operator_text = ' -y%savg ' %(tscale_abbrev)
    std_operator_text = ' -y%sstd ' %(tscale_abbrev)

    selregion = "-sellonlatbox,%d,%d,%d,%d %s " %(west_lon, east_lon, south_lat, north_lat, ifile)

    anomaly = sub_operator_text + selregion + avg_operator_text + selregion
    std = std_operator_text + selregion

    print div_operator_text + anomaly + std   #e.g. cdo ydaydiv anomaly std
    cdo_result = div_operator_func(input=anomaly + std, returnArray=var_id)
    square_term = numpy.square(cdo_result)
    square_term = cdms2.createVariable(square_term, grid=indata.data.getGrid(), axes=indata.data.getAxisList())

    ave_axes = square_term.getOrder().translate(None, 't')  #all but the time axis
    mex_timeseries_raw = cdutil.averager(square_term, axis=ave_axes, weights=['weighted']*len(ave_axes))
    
    mex_avg = numpy.mean(mex_timeseries_raw)
    mex_std = numpy.std(mex_timeseries_raw)

    mex_timeseries_normalised = (mex_timeseries_raw - mex_avg) / mex_std

    # Output file info
    hx = 'Ref: MEX index of Coumou (2014) doi:10.1073/pnas.1412797111'
    var_atts = {'id': 'mex',
                'long_name': 'midlatitude_extreme_index',
                'standard_name': 'midlatitude_extreme_index',
                'units': '',
                'notes': hx}

    outdata_list = [mex_timeseries_normalised,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [(indata.data.getTime(),),]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def calc_mi(ifile, var_id):
    """Calculate the meridional index.

    Expected input: Meridional wind data.
    
    Returns: Meridional index (average meridional wind amplitude from 40-70S)
      and the average meridional wind (to check if close to zero).

    """

    # Read data
    indata = nio.InputData(ifile, var_id, latitude=(-70, -40))
    time_axis = indata.data.getTime()
    
    # v mean
    v_mean = cdutil.averager(indata.data, axis='yx', weights=['unweighted']*2)

    # amp(v) mean
    v_amp = MV2.absolute(indata.data)
    v_amp_mean = cdutil.averager(v_amp, axis='yx', weights=['unweighted']*2)

    # Output file info
    v_mean_atts = {'id': 'v_mean',
                   'long_name': 'v_mean',
                   'standard_name': 'v_mean',
                   'units': indata.data.units}
    v_amp_mean_atts = {'id': 'mi',
                       'long_name': 'meridional_index',
                       'standard_name': 'meridional_index',
                       'units': indata.data.units,
                       'notes': 'Average amplitude of the meridional wind from 40-70S'}

    outdata_list = [v_mean, v_amp_mean]
    outvar_atts_list = [v_mean_atts, v_amp_mean_atts]
    outvar_axes_list = [(time_axis,), (time_axis,)]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def calc_nino(index, ifile, var_id, base_period):
    """Calculate a Nino index.

    Expected input: Sea surface temperature data.

    """

    # Determine the timescale
    indata = nio.InputData(ifile, var_id, region='nino'+index[4:])
    tscale_abbrev = get_timescale(indata.data)

    # Calculate the index
    south_lat, north_lat = nio.regions['nino'+index[4:]][0][0: 2]
    west_lon, east_lon = nio.regions['nino'+index[4:]][1][0: 2]
    
    sub_operator_text = 'cdo y%ssub ' %(tscale_abbrev)
    sub_operator_func = eval(sub_operator_text.replace(' ', '.', 1)) 
    avg_operator_text = ' -y%savg ' %(tscale_abbrev)
    
    selregion = "-sellonlatbox,%3.2f,%3.2f,%3.2f,%3.2f %s " %(west_lon, east_lon, south_lat, north_lat, ifile)
    seldate = "-seldate,%s,%s " %(base_period[0], base_period[1])
    raw_data = "-fldmean "+selregion
    climatology = avg_operator_text + seldate + raw_data
    
    print sub_operator_text + raw_data + climatology
    result = sub_operator_func(input=raw_data + climatology, returnArray=var_id)
    nino_timeseries = numpy.squeeze(result)

    # Output file info
    hx = 'lat: %s to %s, lon: %s to %s, base: %s to %s' %(south_lat, north_lat,
                                                          west_lon, east_lon,
                                                          base_period[0], base_period[1])
    var_atts = {'id': 'nino'+index[4:],
                'long_name': 'nino'+index[4:]+'_index',
                'standard_name': 'nino'+index[4:]+'_index',
                'units': 'Celsius',
                'notes': hx}
    
    outdata_list = [nino_timeseries,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [(indata.data.getTime(),),]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def calc_nino_new(index, ifile, var_id, base_period):
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
        outdata_list, temp_atts_list, outvar_axes_list, global_atts = calc_nino(reg, ifile, var_id, base_period)       
        anomaly_timeseries[reg] = outdata_list[0]      
 
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
    
    # Determine the attributes
    hx = 'Ref: Ren & Jin 2011, GRL, 38, L04704. Base period: %s to %s'  %(base_period[0], 
                                                                          base_period[1])
    long_name = {}
    long_name['NINOCT'] = 'nino_cold_tongue_index'
    long_name['NINOWP'] = 'nino_warm_pool_index'    

    var_atts = {'id': 'nino'+index[4:],
                'long_name': long_name[index],
                'standard_name': long_name[index],
                'units': 'Celsius',
                'notes': hx}

    outdata_list = [nino_new_timeseries,]
    outvar_atts_list = [var_atts,]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, global_atts 


def calc_pwi(ifile, var_id):
    """Calculate the Planetary Wave Index.

    Ref: Irving & Simmonds (2015). Southern Hemisphere planetary wave 
      activity and its influence on weather and climate extremes. 
      https://www.authorea.com/users/5641/articles/12197/_show_article

    Expected input: Wave envelope.   

    """
    
    # Read data
    indata = nio.InputData(ifile, var_id, latitude=(-70, -40))
    assert indata.data.getOrder() == 'tyx', "Order of the data must be time, lon, lat"

    # Calulcate the index
    mermax = numpy.max(indata.data, axis=1)
    pwi_timeseries = numpy.median(mermax, axis=-1)

    # Output file info
    pwi_atts = {'id': 'pwi',
                'long_name': 'planetary_wave_index',
                'standard_name': 'planetary_wave_index',
                'units': indata.data.units,
                'notes': 'Ref: https://www.authorea.com/users/5641/articles/12197/_show_article'}

    outdata_list = [pwi_timeseries,]
    outvar_atts_list = [pwi_atts,]
    outvar_axes_list = [(indata.data.getTime(),),]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def calc_sam(ifile, var_id):
    """Calculate an index of the Southern Annular Mode.

    Ref: Gong & Wang (1999). Definition of Antarctic Oscillation index. 
      Geophysical Research Letters, 26(4), 459-462.
      doi:10.1029/1999GL900003

    Expected input: Mean sea level pressure data.

    Concept: Difference between the normalised zonal mean pressure 
      difference between 40S and 65S.

    """
    
    # Determine the timescale
    indata = nio.InputData(ifile, var_id, longitude=(10,12))
    tscale_abbrev = get_timescale(indata.data)
    
    # Determine latitude range (cdo requires exact latitude value)
    lat_axis = indata.data.getLatitude()[:]
    north_lat = nio.find_nearest(lat_axis, -40)
    south_lat = nio.find_nearest(lat_axis, -65)

    # Calculate the index
    normalised_zonal_mean_mslp = {}
    for lat in [north_lat, south_lat]: 
        div_operator_text = 'cdo y%sdiv ' %(tscale_abbrev)
        div_operator_func = eval(div_operator_text.replace(' ', '.', 1))
        sub_operator_text = ' -y%ssub ' %(tscale_abbrev)
        avg_operator_text = ' -y%savg ' %(tscale_abbrev)
        std_operator_text = ' -y%sstd ' %(tscale_abbrev)
    
        sellat = "-sellonlatbox,0,360,%3.2f,%3.2f %s" %(lat, lat, ifile)
        zonmean = "-zonmean "+sellat
        anomaly = sub_operator_text + zonmean + avg_operator_text + zonmean
        std = std_operator_text + zonmean
    
        print div_operator_text + anomaly + std   #e.g. cdo ydaydiv anomaly std
        result = div_operator_func(input=anomaly + std, returnArray=var_id)
        normalised_zonal_mean_mslp[lat] = numpy.squeeze(result)

    sam_timeseries = normalised_zonal_mean_mslp[north_lat] - normalised_zonal_mean_mslp[south_lat]

    # Output file info
    hx = 'Ref: Gong & Wang (1999). GRL, 26, 459-462. doi:10.1029/1999GL900003'
    var_atts = {'id': 'sam',
                'long_name': 'Southern_Annular_Mode_Index',
                'standard_name': 'Southern_Annular_Mode_Index',
                'units': '',
                'notes': hx}

    outdata_list = [sam_timeseries,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [(indata.data.getTime(),),]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def calc_zw3(ifile, var_id):
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

    # Determine the timescale
    indata = nio.InputData(ifile, var_id, region='small')
    tscale_abbrev = get_timescale(indata.data)

    # Calculate the index
    index = {}
    for region in ['zw31', 'zw32', 'zw33']: 
        south_lat, north_lat = nio.regions[region][0][0: 2]
        west_lon, east_lon = nio.regions[region][1][0: 2]
    
        div_operator_text = 'cdo y%sdiv ' %(tscale_abbrev)
        div_operator_func = eval(div_operator_text.replace(' ', '.', 1))
        sub_operator_text = ' -y%ssub ' %(tscale_abbrev)
        avg_operator_text = ' -y%savg ' %(tscale_abbrev)
        std_operator_text = ' -y%sstd ' %(tscale_abbrev)
    
        selregion = "-sellonlatbox,%d,%d,%d,%d %s " %(west_lon, east_lon, south_lat, north_lat, ifile)
        fldmean = "-fldmean "+selregion
        anomaly = sub_operator_text + fldmean + avg_operator_text + fldmean
        std = std_operator_text + fldmean
    
        print div_operator_text + anomaly + std   #e.g. cdo ydaydiv anomaly std
        result = div_operator_func(input=anomaly + std, returnArray=var_id)
        index[region] = numpy.squeeze(result)

    zw3_timeseries = (index['zw31'] + index['zw32'] + index['zw33']) / 3.0
 
    # Define the output attributes
    notes = 'Ref: ZW3 index of Raphael (2004)'
    var_atts = {'id': 'zw3',
                'long_name': 'zonal_wave_3_index',
                'standard_name': 'zonal_wave_3_index',
                'units': '',
                'notes': notes}

    outdata_list = [zw3_timeseries,]
    outvar_atts_list = [var_atts,]
    outvar_axes_list = [(indata.data.getTime(),),]
    
    return outdata_list, outvar_atts_list, outvar_axes_list, indata.global_atts 


def get_timescale(indata):
    """Find the timescale of the data.

    Args:
      indata (cdms2.Tvariable.transientvariable): Input data

    Returns:
      'day' or 'mon' to signify daily or monthly timescale data

    """

    time_axis = indata.getTime().asComponentTime()
    timescale = nio.get_timescale(nio.get_datetime(time_axis[0:2]))
        
    assert timescale in ['daily', 'monthly']
    tscale_abbrev = 'day' if timescale == 'daily' else 'mon'

    return tscale_abbrev


def main(inargs):
    """Run the program."""
        
    # Identify relevant function and calculate index
    function_for_index = {'NINO': calc_nino,
                          'NINO_new': calc_nino_new,
                          'SAM': calc_sam,
                          'ZW3': calc_zw3,
                          'MEX': calc_mex,
                          'ASL': calc_asl,
                          'MI': calc_mi,
                          'PWI': calc_pwi}   
    
    if inargs.index[0:4] == 'NINO':
        if inargs.index == 'NINOCT' or inargs.index == 'NINOWP':
            calc_index = function_for_index['NINO_new']
        else:
            calc_index = function_for_index['NINO']

        outdata_list, outvar_atts_list, outvar_axes_list, global_atts = calc_index(inargs.index, 
                                                                                   inargs.infile, 
                                                                                   inargs.variable, 
                                                                                   inargs.base)            
    else:
        calc_index = function_for_index[inargs.index]
        outdata_list, outvar_atts_list, outvar_axes_list, global_atts = calc_index(inargs.infile, 
                                                                                   inargs.variable)
    
    # Write the outfile
    nio.write_netcdf(inargs.outfile, " ".join(sys.argv), 
                     global_atts,  
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info ="""

example:
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_climate_index.py NINO34 
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
