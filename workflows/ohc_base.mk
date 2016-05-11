# zw_base.mk
#
# Description: Basic workflow that underpins all other ocean heat content 
#
# To execute:
#	make -n -B -f ohc_base.mk  (-n is a dry run) (-B is a force make)


# Define marcos
include ohc_config.mk

all : ${TARGET}

# Data

TEMPERATURE_FILES=${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc
VOLUME_FILE=${UA6_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/volcello/r0i0p0/volcello_fx_${MODEL}_${EXPERIMENT}_r0i0p0.nc

CLIMATOLOGY_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/thetao/${RUN}/thetao_Omon_${MODEL}_${EXPERIMENT}_${RUN}_annual-climatology.nc
${CLIMATOLOGY_FILE} : ${TEMPERATURE_FILES}
	python ${DATA_SCRIPT_DIR}/calc_climatology.py $< $@


# OHC metrics

OHC_METRICS_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc-metrics/${RUN}/ohc-metrics_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
${OHC_METRICS_FILE} : ${TEMPERATURE_FILES} ${CLIMATOLOGY_FILE} ${VOLUME_FILE}
	python ${DATA_SCRIPT_DIR}/calc_ohc_metrics.py $< sea_water_potential_temperature $@ --climatology_file $(word 2,$^) --volume_file $(word 3,$^) #--max_depth ${MAX_DEPTH}

#plot...

# OHC maps
OHC_FILE=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc/${RUN}/ohc_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
${OHC_FILE} : ${TEMPERATURE_FILES} ${CLIMATOLOGY_FILE}
	python ${DATA_SCRIPT_DIR}/calc_ohc_maps.py $< sea_water_potential_temperature $@ --climatology_file $(word 2,$^) #--max_depth ${MAX_DEPTH}

OHC_PLOT=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/ohc/${RUN}/ohc_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
${OHC_PLOT} : ${OHC_FILE}
	python ${VIS_SCRIPT_DIR}/plot_ohc_trend.py $< $@ --time ${START_DATE} ${END_DATE} 
