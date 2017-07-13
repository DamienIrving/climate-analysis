# Data processing

### Date lists

1. Convert csv date files to txt date listings for composite calculation
```
$ python cmmt_date_list.py ellsworth_CMMTdatetimes.csv /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/ellsworth_CMMTdatetimes.txt
```

### ERA-Interim preparation

1. Select 500hPa level, calculate daily mean and merge files

```
$ python preprocess_eraint_nci.py /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/v01/ua/ua_6hrs_ERAI_historical_an-pl_19*.nc /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/v01/ua/ua_6hrs_ERAI_historical_an-pl_200*.nc  /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/v01/ua/ua_6hrs_ERAI_historical_an-pl_201[0123456]*.nc  /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/ua_eraint_500hPa_daily_native.nc
```

2. Invert the latitude dimension and make latitude [0, 360)

```
$ cdo invertlat -sellonlatbox,0,359.9,-90,90 /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/ua_eraint_500hPa_daily_native.nc /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/ua_eraint_500hPa_daily_native-reoriented.nc
```

3. Calculate streamfunction temporal anomaly

```
$ bash calc_wind_quantities.sh streamfunction /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/ua_eraint_500hPa_daily_native-reoriented.nc ua /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/va_eraint_500hPa_daily_native-reoriented.nc va /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf_eraint_500hPa_daily_native-reoriented.nc /g/data/r87/dbi599/miniconda2/envs/wisconsin/bin/python ~/climate-analysis/data_processing /g/data/r87/dbi599/temp

$ cdo ydaysub /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf_eraint_500hPa_daily_native-reoriented.nc -ydayavg /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf_eraint_500hPa_daily_native-reoriented.nc /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf_eraint_500hPa_daily-anom-wrt-all_native-reoriented.nc
```

### Calculate and plot composites

```
$ python calc_composite.py /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf_eraint_500hPa_daily-anom-wrt-all_native-reoriented.nc sf /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_ellsworth.nc --date_file /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/ellsworth_CMMTdatetimes.txt
```

```
$ python plot_map.py 3 2 --infile /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_ellsworth.nc sf_annual none none none contour0 1 --infile /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_ellsworth.nc sf_DJF none none none contour0 3 --infile /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_ellsworth.nc sf_MAM none none none contour0 4 --infile /g/data/r87/dbi599/data_eraint/wisconsin_cmmt/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_ellsworth.nc sf_JJA none none none contour0 5 --infile /g/data/r87/dbi599/data_eraint/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_ellsworth.nc sf_SON none none none contour0 6 --output_projection SouthPolarStereo --subplot_headings Annual none DJF MAM JJA SON --infile /g/data/r87/dbi599/data_eraint/ua-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc ua_annual none none none uwind0 1 --infile /g/data/r87/dbi599/data_eraint/ua-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc ua_DJF none none none uwind0 3 --infile /g/data/r87/dbi599/data_eraint/ua-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc ua_MAM none none none uwind0 4 --infile /g/data/r87/dbi599/data_eraint/ua-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc ua_JJA none none none uwind0 5 --infile /g/data/r87/dbi599/data_eraint/ua-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc ua_SON none none none uwind0 6 --figure_size 9 16 --infile /g/data/r87/dbi599/data_eraint/va-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc va_annual none none none vwind0 1 --infile /g/data/r87/dbi599/data_eraint/va-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc va_DJF none none none vwind0 3 --infile /g/data/r87/dbi599/data_eraint/va-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc va_MAM none none none vwind0 4 --infile /g/data/r87/dbi599/data_eraint/va-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc va_JJA none none none vwind0 5 --infile /g/data/r87/dbi599/data_eraint/va-composite_eraint_500hPa_daily_native-reoriented_ellsworth.nc va_SON none none none vwind0 6 --ofile figure.png --flow_type streamlines --contour_levels -12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5 --exclude_blanks --streamline_colour 0.7

```
