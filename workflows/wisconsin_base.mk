# wisconsin_base.mk
#
# Description: Workflow for generating data for University of Wisconsin
#   study into meridional moisture transport           
#
# To execute:
#   1. copy name of target file from wisconsin_base.mk 
#   2. paste it into wisconsin_config.mk as the target variable  
#   3. $ make -n -B -f wisconsin_base.mk  (-n is a dry run) (-B is a force make)
#
# Data history:
#   http://apps.ecmwf.int/datasets/data/interim-full-moda/levtype=pl/
#     - ERA Interim, Monthly Means of Daily Means
#     - Pressure levels
#     - 500hPa, v wind and geopotential (Grid: 0.75x0.75)
#

# Define marcos

include wisconsin_config.mk
all : ${TARGET}

# Filenames

V_RAW=${DATA_DIR}/v_eraint_500hPa_monthly_native_raw.nc
VA_DATA=${DATA_DIR}/va_eraint_500hPa_monthly_native.nc

Z_RAW=${DATA_DIR}/z_eraint_500hPa_monthly_native_raw.nc
ZG_DATA=${DATA_DIR}/zg_eraint_500hPa_monthly_native.nc
ZG_ZONAL_ANOM=${DATA_DIR}/zg_eraint_500hPa_monthly_native-zonal-anom.nc

ENV_DATA=${WISCONSIN_DIR}/envva_w1-9_eraint_500hPa_monthly_native.nc
PWI_DATA=${WISCONSIN_DIR}/pwi_va_eraint_500hPa_monthly_native.nc
ZW3_DATA=${WISCONSIN_DIR}/zw3_eraint_500hPa_monthly_native.nc
MI_DATA=${WISCONSIN_DIR}/mi_va_eraint_500hPa_monthly_native.nc

# Pre-processing

${VA_DATA} : ${V_RAW}
	cdo invertlat -sellonlatbox,0,359.9,-90,90 $< $@
	ncrename -O -v v,va $@
	ncatted -O -a calendar,global,d,, $@
        # (for Iris compatability)
	ncatted -O -a standard_name,va,o,c,"northward_wind" $@
	ncatted -O -a long_name,va,o,c,"northward_wind" $@
	ncatted -O -a level,va,o,c,"500hPa" $@

${ZG_DATA} : ${Z_RAW}
	cdo invertlat -sellonlatbox,0,359.9,-90,90 -divc,9.80665 $< $@   
        # (divides by standard gravity to go from geopotential to geopotential height)
	ncrename -O -v z,zg $@
	ncatted -O -a calendar,global,d,, $@
        # (for Iris compatability)
	ncatted -O -a units,zg,o,c,"m" $@
	ncatted -O -a standard_name,zg,o,c,"geopotential_height" $@
	ncatted -O -a long_name,zg,o,c,"geopotential_height" $@
	ncatted -O -a level,zg,o,c,"500hPa" $@

# PWI

${ENV_DATA} : ${VA_DATA}
	mkdir -p ${WISCONSIN_DIR}
	python ${SCRIPT_DIR}/calc_fourier_transform.py $< va $@ 1 9 envelope 

${PWI_DATA} : ${ENV_DATA}
	python ${SCRIPT_DIR}/calc_climate_index.py PWI $< envva $@

# ZW3

${ZG_ZONAL_ANOM} : ${ZG_DATA}
	python ${SCRIPT_DIR}/calc_zonal_anomaly.py $< zg $@

${ZW3_DATA} : ${ZG_ZONAL_ANOM}
	mkdir -p ${WISCONSIN_DIR}
	python ${SCRIPT_DIR}/calc_climate_index.py ZW3 $< zg $@

# MI (meridional index)

${MI_DATA} : ${VA_DATA}
	mkdir -p ${WISCONSIN_DIR}
	python ${SCRIPT_DIR}/calc_climate_index.py MI $< va $@

