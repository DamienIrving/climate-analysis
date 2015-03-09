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
ENV_3D=${ZW_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
${ENV_3D} : ${V_RUNMEAN}
	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< ${VAR} $@ ${CDO_FIX_SCRIPT} ${WAVE_MIN} ${WAVE_MAX} hilbert ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

## Step 3: Collapse the meridional dimension
ENV_2D=${ZW_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
${ENV_2D} : ${ENV_3D}
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	bash ${CDO_FIX_SCRIPT} $@ env${VAR}

## Step 4: Calculate the PWI and other wave statistics (mean & max, extent/coverage, etc)
WAVE_STATS=${ZW_DIR}/wavestats_zw_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc 
${WAVE_STATS} : ${ENV_2D}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< env${VAR} $@ --threshold ${EXTENT_THRESH}

## Step 5: Generate list of dates exceeding some PWI threshold (for later use in composite creation)
DATE_LIST=${COMP_DIR}/dates_zw_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.txt 
${DATE_LIST}: ${WAVE_STATS}
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --date_list $@ --metric_threshold ${METRIC_HIGH_THRESH}


# Common indices

## Phase and amplitude of each Fourier component
FOURIER_INFO=${ZW_DIR}/fourier_zw_${COE_WAVE_LABEL}-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc 
${FOURIER_INFO} : ${V_RUNMEAN}
	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< ${VAR} $@ ${CDO_FIX_SCRIPT} ${WAVE_MIN} ${WAVE_MAX} coefficients ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

## ZW3 index 
### Step 1: Calculate zonal anomaly
ZG_ORIG=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native.nc
ZG_ZONAL_ANOM=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native-zonal-anom.nc
${ZG_ZONAL_ANOM} : ${ZG_ORIG}       
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< zg $@ ${CDO_FIX_SCRIPT} ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}
### Step 2: Apply running mean
ZG_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZG_ZONAL_ANOM_RUNMEAN} : ${ZG_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ zg
### Step 3: Calculate index
ZW3_INDEX=${ZW_DIR}/zw3index_zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZW3_INDEX} : ${ZG_ZONAL_ANOM_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py ZW3 $< zg $@

## Nino 3.4
### Step 1: Apply running mean
TOS_ORIG=${DATA_DIR}/tos_${DATASET}_surface_daily_native-tropicalpacific.nc
TOS_RUNMEAN=${DATA_DIR}/tos_${DATASET}_surface_${TSCALE_LABEL}_native-tropicalpacific.nc
${TOS_RUNMEAN} : ${TOS_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ tos
### Step 2: Calculate index
NINO34_INDEX=${INDEX_DIR}/nino34_tos_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${NINO34_INDEX} : ${TOS_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py NINO34 $< tos $@
### Step 3: Generate El Nino date list
ELNINO_DATES=${INDEX_DIR}/dates_nino34-elnino_tos_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${ELNINO_DATES} : ${NINO34_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< nino34 $@ --metric_threshold 0.5 --threshold_direction greater
### Step 4: Generate La Nina date list
ELNINO_DATES=${INDEX_DIR}/dates_nino34-lanina_tos_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${LANINA_DATES} : ${NINO34_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< nino34 $@ --metric_threshold -0.5 --threshold_direction less

## SAM
### Step 1: Apply running mean
PSL_ORIG=${DATA_DIR}/psl_${DATASET}_surface_daily_native-shextropics30.nc
PSL_RUNMEAN=${DATA_DIR}/psl_${DATASET}_surface_${TSCALE_LABEL}_native-shextropics30.nc
${PSL_RUNMEAN} : ${PSL_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ psl
### Step 2: Calculate index
SAM_INDEX=${INDEX_DIR}/sam_psl_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${SAM_INDEX} : ${PSL_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py SAM $< psl $@
### Step 3: Generate positive SAM date list
SAM_POS_DATES=${INDEX_DIR}/dates_sam-gt75pct_psl_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${SAM_POS_DATES} : ${SAM_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< sam $@ --metric_threshold 75pct --threshold_direction greater
### Step 4: Generate negative SAM date list
SAM_NEG_DATES=${INDEX_DIR}/dates_sam-lt25pct_psl_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${SAM_NEG_DATES} : ${SAM_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< sam $@ --metric_threshold 25pct --threshold_direction less

# Data for contours on plots

## Step 1: Calculate the contour zonal anomaly
CONTOUR_ORIG=${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native.nc
CONTOUR_ZONAL_ANOM=${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native-zonal-anom.nc       
${CONTOUR_ZONAL_ANOM} : ${CONTOUR_ORIG}
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< ${CONTOUR_VAR} $@ ${CDO_FIX_SCRIPT} ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

## Step 2: Apply temporal averaging to the zonal contour data
CONTOUR_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc 
${CONTOUR_ZONAL_ANOM_RUNMEAN} : ${CONTOUR_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ ${CONTOUR_VAR}


# Common table/database

TABLE=${ZW_DIR}/table_zw_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv 
${TABLE} : ${WAVE_STATS} ${ZW3_INDEX} ${FOURIER_INFO}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_zw_table.py $(word 1,$^) $(word 2,$^) $(word 3,$^) $@

