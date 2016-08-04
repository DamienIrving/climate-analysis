# ohc_base.mk
#
# Description: Core ocean heat content workflows 
#
# To execute:
#      1. copy name of target file from ohc_base.mk 
#      2. paste it into ohc_config.mk as the target variable  
#      2. $ make -n -B -f ohc_base.mk  (-n is a dry run) (-B is a force make)


# Define marcos

include ohc_config.mk
all : ${TARGET}

# Filenames

CONTROL_FILES=$(wildcard ${ORIG_CONTROL_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/thetao/${CONTROL_RUN}/thetao_Omon_${MODEL}_piControl_${CONTROL_RUN}_*.nc)
CONTROL_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/thetao/${CONTROL_RUN}
DRIFT_COEFFICIENTS=${CONTROL_DIR}/thetao-coefficients_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc

TEMPERATURE_FILES=$(wildcard ${ORIG_TEMPERATURE_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)

DEDRIFTED_TEMPERATURE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/dedrifted
DEDRIFTED_TEMPERATURE_FILES = $(patsubst ${ORIG_TEMPERATURE_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_%.nc, ${DEDRIFTED_TEMPERATURE_DIR}/thetao_%.nc, ${TEMPERATURE_FILES})

VOLUME_FILE=${ORIG_VOLUME_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/volcello/${VOLUME_RUN}/volcello_fx_${MODEL}_${EXPERIMENT}_${VOLUME_RUN}.nc

CLIMATOLOGY_FILE=${DEDRIFTED_TEMPERATURE_DIR}/thetao-annual-clim_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

TEMPERATURE_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao-maps/${RUN}
TEMPERATURE_MAPS_FILE=${TEMPERATURE_MAPS_DIR}/thetao-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
TEMPERATURE_MAPS_VERTICAL_PLOT=${TEMPERATURE_MAPS_DIR}/thetao-maps-vertical-mean_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
TEMPERATURE_MAPS_ZONAL_PLOT=${TEMPERATURE_MAPS_DIR}/thetao-maps-zonal-mean_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}

OHC_METRICS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/${METRIC}/${RUN}
OHC_METRICS_FILE=${OHC_METRICS_DIR}/${METRIC}_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OHC_METRICS_PLOT=${OHC_METRICS_DIR}/${METRIC}_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.${FIG_TYPE}

OHC_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc-maps/${RUN}
OHC_MAPS_FILE=${OHC_MAPS_DIR}/ohc-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OHC_MAPS_PLOT=${OHC_MAPS_DIR}/ohc-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
OHC_SEASONAL_CYCLE_PLOT=${OHC_MAPS_DIR}/ohc-maps-seasonal-cycle_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}


# De-drift

${DRIFT_COEFFICIENTS} :
	mkdir -p ${CONTROL_DIR} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py ${CONTROL_FILES} $@ --var sea_water_potential_temperature

${DEDRIFTED_TEMPERATURE_DIR} : ${DRIFT_COEFFICIENTS}
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py ${TEMPERATURE_FILES} sea_water_potential_temperature $< $@/

# Core data

${CLIMATOLOGY_FILE} : ${DEDRIFTED_TEMPERATURE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@

# Temperature maps

${TEMPERATURE_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${TEMPERATURE_MAPS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_maps.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $<

${TEMPERATURE_MAPS_VERTICAL_PLOT} : ${TEMPERATURE_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< sea_water_potential_temperature vertical_mean $@ --time ${START_DATE} ${END_DATE} --vm_tick_scale 4 1 2 2 6

${TEMPERATURE_MAPS_ZONAL_PLOT} : ${TEMPERATURE_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< sea_water_potential_temperature zonal_mean $@ --time ${START_DATE} ${END_DATE}

# OHC metrics

${OHC_METRICS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${OHC_METRICS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc_metrics.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $< --max_depth ${MAX_DEPTH} ${REF}

${OHC_METRICS_PLOT} : ${OHC_METRICS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ohc_metric_timeseries.py $< $@ ${REF}

# OHC maps

${OHC_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${OHC_MAPS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc_maps.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $< --max_depth ${MAX_DEPTH}

${OHC_MAPS_PLOT} : ${OHC_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ohc_trend.py $< $@ --time ${START_DATE} ${END_DATE} 

${OHC_SEASONAL_CYCLE_PLOT} : ${OHC_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ohc_trend.py $< $@ --time ${START_DATE} ${END_DATE} --seasonal_cycle
