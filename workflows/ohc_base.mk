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

CONTROL_FILES=$(wildcard ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/thetao/${CONTROL_RUN}/thetao_Omon_${MODEL}_piControl_${CONTROL_RUN}_*.nc)
CONTROL_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/thetao/${CONTROL_RUN}
DRIFT_COEFFICIENTS=${CONTROL_DIR}/thetao-coefficients_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc

TEMPERATURE_FILES=$(wildcard ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)

DEDRIFTED_TEMPERATURE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/dedrifted
DEDRIFTED_TEMPERATURE_FILES = $(patsubst ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_%.nc, ${DEDRIFTED_TEMPERATURE_DIR}/thetao_%.nc, ${TEMPERATURE_FILES})

VOLUME_FILE=${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/volcello/${VOLUME_RUN}/volcello_fx_${MODEL}_${EXPERIMENT}_${VOLUME_RUN}.nc

CLIMATOLOGY_FILE=${DEDRIFTED_TEMPERATURE_DIR}/thetao-annual-clim_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

TEMPERATURE_METRICS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/${METRIC}/${RUN}
TEMPERATURE_METRICS_FILE=${TEMPERATURE_METRICS_DIR}/${METRIC}_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
TEMPERATURE_METRICS_PLOT=${TEMPERATURE_METRICS_DIR}/${METRIC}_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.${FIG_TYPE}

OHC_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc-maps/${RUN}
OHC_MAPS_FILE=${OHC_MAPS_DIR}/ohc-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OHC_MAPS_PLOT=${OHC_MAPS_DIR}/ohc-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}


# De-drift

${DRIFT_COEFFICIENTS} :
	mkdir -p ${CONTROL_DIR} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py ${CONTROL_FILES} $@ 

${DEDRIFTED_TEMPERATURE_DIR} : ${DRIFT_COEFFICIENTS}
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/remove_drift.py ${TEMPERATURE_FILES} $< $@/

# Core data

${CLIMATOLOGY_FILE} : ${DEDRIFTED_TEMPERATURE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@


# OHC metrics

${TEMPERATURE_METRICS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${TEMPERATURE_METRICS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_temperature_metrics.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@ --volume_file ${VOLUME_FILE} --climatology_file $< --max_depth ${MAX_DEPTH} ${REF}

${TEMPERATURE_METRICS_PLOT} : ${TEMPERATURE_METRICS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_temperature_metric_timeseries.py $< $@ ${REF}

# OHC maps

${OHC_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${OHC_MAPS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ohc_maps.py ${DEDRIFTED_TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $< --max_depth ${MAX_DEPTH}

${OHC_MAPS_PLOT} : ${OHC_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ohc_trend.py $< $@ --time ${START_DATE} ${END_DATE} 
