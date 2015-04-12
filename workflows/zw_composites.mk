# zw_composites.mk
#
# Description: Calculate composite for variable of interest (e.g. tas, pr, sic)
#
# Composite methods:
#   variable: calculate composite mean variable for times where index exceeds threshold
#   index: calculate composite mean index for times where variable anomaly exceeds threshold 
#
# Thresholds:
#   upper: e.g. > 90th percentile
#   lower: e.g. < 10th percentile  
#
# To execute:
#   make -n -B -f zw_composites.mk  (-n is a dry run) (-B is a force make)

# Define marcos
include zw_config.mk
include zw_base.mk

all : ${TARGET}

# Baseline anomaly data (calculates anomaly then running mean)

## Surface variable of interest (temporal anomaly)

CVAR_ORIG=${DATA_DIR}/${COMP_VAR}_${DATASET}_surface_daily_native.nc
CVAR_ANOM_RUNMEAN=${DATA_DIR}/${COMP_VAR}_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc
${CVAR_ANOM_RUNMEAN} : ${CVAR_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	bash ${CDO_FIX_SCRIPT} $@ ${COMP_VAR}


# Streamfunction composites (for contours)

## Temporal anomaly
COMP_SF_ANOM_RUNMEAN=${COMP_DIR}/sf-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN} : ${SF_ANOM_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --region shextropics15

COMP_SF_ANOM_RUNMEAN_INDEX_HIGH=${COMP_DIR}/sf-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH} : ${SF_ANOM_RUNMEAN} ${DATES_${INDEX_CAPS}_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

COMP_SF_ANOM_RUNMEAN_INDEX_LOW=${COMP_DIR}/sf-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN_INDEX_LOW} : ${SF_ANOM_RUNMEAN} ${DATES_${INDEX_CAPS}_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

## Zonal anomaly
COMP_SF_ZONAL_ANOM_RUNMEAN=${COMP_DIR}/sf-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.nc 
${COMP_SF_ZONAL_ANOM_RUNMEAN} : ${SF_ZONAL_ANOM_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --region shextropics15

COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH=${COMP_DIR}/sf-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.nc 
${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH} : ${SF_ZONAL_ANOM_RUNMEAN} ${DATES_${INDEX_CAPS}_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_LOW=${COMP_DIR}/sf-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.nc 
${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_LOW} : ${SF_ZONAL_ANOM_RUNMEAN} ${DATES_${INDEX_CAPS}_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15


# Summary composites

## All timesteps

COMP_V_RUNMEAN=${COMP_DIR}/va-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_V_RUNMEAN} : ${V_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< va $@ --region shextropics15

COMP_U_RUNMEAN=${COMP_DIR}/ua-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_U_RUNMEAN} : ${U_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ua $@ --region shextropics15

COMP_ENV_RUNMEAN=${COMP_DIR}/envva-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_ENV_RUNMEAN} : ${ENV_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< envva $@ --region shextropics15

COMP_SUMMARY_PLOT=${COMP_DIR}/sf-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.png
${COMP_SUMMARY_PLOT} : ${COMP_SF_ZONAL_ANOM_RUNMEAN} ${COMP_U_RUNMEAN} ${COMP_V_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_summary_composite.sh $(word 1,$^) sf $(word 2,$^) ua $(word 3,$^) va $@ streamlines ${PYTHON} ${VIS_SCRIPT_DIR}


## Index > high threshold

### Spatial composite
COMP_V_RUNMEAN_INDEX_HIGH=${COMP_DIR}/va-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_V_RUNMEAN_INDEX_HIGH} : ${V_RUNMEAN} ${DATES_${INDEX_CAPS}_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< va $@ --date_file $(word 2,$^) --region shextropics15

COMP_U_RUNMEAN_INDEX_HIGH=${COMP_DIR}/ua-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_U_RUNMEAN_INDEX_HIGH} : ${U_RUNMEAN} ${DATES_${INDEX_CAPS}_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ua $@ --date_file $(word 2,$^) --region shextropics15

COMP_SUMMARY_PLOT_INDEX_HIGH=${COMP_DIR}/sf-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.png
${COMP_SUMMARY_PLOT_INDEX_HIGH} : ${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH} ${COMP_U_RUNMEAN_INDEX_HIGH} ${COMP_V_RUNMEAN_INDEX_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_summary_composite.sh $(word 1,$^) sf $(word 2,$^) ua $(word 3,$^) va $@ streamlines ${PYTHON} ${VIS_SCRIPT_DIR}

### Temporal histograms
DATES_INDEX_HIGH_PLOT=${INDEX_DIR}/dates-summary_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.png
${DATES_INDEX_HIGH_PLOT} : ${DATES_${INDEX_CAPS}_HIGH}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_date_list.py $< $@ --start ${START} --end ${END}

## Index < low threshold

COMP_V_RUNMEAN_INDEX_LOW=${COMP_DIR}/va-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_V_RUNMEAN_INDEX_LOW} : ${V_RUNMEAN} ${DATES_${INDEX_CAPS}_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< va $@ --date_file $(word 2,$^) --region shextropics15

COMP_U_RUNMEAN_INDEX_LOW=${COMP_DIR}/ua-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-shextropics15.nc 
${COMP_U_RUNMEAN_INDEX_LOW} : ${U_RUNMEAN} ${DATES_${INDEX_CAPS}_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ua $@ --date_file $(word 2,$^) --region shextropics15

COMP_SUMMARY_PLOT_INDEX_LOW=${COMP_DIR}/sf-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.png
${COMP_SUMMARY_PLOT_INDEX_LOW} : ${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_LOW} ${COMP_U_RUNMEAN_INDEX_LOW} ${COMP_V_RUNMEAN_INDEX_LOW}
	bash ${VIS_SCRIPT_DIR}/plot_summary_composite.sh $(word 1,$^) sf $(word 2,$^) ua $(word 3,$^) va $@ streamlines ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, upper threshold of index

COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH=${COMP_DIR}/${COMP_VAR}-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH} : ${CVAR_ANOM_RUNMEAN} ${DATES_${INDEX_CAPS}_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ${COMP_VAR} $@ --date_file $(word 2,$^) --region shextropics15 

COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH_PLOT=${COMP_DIR}/${COMP_VAR}-composite_${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH_PLOT} : ${COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH} ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_composite.sh $(word 1,$^) ${COMP_VAR} $(word 2,$^) sf $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, upper threshold of index + Nino phases

## Step 1: Combine the index and nino date lists
DATES_INDEX_HIGH_ELNINO=${INDEX_DIR}/dates_nino34elnino-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_INDEX_HIGH_ELNINO} : ${DATES_ELNINO} ${DATES_${INDEX_CAPS}_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

DATES_INDEX_HIGH_LANINA=${INDEX_DIR}/dates_nino34lanina-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_INDEX_HIGH_LANINA} : ${DATES_LANINA} ${DATES_${INDEX_CAPS}_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

## Step 2: Calculate the Nino contour composites
COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_ELNINO=${COMP_DIR}/sf-composite_nino34elnino-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_ELNINO} : ${SF_ANOM_RUNMEAN} ${DATES_INDEX_HIGH_ELNINO} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_LANINA=${COMP_DIR}/sf-composite_nino34lanina-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_LANINA} : ${SF_ANOM_RUNMEAN} ${DATES_INDEX_HIGH_LANINA} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

## Step 3: Plot
COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH_NINO_PLOT=${COMP_DIR}/sf-composite_nino-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH_NINO_PLOT} : ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_ELNINO} ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH} ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_LANINA}
	bash ${VIS_SCRIPT_DIR}/plot_variability_composite.sh $(word 1,$^) $(word 2,$^) $(word 3,$^) sf $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, upper threshold of index + SAM phases

## Step 1: Combine the index and SAM date lists
DATES_INDEX_HIGH_SAM_POS=${INDEX_DIR}/dates_samgt75pct-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_INDEX_HIGH_SAM_POS} : ${DATES_SAM_POS} ${DATES_${INDEX_CAPS}_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

DATES_INDEX_HIGH_SAM_NEG=${INDEX_DIR}/dates_samlt75pct-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_INDEX_HIGH_SAM_NEG} : ${DATES_SAM_NEG} ${DATES_${INDEX_CAPS}_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

## Step 2: Calculate the SAM contour composites

### Temporal anomaly
COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_SAM_POS=${COMP_DIR}/sf-composite_samgt75pct-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_SAM_POS} : ${SF_ANOM_RUNMEAN} ${DATES_INDEX_HIGH_SAM_POS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_SAM_NEG=${COMP_DIR}/sf-composite_samlt25pct-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_SAM_NEG} : ${SF_ANOM_RUNMEAN} ${DATES_INDEX_HIGH_SAM_NEG} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

### Zonal anomaly
COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_POS=${COMP_DIR}/sf-composite_samgt75pct-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.nc 
${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_POS} : ${SF_ZONAL_ANOM_RUNMEAN} ${DATES_INDEX_HIGH_SAM_POS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_NEG=${COMP_DIR}/sf-composite_samlt25pct-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.nc 
${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_NEG} : ${SF_ZONAL_ANOM_RUNMEAN} ${DATES_INDEX_HIGH_SAM_NEG} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< sf $@ --date_file $(word 2,$^) --region shextropics15

## Step 3: Plot

### Temporal anomaly
COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH_SAM_PLOT=${COMP_DIR}/sf-composite_sam-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_CVAR_ANOM_RUNMEAN_INDEX_HIGH_SAM_PLOT} : ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_SAM_POS} ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH} ${COMP_SF_ANOM_RUNMEAN_INDEX_HIGH_SAM_NEG}
	bash ${VIS_SCRIPT_DIR}/plot_variability_composite.sh $(word 1,$^) $(word 2,$^) $(word 3,$^) sf $@ ${PYTHON} ${VIS_SCRIPT_DIR}

### Zonal anomaly
COMP_CVAR_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_PLOT=${COMP_DIR}/sf-composite_sam-${INDEX}gt${INDEX_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom-shextropics15.png
${COMP_CVAR_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_PLOT} : ${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_POS} ${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH} ${COMP_SF_ZONAL_ANOM_RUNMEAN_INDEX_HIGH_SAM_NEG}
	bash ${VIS_SCRIPT_DIR}/plot_variability_composite.sh $(word 1,$^) $(word 2,$^) $(word 3,$^) sf $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, lower threshold of index

COMP_CVAR_ANOM_RUNMEAN_INDEX_LOW=${COMP_DIR}/${COMP_VAR}-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc 
${COMP_CVAR_ANOM_RUNMEAN_INDEX_LOW} : ${CVAR_ANOM_RUNMEAN} ${DATES_${INDEX_CAPS}_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ${COMP_VAR} $@ --date_file $(word 2,$^) --region shextropics15 

COMP_CVAR_ANOM_RUNMEAN_INDEX_LOW_PLOT=${COMP_DIR}/${COMP_VAR}-composite_${INDEX}lt${INDEX_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_CVAR_ANOM_RUNMEAN_INDEX_LOW_PLOT} : ${COMP_CVAR_ANOM_RUNMEAN_INDEX_LOW} ${COMP_SF_ANOM_RUNMEAN_INDEX_LOW}
	bash ${VIS_SCRIPT_DIR}/plot_composite.sh $(word 1,$^) ${COMP_VAR} $(word 2,$^) sf $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Index composite, upper threshold

COMP_INDEX_CVAR_ANOM_RUNMEAN_HIGH=${COMP_DIR}/${INDEX}-composite_${COMP_VAR}90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc
${COMP_INDEX_CVAR_ANOM_RUNMEAN_HIGH} : ${CVAR_ANOM_RUNMEAN} ${${INDEX_CAPS}_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_index_composite.py $(word 1,$^) ${COMP_VAR} $(word 2,$^) ${INDEX} 90pct $@ --region shextropics15

COMP_INDEX_CVAR_ANOM_RUNMEAN_HIGH_PLOT=${COMP_DIR}/${INDEX}-composite_${COMP_VAR}90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_INDEX_CVAR_ANOM_RUNMEAN_HIGH_PLOT} : ${COMP_INDEX_CVAR_ANOM_RUNMEAN_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_index_composite.sh $< ${INDEX} 90pct $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Index composite, lower threshold

COMP_INDEX_CVAR_ANOM_RUNMEAN_LOW=${COMP_DIR}/${INDEX}-composite_${COMP_VAR}10pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc
${COMP_INDEX_CVAR_ANOM_RUNMEAN_LOW} : ${CVAR_ANOM_RUNMEAN} ${${INDEX_CAPS}_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_index_composite.py $(word 1,$^) ${COMP_VAR} $(word 2,$^) ${INDEX} 90pct $@ --region shextropics15 --include below

COMP_INDEX_CVAR_ANOM_RUNMEAN_LOW_PLOT=${COMP_DIR}/${INDEX}-composite_${COMP_VAR}10pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_INDEX_CVAR_ANOM_RUNMEAN_LOW_PLOT} : ${COMP_INDEX_CVAR_ANOM_RUNMEAN_LOW}
	bash ${VIS_SCRIPT_DIR}/plot_index_composite.sh $< ${INDEX} 10pct $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Index composite, upper threshold (absolute value anomalies)

COMP_INDEX_CVAR_ANOM_RUNMEAN_ABS_HIGH=${COMP_DIR}/${INDEX}-composite_${COMP_VAR}abs90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.nc
${COMP_INDEX_CVAR_ANOM_RUNMEAN_ABS_HIGH} : ${CVAR_ANOM_RUNMEAN} ${${INDEX_CAPS}_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_index_composite.py $(word 1,$^) ${COMP_VAR} $(word 2,$^) ${INDEX} 90pct $@ --region shextropics15 --absolute

COMP_INDEX_CVAR_ANOM_RUNMEAN_ABS_HIGH_PLOT=${COMP_DIR}/${INDEX}-composite_${COMP_VAR}abs90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-shextropics15.png
${COMP_INDEX_CVAR_ANOM_RUNMEAN_ABS_HIGH_PLOT} : ${COMP_INDEX_CVAR_ANOM_RUNMEAN_ABS_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_index_composite.sh $< ${INDEX} 90pctabs $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# ASL composite, upper threshold of index
 
# bash calc_asl_composite.sh
