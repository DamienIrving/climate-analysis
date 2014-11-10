# zw3_climatology.mk
#
# To execute:
#   make -n -B -f zw3_climatology.mk  (-n is a dry run) (-B is a force make)

# Pre-processing:
#   The regirdding (if required) needs to be done beforehand 
#   (probably using cdo remapcon2,r360x181 in.nc out.nc)
#   So does the zonal anomaly


## Define marcos ##
include zw3_climatology_config.mk


all : ${TARGET}

### Calculate the wave envelope ###

## Step 1: Apply temporal averaging to the meridional wind data ##

V_ORIG=${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_daily_${GRID}.nc
V_RUNMEAN=${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
${V_RUNMEAN} : ${V_ORIG}
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 2: Extract the wave envelope (for the entire globe) ##

ENV_3D=${ZW3_DIR}/env${VAR}_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
${ENV_3D} : ${V_RUNMEAN}
	${FOURIER_METHOD} $< ${VAR} $@ ${ENV_SEARCH}

## Step 3: Collapse the meridional dimension ##

ENV_2D=${ZW3_DIR}/env${VAR}_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
${ENV_2D} : ${ENV_3D}
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	ncatted -O -a axis,time,c,c,T $@


### Generate the table/database of interesting results ###

## Step 1: Calculate the wave statistics (metrics like mean & max, extent/coverage, etc) ##

WAVE_STATS=${ZW3_DIR}/wavestats_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc 
${WAVE_STATS} : ${ENV_2D}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< env${VAR} $@ --threshold ${EXTENT_THRESH}

## Step 2: Calculate the phase and amplitude of each Fourier component ##

FOURIER_INFO=${ZW3_DIR}/fourier_zw3_${COE_WAVE_LABEL}-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc 
${FOURIER_INFO} : ${V_RUNMEAN}
	${FOURIER_METHOD} $< ${VAR} $@ ${COE_SEARCH}

## Step 3: Calculate the ZW3 index of Raphael (2004) ## 

ZG_ORIG=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native.nc
ZG_ZONAL_ANOM=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native-zonal-anom.nc
${ZG_ZONAL_ANOM} : ${ZG_ORIG}       
	${ZONAL_ANOM_METHOD} $< zg $@
	ncatted -O -a axis,time,c,c,T $@

ZG_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZG_ZONAL_ANOM_RUNMEAN} : ${ZG_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

ZW3_INDEX=${ZW3_DIR}/zw3index_zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZW3_INDEX} : ${ZG_ZONAL_ANOM_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py ZW3 $< zg $@

## Step 4: Put it all in a common table/database ##

TABLE=${ZW3_DIR}/table_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv 
${TABLE} : ${WAVE_STATS} ${ZW3_INDEX} ${FOURIER_INFO}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_zw3_table.py $(word 1,$^) $(word 2,$^) $(word 3,$^) $@

