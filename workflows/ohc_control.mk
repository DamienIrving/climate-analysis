# ohc_control.mk
#
# Description: Control experiment data used for de-drifting ocean heat content results 
#


# Filenames

CONTROL_TEMPERATURE_FILES=$(wildcard ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/thetao/${CONTROL_RUN}/thetao_Omon_${MODEL}_piControl_${CONTROL_RUN}_*.nc)
CONTROL_VOLUME_FILE=$(wildcard ${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/fx/ocean/volcello/r0i0p0/volcello_fx_${MODEL}_piControl_r0i0p0.nc)

CONTROL_CLIMATOLOGY_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/thetao/${CONTROL_RUN}/thetao_Omon_${MODEL}_piControl_${CONTROL_RUN}_annual-climatology.nc

CONTROL_OHC_METRICS_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/ohc-metrics/${CONTROL_RUN}/ohc-metrics_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc
CONTROL_OHC_MAPS_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/ohc/${CONTROL_RUN}/ohc_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc

CONTROL_OHC_METRICS_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/ohc-metrics/${CONTROL_RUN}/ohc-metrics_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc
CONTROL_OHC_MAPS_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/ohc-maps/${CONTROL_RUN}/ohc-maps_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc

CONTROL_OHC_METRICS_COEFFICIENTS=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/ohc-metrics-coefficients/${CONTROL_RUN}/ohc-metrics-coefficients_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc
CONTROL_OHC_MAPS_COEFFICIENTS=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/piControl/mon/ocean/ohc-maps-coefficients/${CONTROL_RUN}/ohc-maps-coefficients_Omon_${MODEL}_piControl_${CONTROL_RUN}_all.nc


${CONTROL_CLIMATOLOGY_FILE} : 
	python ${DATA_SCRIPT_DIR}/calc_climatology.py ${CONTROL_TEMPERATURE_FILES} $@


# OHC metrics
${CONTROL_OHC_METRICS_FILE} : ${CONTROL_CLIMATOLOGY_FILE}
	python ${DATA_SCRIPT_DIR}/calc_ohc_metrics.py ${CONTROL_TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $< --volume_file ${CONTROL_VOLUME_FILE}

${CONTROL_OHC_METRICS_COEFFICIENTS} : ${CONTROL_OHC_METRICS_FILE}
	python ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< $@ 


# OHC maps

${CONTROL_OHC_MAPS_FILE} : ${CONTROL_CLIMATOLOGY_FILE}
	python ${DATA_SCRIPT_DIR}/calc_ohc_maps.py ${CONTROL_TEMPERATURE_FILES} sea_water_potential_temperature $@ --climatology_file $<

${CONTROL_OHC_MAPS_COEFFICIENTS} : ${CONTROL_OHC_MAPS_FILE}
	python ${DATA_SCRIPT_DIR}/calc_drift_coefficients.py $< $@



