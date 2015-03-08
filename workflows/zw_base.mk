# zw_base.mk
#
# Description: Basic workflow that underpins all other zonal wave (zw) workflows 
#
# To execute:
#   make -n -B -f zw_base.mk  (-n is a dry run) (-B is a force make)

# Pre-processing:
#   The regirdding (if required) needs to be done beforehand 
#   (probably using cdo remapcon2,r360x181 in.nc out.nc)
#   So does the zonal anomaly


# Define marcos
include zw_config.mk

all : ${TARGET}


# Wave envelope & PWI

## Step 1: Apply temporal averaging to the meridional wind data
V_ORIG=${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_daily_${GRID}.nc
V_RUNMEAN=${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
${V_RUNMEAN} : ${V_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ ${VAR}

## Step 2: Extract the wave envelope (for the entire globe)
ENV_3D=${ZW3_DIR}/env${VAR}_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
${ENV_3D} : ${V_RUNMEAN}
	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< ${VAR} $@ ${CDO_FIX_SCRIPT} ${WAVE_MIN} ${WAVE_MAX} hilbert ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMP_DATA_DIR}

## Step 3: Collapse the meridional dimension
ENV_2D=${ZW3_DIR}/env${VAR}_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
${ENV_2D} : ${ENV_3D}
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	bash ${CDO_FIX_SCRIPT} $@ env${VAR}

## Step 4: Calculate the PWI and other wave statistics (mean & max, extent/coverage, etc)
WAVE_STATS=${ZW3_DIR}/wavestats_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc 
${WAVE_STATS} : ${ENV_2D}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< env${VAR} $@ --threshold ${EXTENT_THRESH}

## Step 5: Generate list of dates exceeding some PWI threshold (for later use in composite creation)
DATE_LIST=${COMP_DIR}/dates_zw3_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.txt 
${DATE_LIST}: ${WAVE_STATS}
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --date_list $@ --metric_threshold ${METRIC_HIGH_THRESH}


# Common indices

## Phase and amplitude of each Fourier component
FOURIER_INFO=${ZW3_DIR}/fourier_zw3_${COE_WAVE_LABEL}-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc 
${FOURIER_INFO} : ${V_RUNMEAN}
	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< ${VAR} $@ ${CDO_FIX_SCRIPT} ${WAVE_MIN} ${WAVE_MAX} coefficients ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMP_DATA_DIR}

## ZW3 index 
ZG_ORIG=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native.nc
ZG_ZONAL_ANOM=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native-zonal-anom.nc
${ZG_ZONAL_ANOM} : ${ZG_ORIG}       
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< zg $@ ${CDO_FIX_SCRIPT} ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMP_DATA_DIR}

ZG_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZG_ZONAL_ANOM_RUNMEAN} : ${ZG_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ zg

ZW3_INDEX=${ZW3_DIR}/zw3index_zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZW3_INDEX} : ${ZG_ZONAL_ANOM_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climate_index.py ZW3 $< zg $@


# Data for contours on plots

## Step 1: Calculate the contour zonal anomaly
CONTOUR_ORIG=${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native.nc
CONTOUR_ZONAL_ANOM=${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native-zonal-anom.nc       
${CONTOUR_ZONAL_ANOM} : ${CONTOUR_ORIG}
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< ${CONTOUR_VAR} $@ ${CDO_FIX_SCRIPT} ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMP_DATA_DIR}

## Step 2: Apply temporal averaging to the zonal contour data
CONTOUR_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc 
${CONTOUR_ZONAL_ANOM_RUNMEAN} : ${CONTOUR_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ ${CONTOUR_VAR}


# Common table/database

TABLE=${ZW3_DIR}/table_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv 
${TABLE} : ${WAVE_STATS} ${ZW3_INDEX} ${FOURIER_INFO}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_zw3_table.py $(word 1,$^) $(word 2,$^) $(word 3,$^) $@

