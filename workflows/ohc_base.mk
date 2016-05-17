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
include ohc_control.mk

# Filenames

TEMPERATURE_FILES=$(wildcard ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
VOLUME_FILE=$(wildcard ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/volcello/r0i0p0/volcello_fx_${MODEL}_${EXPERIMENT}_r0i0p0.nc)

CLIMATOLOGY_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}
CLIMATOLOGY_FILE=${CLIMATOLOGY_DIR}/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_annual-climatology.nc

TEMPERATURE_METRICS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc-metrics/${RUN}
TEMPERATURE_METRICS_FILE=${TEMPERATURE_METRICS_DIR}/ohc-metrics_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

OHC_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc-maps/${RUN}
OHC_MAPS_FILE=${OHC_MAPS_DIR}/ohc-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OHC_MAPS_PLOT=${OHC_MAPS_DIR}/ohc-maps_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}

# Core data

${CLIMATOLOGY_FILE} :
	mkdir -p ${CLIMATOLOGY_DIR} 
	python ${DATA_SCRIPT_DIR}/calc_climatology.py ${TEMPERATURE_FILES} $@


# OHC metrics

${TEMPERATURE_METRICS_FILE} : ${CLIMATOLOGY_FILE} ${CONTROL_TEMPERATURE_METRICS_COEFFICIENTS}
	mkdir -p ${TEMPERATURE_METRICS_DIR}
	python ${DATA_SCRIPT_DIR}/calc_ocean_temperature_metrics.py ${TEMPERATURE_FILES} sea_water_potential_temperature $@ --volume_file ${VOLUME_FILE} --climatology_file $< --dedrift $(word 2,$^)

#plot...

# OHC maps

${OHC_MAPS_FILE} : ${CLIMATOLOGY_FILE} ${CONTROL_OHC_MAPS_COEFFICIENTS}
	mkdir -p ${OHC_MAPS_DIR}
	python ${DATA_SCRIPT_DIR}/calc_ohc_maps.py ${TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $< --dedrift $(word 2,$^)

${OHC_MAPS_PLOT} : ${OHC_MAPS_FILE}
	python ${VIS_SCRIPT_DIR}/plot_ohc_trend.py $< $@ --time ${START_DATE} ${END_DATE} 
