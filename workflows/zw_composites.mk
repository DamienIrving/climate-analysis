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


# Contour composites (zg zonal anomaly)

COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_HIGH=${COMP_DIR}/zg-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_HIGH} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh

COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_LOW=${COMP_DIR}/zg-composite_mi${METRIC_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_LOW} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh


# Summary composites

## All timesteps

COMP_V_RUNMEAN=${COMP_DIR}/va-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh.nc 
${COMP_V_RUNMEAN} : ${V_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< va $@ --region sh

COMP_U_RUNMEAN=${COMP_DIR}/ua-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh.nc 
${COMP_U_RUNMEAN} : ${U_RUNMEAN} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ua $@ --region sh

COMP_SUMMARY_PLOT=${COMP_DIR}/zg-composite_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.png
${COMP_SUMMARY_PLOT} : ${COMP_ZG_ZONAL_ANOM_RUNMEAN} ${COMP_U_RUNMEAN} ${COMP_V_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_summary_composite.sh $(word 1,$^) zg $(word 2,$^) ua $(word 3,$^) va $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## MI > 90pct

COMP_V_RUNMEAN_MI_HIGH=${COMP_DIR}/va-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh.nc 
${COMP_V_RUNMEAN_MI_HIGH} : ${V_RUNMEAN} ${DATES_MI_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< va $@ --date_file $(word 2,$^) --region sh

COMP_U_RUNMEAN_MI_HIGH=${COMP_DIR}/ua-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh.nc 
${COMP_U_RUNMEAN_MI_HIGH} : ${U_RUNMEAN} ${DATES_MI_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ua $@ --date_file $(word 2,$^) --region sh

COMP_SUMMARY_PLOT_MI_HIGH=${COMP_DIR}/zg-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.png
${COMP_SUMMARY_PLOT_MI_HIGH} : ${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_HIGH} ${COMP_U_RUNMEAN_MI_HIGH} ${COMP_V_RUNMEAN_MI_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_summary_composite.sh $(word 1,$^) zg $(word 2,$^) ua $(word 3,$^) va $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, upper threshold of MI

COMP_CVAR_ANOM_RUNMEAN_MI_HIGH=${COMP_DIR}/${COMP_VAR}-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.nc 
${COMP_CVAR_ANOM_RUNMEAN_MI_HIGH} : ${CVAR_ANOM_RUNMEAN} ${DATES_MI_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ${COMP_VAR} $@ --date_file $(word 2,$^) --region sh 

COMP_CVAR_ANOM_RUNMEAN_MI_HIGH_PLOT=${COMP_DIR}/${COMP_VAR}-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_CVAR_ANOM_RUNMEAN_MI_HIGH_PLOT} : ${COMP_CVAR_ANOM_RUNMEAN_MI_HIGH} ${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_composite.sh $(word 1,$^) ${COMP_VAR} $(word 2,$^) zg $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, upper threshold of MI + Nino phases

## Step 1: Combine the MI and nino date lists
DATES_MI_HIGH_ELNINO=${INDEX_DIR}/dates_nino34elnino-mi${METRIC_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_MI_HIGH_ELNINO} : ${DATES_ELNINO} ${DATES_MI_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

DATES_MI_HIGH_LANINA=${INDEX_DIR}/dates_nino34lanina-mi${METRIC_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_MI_HIGH_LANINA} : ${DATES_LANINA} ${DATES_MI_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

## Step 2: Calculate the Nino contour composites
COMP_ZG_ANOM_RUNMEAN_MI_HIGH_ELNINO=${COMP_DIR}/zg-composite_nino34elnino-mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_ELNINO} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_HIGH_ELNINO} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh

COMP_ZG_ANOM_RUNMEAN_MI_HIGH_LANINA=${COMP_DIR}/zg-composite_nino34lanina-mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_LANINA} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_HIGH_LANINA} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh

## Step 3: Plot
COMP_CVAR_ANOM_RUNMEAN_MI_HIGH_NINO_PLOT=${COMP_DIR}/zg-composite_nino-mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_CVAR_ANOM_RUNMEAN_MI_HIGH_NINO_PLOT} : ${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_ELNINO} ${COMP_ZG_ANOM_RUNMEAN_MI_HIGH} ${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_LANINA}
	bash ${VIS_SCRIPT_DIR}/plot_variability_composite.sh $(word 1,$^) $(word 2,$^) $(word 3,$^) zg $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, upper threshold of PWI + SAM phases

## Step 1: Combine the MI and SAM date lists
DATES_MI_HIGH_SAM_POS=${INDEX_DIR}/dates_samgt75pct-mi${METRIC_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_MI_HIGH_SAM_POS} : ${DATES_SAM_POS} ${DATES_MI_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

DATES_MI_HIGH_SAM_NEG=${INDEX_DIR}/dates_samlt75pct-mi${METRIC_HIGH_THRESH}_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_MI_HIGH_SAM_NEG} : ${DATES_SAM_NEG} ${DATES_MI_HIGH}
	${PYTHON} ${DATA_SCRIPT_DIR}/combine_dates.py $@ $< $(word 2,$^)

## Step 2: Calculate the SAM contour composites
COMP_ZG_ANOM_RUNMEAN_MI_HIGH_SAM_POS=${COMP_DIR}/zg-composite_samgt75pct-mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_SAM_POS} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_HIGH_SAM_POS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh

COMP_ZG_ANOM_RUNMEAN_MI_HIGH_SAM_NEG=${COMP_DIR}/zg-composite_samlt25pct-mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_SAM_NEG} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_HIGH_SAM_NEG} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh

## Step 3: Plot
COMP_CVAR_ANOM_RUNMEAN_MI_HIGH_SAM_PLOT=${COMP_DIR}/zg-composite_sam-mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_CVAR_ANOM_RUNMEAN_MI_HIGH_SAM_PLOT} : ${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_SAM_POS} ${COMP_ZG_ANOM_RUNMEAN_MI_HIGH} ${COMP_ZG_ANOM_RUNMEAN_MI_HIGH_SAM_NEG}
	bash ${VIS_SCRIPT_DIR}/plot_variability_composite.sh $(word 1,$^) $(word 2,$^) $(word 3,$^) zg $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Variable composite, lower threshold of PWI

COMP_CVAR_ANOM_RUNMEAN_MI_LOW=${COMP_DIR}/${COMP_VAR}-composite_mi${METRIC_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.nc 
${COMP_CVAR_ANOM_RUNMEAN_MI_LOW} : ${CVAR_ANOM_RUNMEAN} ${DATES_MI_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ${COMP_VAR} $@ --date_file $(word 2,$^) --region sh 

COMP_CVAR_ANOM_RUNMEAN_MI_LOW_PLOT=${COMP_DIR}/${COMP_VAR}-composite_mi${METRIC_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_CVAR_ANOM_RUNMEAN_MI_LOW_PLOT} : ${COMP_CVAR_ANOM_RUNMEAN_MI_LOW} ${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_LOW}
	bash ${VIS_SCRIPT_DIR}/plot_composite.sh $(word 1,$^) ${COMP_VAR} $(word 2,$^) zg $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Index composite, upper threshold

COMP_MI_CVAR_ANOM_RUNMEAN_HIGH=${COMP_DIR}/mi-composite_${COMP_VAR}90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.nc
${COMP_MI_CVAR_ANOM_RUNMEAN_HIGH} : ${CVAR_ANOM_RUNMEAN} ${MI_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_index_composite.py $(word 1,$^) ${COMP_VAR} $(word 2,$^) mi 90pct $@ --region sh

COMP_MI_CVAR_ANOM_RUNMEAN_HIGH_PLOT=${COMP_DIR}/mi-composite_${COMP_VAR}90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_MI_CVAR_ANOM_RUNMEAN_HIGH_PLOT} : ${COMP_MI_CVAR_ANOM_RUNMEAN_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_index_composite.sh $< mi 90pct $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Index composite, lower threshold

COMP_MI_CVAR_ANOM_RUNMEAN_LOW=${COMP_DIR}/mi-composite_${COMP_VAR}10pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.nc
${COMP_MI_CVAR_ANOM_RUNMEAN_LOW} : ${CVAR_ANOM_RUNMEAN} ${MI_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_index_composite.py $(word 1,$^) ${COMP_VAR} $(word 2,$^) mi 90pct $@ --region sh --include below

COMP_MI_CVAR_ANOM_RUNMEAN_LOW_PLOT=${COMP_DIR}/mi-composite_${COMP_VAR}10pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_MI_CVAR_ANOM_RUNMEAN_LOW_PLOT} : ${COMP_MI_CVAR_ANOM_RUNMEAN_LOW}
	bash ${VIS_SCRIPT_DIR}/plot_index_composite.sh $< mi 10pct $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Index composite, upper threshold (absolute value anomalies)

COMP_MI_CVAR_ANOM_RUNMEAN_ABS_HIGH=${COMP_DIR}/mi-composite_${COMP_VAR}abs90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.nc
${COMP_MI_CVAR_ANOM_RUNMEAN_ABS_HIGH} : ${CVAR_ANOM_RUNMEAN} ${MI_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_index_composite.py $(word 1,$^) ${COMP_VAR} $(word 2,$^) mi 90pct $@ --region sh --absolute

COMP_MI_CVAR_ANOM_RUNMEAN_ABS_HIGH_PLOT=${COMP_DIR}/mi-composite_${COMP_VAR}abs90pct_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-sh.png
${COMP_MI_CVAR_ANOM_RUNMEAN_ABS_HIGH_PLOT} : ${COMP_MI_CVAR_ANOM_RUNMEAN_ABS_HIGH}
	bash ${VIS_SCRIPT_DIR}/plot_index_composite.sh $< mi 90pctabs $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# ASL composite, upper threshold of PWI
 
# bash calc_asl_composite.sh
