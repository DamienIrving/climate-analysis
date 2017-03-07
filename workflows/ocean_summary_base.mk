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

VOLUME_FILE=${ORIG_VOL_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/volcello/${FX_RUN}/volcello_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
BASIN_FILE=${ORIG_BASIN_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/basin/${FX_RUN}/basin_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
DEPTH_FILE=${ORIG_DEPTH_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/deptho/${FX_RUN}/deptho_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
ATMOS_AREA_FILE=${ORIG_AREAA_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/atmos/areacella/${FX_RUN}/areacella_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
OCEAN_AREA_FILE=${ORIG_AREAO_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/ocean/areacello/${FX_RUN}/areacello_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc
SFTLF_FILE=${ORIG_SFTLF_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/fx/atmos/sftlf/${FX_RUN}/sftlf_fx_${MODEL}_${EXPERIMENT}_${FX_RUN}.nc

SO_FILE=$(wildcard ${ORIG_SO_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/so/${RUN}/so_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_SO_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/so/${RUN}
GLOBAL_MEAN_SO_FILE=${GLOBAL_SO_DIR}/so-global-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_GRIDDEV_SO_FILE=${GLOBAL_SO_DIR}/so-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

TAS_FILE=$(wildcard ${ORIG_TAS_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/tas/${RUN}/tas_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_TAS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/tas/${RUN}
GLOBAL_MEAN_TAS_FILE=${GLOBAL_MEAN_TAS_DIR}/tas-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

SOS_FILE=$(wildcard ${ORIG_SOS_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/sos/${RUN}/sos_Omon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_SOS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/sos/${RUN}
GLOBAL_GRIDDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-griddev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_BULKDEV_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-bulkdev_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
SOS_CLIM_FILE=${GLOBAL_SOS_DIR}/sos-clim_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
GLOBAL_MYAMP_SOS_FILE=${GLOBAL_SOS_DIR}/sos-global-myamp_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

PR_FILE=$(wildcard ${ORIG_PR_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/pr/${RUN}/pr_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_PR_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/pr/${RUN}
GLOBAL_MEAN_PR_FILE=${GLOBAL_MEAN_PR_DIR}/pr-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

EVSPSBL_DIR=${ORIG_EVSPSBL_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/evspsbl/${RUN}
EVSPSBL_FILE=$(wildcard ${EVSPSBL_DIR}/evspsbl_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc)
GLOBAL_MEAN_EVSPSBL_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/evspsbl/${RUN}
GLOBAL_MEAN_EVSPSBL_FILE=${GLOBAL_MEAN_EVSPSBL_DIR}/evspsbl-global-mean_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

PE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/atmos/pe/${RUN}
GLOBAL_PE_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/atmos/pe/${RUN}
GLOBAL_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-global-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
OCEAN_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-ocean-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
LAND_GRIDDEV_PE_FILE=${GLOBAL_PE_DIR}/pe-land-griddev_Ayr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc

GLOBAL_METRICS=global_metrics.nc

VARIABLE_MAPS_DIR=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/yr/ocean/${VAR}-maps/${RUN}
VARIABLE_MAPS_FILE=${VARIABLE_MAPS_DIR}/${VAR}-maps_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
VARIABLE_MAPS_TIME_TREND=${VARIABLE_MAPS_DIR}/${VAR}-maps-time-trend_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.nc
VARIABLE_MAPS_TAS_TREND=${VARIABLE_MAPS_DIR}/${VAR}-maps-tas-trend_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.nc
VARIABLE_MAPS_TIME_VERTICAL_PLOT=${VARIABLE_MAPS_DIR}/${VAR}-maps-time-trend-vertical-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
VARIABLE_MAPS_TIME_ZONAL_PLOT=${VARIABLE_MAPS_DIR}/${VAR}-maps-time-trend-zonal-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
VARIABLE_MAPS_TAS_VERTICAL_PLOT=${VARIABLE_MAPS_DIR}/${VAR}-maps-global-tas-trend-vertical-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}
VARIABLE_MAPS_TAS_ZONAL_PLOT=${VARIABLE_MAPS_DIR}/${VAR}-maps-global-tas-trend-zonal-mean_Oyr_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}

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
        #--no_parent_check

# Core data

${CLIMATOLOGY_FILE} : ${DEDRIFTED_VARIABLE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${DEDRIFTED_VARIABLE_FILES} ${LONG_NAME} $@

# Variable maps

${VARIABLE_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	mkdir -p ${VARIABLE_MAPS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_maps.py ${DEDRIFTED_VARIABLE_FILES} ${LONG_NAME} $@ --climatology_file $<
        #--chunk x --basin_file ${BASIN_FILE} --depth_file ${DEPTH_FILE}

${CLIMATOLOGY_MAPS_FILE} : ${CLIMATOLOGY_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_ocean_maps.py $< ${LONG_NAME} $@ 
        # --basin_file ${BASIN_FILE}  --depth_file ${DEPTH_FILE}

${VARIABLE_MAPS_TIME_TREND} : ${VARIABLE_MAPS_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py $< $@ --time_bounds ${START_DATE} ${END_DATE}

${VARIABLE_MAPS_TIME_VERTICAL_PLOT} : ${VARIABLE_MAPS_TIME_TREND}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< ${LONG_NAME} vertical_mean $@ --scale_factor ${SCALE_FACTOR} --vm_tick_scale 4 1 2 2 6 --palette ${PALETTE} --vm_ticks ${VM_TICK_MAX} ${VM_TICK_STEP}

${VARIABLE_MAPS_TIME_ZONAL_PLOT} : ${VARIABLE_MAPS_TIME_TREND} ${CLIMATOLOGY_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< ${LONG_NAME} zonal_mean $@ --scale_factor ${SCALE_FACTOR} --palette ${PALETTE} --climatology_file $(word 2,$^) --zm_ticks ${ZM_TICK_MAX} ${ZM_TICK_STEP}

# Trends against global mean temperature

${GLOBAL_MEAN_TAS_FILE} :  
	mkdir -p ${GLOBAL_MEAN_TAS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${TAS_FILE} air_temperature mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${VARIABLE_MAPS_TAS_TREND} : ${VARIABLE_MAPS_FILE} ${GLOBAL_MEAN_TAS_FILE} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_trend.py $< $@ --time_bounds ${START_DATE} ${END_DATE} --xaxis $(word 2,$^) air_temperature

${VARIABLE_MAPS_TAS_VERTICAL_PLOT} : ${VARIABLE_MAPS_TAS_TREND}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< ${LONG_NAME} vertical_mean $@  --vm_ticks ${VM_TICK_MAX} ${VM_TICK_STEP} --vm_tick_scale 4 1 2 2 6 --palette ${PALETTE} 

${VARIABLE_MAPS_TAS_ZONAL_PLOT} : ${VARIABLE_MAPS_TAS_TREND} ${CLIMATOLOGY_MAPS_FILE}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_ocean_trend.py $< ${LONG_NAME} zonal_mean $@ --palette ${PALETTE} --climatology_file $(word 2,$^) --zm_ticks ${ZM_TICK_MAX} ${ZM_TICK_STEP}

## Use ocean_summary_ensembles.sh if more than one run
## Use plot_trend_comparison.sh to compare GHG to AA
## Use plot_ocean_trend_ensemble.sh to plot same basin for entire ensemble
## Use plot_integrated_ocean_trend_ensemble.py for zonal mean, vertical mean trend comparison between GHG and AA

# Global indicators

${PE_DIR} :
	mkdir -p $@
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_pe.py ${PR_FILE} precipitation_flux ${EVSPSBL_DIR} water_evaporation_flux $@

${GLOBAL_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${OCEAN_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --sftlf_file ${SFTLF_FILE} ocean

${LAND_GRIDDEV_PE_FILE} :
	mkdir -p ${GLOBAL_PE_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py $(wildcard ${PE_DIR}/pe_Amon_${MODEL}_${EXPERIMENT}_${RUN}_*.nc) precipitation_minus_evaporation_flux grid-deviation $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual --sftlf_file ${SFTLF_FILE} land

${GLOBAL_BULKDEV_SOS_FILE} :
	mkdir -p ${GLOBAL_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${SOS_FILE} sea_surface_salinity bulk-deviation $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual

${GLOBAL_GRIDDEV_SOS_FILE} :  
	mkdir -p ${GLOBAL_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${SOS_FILE} sea_surface_salinity grid-deviation $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual

${SOS_CLIM_FILE} :
	mkdir -p ${GLOBAL_BULKDEV_SOS_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climatology.py ${SOS_FILE} sea_surface_salinity $@

${GLOBAL_MYAMP_SOS_FILE} : ${SOS_CLIM_FILE}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_my_salinity_amp.py ${SOS_FILE} sea_surface_salinity $< $@ --area_file ${OCEAN_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_PR_FILE} :  
	mkdir -p ${GLOBAL_MEAN_PR_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${PR_FILE} precipitation_flux mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_EVSPSBL_FILE} :  
	mkdir -p ${GLOBAL_MEAN_EVSPSBL_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_metric.py ${EVSPSBL_FILE} water_evaporation_flux mean $@ --area_file ${ATMOS_AREA_FILE} --smoothing annual

${GLOBAL_MEAN_SO_FILE} :  
	mkdir -p ${GLOBAL_SO_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_3D_metric.py ${DEDRIFTED_VARIABLE_FILES} sea_water_salinity mean $@ --volume_file ${VOLUME_FILE} --smoothing annual

${GLOBAL_GRIDDEV_SO_FILE} :  
	mkdir -p ${GLOBAL_SO_DIR}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_global_3D_metric.py ${DEDRIFTED_VARIABLE_FILES} sea_water_salinity grid-deviation $@ --volume_file ${VOLUME_FILE} --smoothing annual

${GLOBAL_METRICS} : ${GLOBAL_MEAN_TAS_FILE} ${GLOBAL_MEAN_PR_FILE} ${GLOBAL_MEAN_EVSPSBL_FILE} ${GLOBAL_BULKDEV_SOS_FILE} ${GLOBAL_GRIDDEV_SOS_FILE} ${GLOBAL_GRIDDEV_PE_FILE} ${OCEAN_GRIDDEV_PE_FILE} ${LAND_GRIDDEV_PE_FILE}
	echo generate_delsole_command.py
	echo generate_global_indicator_command.py
	echo plot_comparison_timeseries.py

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

