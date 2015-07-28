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


V_ORIG=${DATA_DIR}/va_${DATASET}_${LEVEL}_daily_native.nc
U_ORIG=${DATA_DIR}/ua_${DATASET}_${LEVEL}_daily_native.nc

## Streamfunction

SF_ORIG=${DATA_DIR}/sf_${DATASET}_${LEVEL}_daily_native.nc
${SF_ORIG} : ${U_ORIG} ${V_ORIG}
	bash ${DATA_SCRIPT_DIR}/calc_wind_quantities.sh streamfunction $< ua $(word 2,$^) va $@ ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

SF_ANOM_RUNMEAN=${DATA_DIR}/sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native.nc
${SF_ANOM_RUNMEAN} : ${SF_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@



# Common indices

## Phase and amplitude of each Fourier component

FOURIER_INFO=${ZW_DIR}/fourier_zw_${COE_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.nc 
${FOURIER_INFO} : ${V_RUNMEAN}
	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< va $@ ${WAVE_MIN} ${WAVE_MAX} coefficients ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}


