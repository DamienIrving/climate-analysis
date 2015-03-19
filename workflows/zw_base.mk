# zw_base.mk
#
# Description: Basic workflow that underpins all other zonal wave (zw) workflows 
#
# To execute:
#   make -n -B -f zw_base.mk  (-n is a dry run) (-B is a force make)

# Pre-processing:
#   The regirdding (if required) needs to be done beforehand 
#   (probably using cdo remapcon2,r360x181 in.nc out.nc)
#   So does the zonal anomaly


# Define marcos
include zw_config.mk

all : ${TARGET}


# Temporal averaging of core data

## Meridional wind

V_ORIG=${DATA_DIR}/va_${DATASET}_${LEVEL}_daily_native.nc
V_RUNMEAN=${DATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.nc
${V_RUNMEAN} : ${V_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ va

## Zonal wind

U_ORIG=${DATA_DIR}/ua_${DATASET}_${LEVEL}_daily_native.nc
U_RUNMEAN=${DATA_DIR}/ua_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.nc
${U_RUNMEAN} : ${U_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ ua

## Geopotential height zonal anomaly

ZG_ORIG=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native.nc
ZG_ZONAL_ANOM=${DATA_DIR}/zg_${DATASET}_500hPa_daily_native-zonal-anom.nc
${ZG_ZONAL_ANOM} : ${ZG_ORIG}       
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< zg $@ ${CDO_FIX_SCRIPT} ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

ZG_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZG_ZONAL_ANOM_RUNMEAN} : ${ZG_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ zg

## Sea surface temperature

TOS_ORIG=${DATA_DIR}/tos_${DATASET}_surface_daily_native-tropicalpacific.nc
TOS_RUNMEAN=${DATA_DIR}/tos_${DATASET}_surface_${TSCALE_LABEL}_native-tropicalpacific.nc
${TOS_RUNMEAN} : ${TOS_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ tos

# Mean sea level pressure

PSL_ORIG=${DATA_DIR}/psl_${DATASET}_surface_daily_native-shextropics30.nc
PSL_RUNMEAN=${DATA_DIR}/psl_${DATASET}_surface_${TSCALE_LABEL}_native-shextropics30.nc
${PSL_RUNMEAN} : ${PSL_ORIG}
	cdo ${TSCALE} $< $@
	bash ${CDO_FIX_SCRIPT} $@ psl


# Common indices

## Phase and amplitude of each Fourier component

FOURIER_INFO=${ZW_DIR}/fourier_zw_${COE_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.nc 
${FOURIER_INFO} : ${V_RUNMEAN}
	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< va $@ ${CDO_FIX_SCRIPT} ${WAVE_MIN} ${WAVE_MAX} coefficients ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

## ZW3 index 

ZW3_INDEX=${ZW_DIR}/zw3index_${DATASET}_500hPa_${TSCALE_LABEL}_native-zonal-anom.nc 
${ZW3_INDEX} : ${ZG_ZONAL_ANOM_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py ZW3 $< zg $@

## Nino 3.4

NINO34_INDEX=${INDEX_DIR}/nino34_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${NINO34_INDEX} : ${TOS_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py NINO34 $< tos $@

DATES_ELNINO=${INDEX_DIR}/dates_nino34elnino_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_ELNINO} : ${NINO34_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< nino34 $@ --metric_threshold 0.5 --threshold_direction greater

DATES_LANINA=${INDEX_DIR}/dates_nino34lanina_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_LANINA} : ${NINO34_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< nino34 $@ --metric_threshold -0.5 --threshold_direction less

## Southern Annular Mode

SAM_INDEX=${INDEX_DIR}/sam_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${SAM_INDEX} : ${PSL_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py SAM $< psl $@

DATES_SAM_POS=${INDEX_DIR}/dates_samgt75pct_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_SAM_POS} : ${SAM_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< sam $@ --metric_threshold 75pct --threshold_direction greater

DATES_SAM_NEG=${INDEX_DIR}/dates_samlt25pct_${DATASET}_surface_${TSCALE_LABEL}_native.txt
${DATES_SAM_NEG} : ${SAM_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< sam $@ --metric_threshold 25pct --threshold_direction less

## Amundsen Sea Low

ASL_INDEX=${INDEX_DIR}/asl_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${ASL_INDEX} : ${PSL_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py ASL $< psl $@

## Meridional index (average amplitude of the v wind)

MI_INDEX=${INDEX_DIR}/mi_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.nc 
${MI_INDEX} : ${V_RUNMEAN}
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py mi $< va $@

DATES_MI_HIGH=${INDEX_DIR}/dates_mi-${METRIC_HIGH_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.txt
${DATES_MI_HIGH} : ${MI_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< MI $@ --metric_threshold ${METRIC_HIGH_THRESH} --threshold_direction greater

DATES_MI_LOW=${INDEX_DIR}/dates_mi-${METRIC_LOW_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.txt
${DATES_MI_LOW} : ${MI_INDEX}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_date_list.py $< MI $@ --metric_threshold ${METRIC_LOW_THRESH} --threshold_direction less

