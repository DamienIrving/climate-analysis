# zw_index_comparisons.mk
#
# Description: Compare various indices
#
# To execute:
#   make -n -B -f zw_index_comparisons.mk  (-n is a dry run) (-B is a force make)

# Define marcos
include zw_config.mk
include zw_base.mk

all : ${TARGET}


# PWI vs wavenumber 3

METRIC_VS_WAVE3_PLOT=${ZWINDEX_DIR}/${METRIC}-vs-wave3_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
${METRIC_VS_WAVE3_PLOT} : ${WAVE_STATS} ${FOURIER_INFO}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) ${METRIC} $(word 2,$^) wave3_amp $@ --colour $(word 2,$^) wave4_amp --normalise --trend_line --zero_lines --thin 3 --cmap hot_r --ylabel wave_3 --xlabel my_index --ylat ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} ${MER_METHOD} --clat ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} ${MER_METHOD}


# PWI vs ZW3 index

METRIC_VS_ZW3_PLOT=${ZWINDEX_DIR}/${METRIC}-vs-zw3index_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
${METRIC_VS_ZW3_PLOT} : ${WAVE_STATS} ${ZW3_INDEX} ${FOURIER_INFO}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) ${METRIC} $(word 2,$^) zw3 $@ --colour $(word 3,$^) wave3_phase --normalise --trend_line --zero_lines --thin 3 --cmap jet --ylabel ZW3_index --xlabel planetary_wave_index --clat ${LAT_SINGLE} ${LAT_SINGLE} none


# PWI vs SAM and ENSO

METRIC_VS_ENSO_PLOT=${ZWINDEX_DIR}/${METRIC}-vs-NINO34_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
${METRIC_VS_ENSO_PLOT} : ${WAVE_STATS} ${NINO34_INDEX} 
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) ${METRIC} $(word 2,$^) nino34 $@ --trend_line --zero_lines

METRIC_VS_SAM_PLOT=${ZWINDEX_DIR}/${METRIC}-vs-SAM_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
${METRIC_VS_SAM_PLOT} : ${WAVE_STATS} ${SAM_INDEX} 
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) ${METRIC} $(word 2,$^) sam $@ --trend_line --zero_lines

METRIC_VS_ENSO_VS_SAM_PLOT=${ZWINDEX_DIR}/${METRIC}-vs-nino34-vs-sam_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
${METRIC_VS_ENSO_VS_SAM_PLOT} : ${NINO34_INDEX} ${SAM_INDEX} ${WAVE_STATS}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) nino34 $(word 2,$^) sam $@ --colour $(word 3,$^) ${METRIC} --trend_line --zero_lines


# PWI vs ASL

METRIC_VS_ASL_PLOT=${ZWINDEX_DIR}/${METRIC}-vs-asl_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
${METRIC_VS_ASL_PLOT} : ${WAVE_STATS} ${ASL_INDEX}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) ${METRIC} $(word 2,$^) asl $@ --trend_line --zero_lines --ylabel amundsen_sea_low --xlabel planetary_wave_index



# Composite circulation for the ZW3 index

## Step 1: Generate list of dates for use in composite creation
ZW3_DATE_LIST=${COMP_DIR}/dates_zw_zw3${METRIC_HIGH_THRESH}_${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.txt 
${ZW3_DATE_LIST} : ${ZW3_INDEX} 
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< zw3 $@ --metric_threshold ${METRIC_HIGH_THRESH}

## Step 2: Get the composite mean contour
CONTOUR_ZONAL_ANOM_RUNMEAN_ZW3COMP=${COMP_DIR}/${CONTOUR_VAR}-composite_zw_zw3${METRIC_HIGH_THRESH}_${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc 
${CONTOUR_ZONAL_ANOM_RUNMEAN_ZW3COMP} : ${CONTOUR_ZONAL_ANOM_RUNMEAN} ${ZW3_DATE_LIST} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ${CONTOUR_VAR} $@ --date_file $(word 2,$^) --region sh

## Step 3: Plot
ZW3COMP_VAR_PLOT=${COMP_DIR}/${CONTOUR_VAR}-composite_zw_zw3${METRIC_HIGH_THRESH}_${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.png
${ZW3COMP_VAR_PLOT} : ${CONTOUR_ZONAL_ANOM_RUNMEAN_ZW3COMP}
	bash ${VIS_SCRIPT_DIR}/plot_composite_contour.sh $< ${CONTOUR_VAR} $@ ${PYTHON} ${VIS_SCRIPT_DIR}

