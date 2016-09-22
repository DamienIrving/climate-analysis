# ocean_summary_base.mk
#
# Description: Core workflow for producing ocean summary data:
#  - zonal mean ocean temperature and salinity fields
#  - vertical mean ocean temperature and salinity fields
#  - ocean heat content fields and timeseries 
#
# To execute:
#   1. copy name of target file from ocean_summary_base.mk 
#   2. paste it into ocean_summary_config.mk as the target variable  
#   3. $ make -n -B -f ocean_summary_base.mk  (-n is a dry run) (-B is a force make)


# Define marcos

include ocean_summary_config.mk
all : ${TARGET}

# Filenames

CONTROL_FILES=$(wildcard ${ORIG_CONTROL_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/${VAR}/${CONTROL_RUN}/${VAR}_Omon_${MODEL}_piControl_${CONTROL_RUN}_*.nc)
CONTROL_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/yr/ocean/${VAR}/${CONTROL_RUN}
DRIFT_COEFFICIENTS=${CONTROL_DIR}/${VAR}-coefficients_Oyr_${MODEL}_piControl_${CONTROL_RUN}_all.nc

VARIABLE_FILES=$(wildcard ${ORIG_VARIABLE_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/${VAR}/${RUN}/${VAR}_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)

DEDRIFTED_VARIABLE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/${VAR}/${RUN}/dedrifted
DEDRIFTED_VARIABLE_FILES = $(patsubst ${ORIG_VARIABLE_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/${VAR}/${RUN}/${VAR}_Omon_%.nc, ${DEDRIFTED_VARIABLE_DIR}/${VAR}_Oyr_%.nc, ${VARIABLE_FILES})

VOLUME_FILE=${ORIG_FX_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/volcello/${FX_RUN}/volcello_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
BASIN_FILE=${ORIG_FX_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/basin/${FX_RUN}/basin_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc

VARIABLE_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/${VAR}-maps/${RUN}
VARIABLE_MAPS_FILE=${VARIABLE_MAPS_DIR}/${VAR}-maps_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
VARIABLE_MAPS_TIME_TREND=${VARIABLE_MAPS_DIR}/${VAR}-maps-time-trend_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.nc
VARIABLE_MAPS_VERTICAL_PLOT=${VARIABLE_MAPS_DIR}/${VAR}-maps-vertical-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
VARIABLE_MAPS_ZONAL_PLOT=${VARIABLE_MAPS_DIR}/${VAR}-maps-zonal-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}

CLIMATOLOGY_FILE=${DEDRIFTED_VARIABLE_DIR}/${VAR}-clim_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
CLIMATOLOGY_MAPS_FILE=${VARIABLE_MAPS_DIR}/${VAR}-maps-clim_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

OHC_METRICS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/${METRIC}/${RUN}
OHC_METRICS_FILE=${OHC_METRICS_DIR}/${METRIC}_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OHC_METRICS_PLOT=${OHC_METRICS_DIR}/${METRIC}_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.${FIG_TYPE}

OHC_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/ohc-maps/${RUN}
OHC_MAPS_FILE=${OHC_MAPS_DIR}/ohc-maps_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OHC_MAPS_PLOT=${OHC_MAPS_DIR}/ohc-maps_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}


# De-drift

${DRIFT_COEFFICIENTS} :
	mkdir -p ${CONTROL_DIR} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py ${CONTROL_FILES} $@ --var ${LONG_NAME} --annual

${DEDRIFTED_VARIABLE_DIR} : ${DRIFT_COEFFICIENTS}
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py ${VARIABLE_FILES} ${LONG_NAME} $< $@/ --annual

# Core data

${CLIMATOLOGY_FILE} : ${DEDRIFTED_VARIABLE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${DEDRIFTED_VARIABLE_FILES} ${LONG_NAME} $@

# VARIABLE maps

${VARIABLE_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${VARIABLE_MAPS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_maps.py ${DEDRIFTED_VARIABLE_FILES} ${LONG_NAME} $@ --climatology_file $< 
        #--chunk --basin_file ${BASIN_FILE}

${CLIMATOLOGY_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_maps.py $< ${LONG_NAME} $@ 
        # --basin_file ${BASIN_FILE}

${VARIABLE_MAPS_TIME_TREND} : ${VARIABLE_MAPS_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py $< $@ --time_bounds ${START_DATE} ${END_DATE}

${VARIABLE_MAPS_VERTICAL_PLOT} : ${VARIABLE_MAPS_TIME_TREND}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< ${LONG_NAME} vertical_mean $@  --vm_ticks ${VM_TICK_MAX} ${VM_TICK_STEP} --scale_factor ${SCALE_FACTOR} --vm_tick_scale 4 1 2 2 6 --palette ${PALETTE} 

${VARIABLE_MAPS_ZONAL_PLOT} : ${VARIABLE_MAPS_TIME_TREND} ${CLIMATOLOGY_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< ${LONG_NAME} zonal_mean $@ --zm_ticks ${ZM_TICK_MAX} ${ZM_TICK_STEP} --scale_factor ${SCALE_FACTOR} --palette ${PALETTE} --climatology_file $(word 2,$^)

# OHC metrics

${OHC_METRICS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${OHC_METRICS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc_metrics.py ${DEDRIFTED_VARIABLE_FILES} ${LONG_NAME} $@ --climatology_file $< --max_depth ${MAX_DEPTH} ${REF} --volume_file ${VOLUME_FILE}

${OHC_METRICS_PLOT} : ${OHC_METRICS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ohc_metric_timeseries.py $< $@ ${REF}

# OHC maps

${OHC_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${OHC_MAPS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc_maps.py ${DEDRIFTED_VARIABLE_FILES} ${LONG_NAME} $@ --climatology_file $< --max_depth ${MAX_DEPTH}

${OHC_MAPS_PLOT} : ${OHC_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ohc_trend.py $< $@ --time ${START_DATE} ${END_DATE} 

