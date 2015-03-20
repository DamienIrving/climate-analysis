## Geopotential height zonal anomaly

ZG_ORIG=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native.nc
ZG_ZONAL_ANOM=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native-zonal-anom.nc
${ZG_ZONAL_ANOM} : ${ZG_ORIG}       
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< zg $@ ${CDO_FIX_SCRIPT} ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

ZG_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZG_ZONAL_ANOM_RUNMEAN} : ${ZG_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ zg

COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_HIGH=${COMP_DIR}/zg-composite_mi${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_HIGH} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_HIGH} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh

COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_LOW=${COMP_DIR}/zg-composite_mi${METRIC_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc 
${COMP_ZG_ZONAL_ANOM_RUNMEAN_MI_LOW} : ${ZG_ZONAL_ANOM_RUNMEAN} ${DATES_MI_LOW} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< zg $@ --date_file $(word 2,$^) --region sh
