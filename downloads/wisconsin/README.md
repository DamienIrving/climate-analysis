# Data processing

### Date lists

1. Convert csv date files to txt date listings for composite calculation
```
$ python cmmt_date_list.py ellsworth_CMMTdatetimes.csv ellsworth_CMMTdatetimes.txt
```

### ERA-Interim preparation

1. Select 500hPa level, calculate daily mean and merge files

```
$ python preprocess_eraint_nci.py /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/v01/ua/ua_6hrs_ERAI_historical_an-pl_19991101_19991130.nc /g/data/ub4/erai/netcdf/6hr/atmos/oper_an_pl/v01/ua/ua_6hrs_ERAI_historical_an-pl_19991201_19991231.nc /g/data/r87/dbi599/data_eraint/ua_eraint_500hPa_daily_native_1992-2012.nc
```

2. Invert the latitude dimension and make latitude [0, 360)

```
$ cdo invertlat -sellonlatbox,0,359.9,-90,90 /g/data/r87/dbi599/data_eraint/ua_eraint_500hPa_daily_native_1992-2012.nc /g/data/r87/dbi599/data_eraint/ua_eraint_500hPa_daily_native-reoriented_1992-2012.nc
```

3. Calculate streamfunction zonal anomaly

