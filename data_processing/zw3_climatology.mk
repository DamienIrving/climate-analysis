# zw3_climatology.mk
#
# To execute:
#   make -n -B -f zw3_climatology.mk  (-n is a dry run) (-B is a force make)

# Pre-processing:
#   The regirdding (if required) needs to be done beforehand 
#   (probably using cdo remapcon2,r360x181 in.nc out.nc)


## Define marcos ##
include zw3_climatology_config.mk

## Phony target
all : ${TARGET}

### Calculate the wave envelope ###

## Step 1: Apply temporal averaging to the meridional wind data ##

${PDATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc : ${DATA_DIR}/va_${DATASET}_${LEVEL}_daily_${GRID}.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 2: Extract the wave envelope (for the entire globe) and collapse the meridional dimension ##

${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc : ${PDATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	${FOURIER_METHOD} $< va $@ ${ENV_SEARCH}

${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc : ${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 3: Normalise the wave envelope (for the entire globe) and collapse the meridional dimension ##

${ZW3_DIR}/nenv-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc : ${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	cdo -ydaydiv -ydaysub $< -ydayavg $< -ydaystd $< $@
	ncatted -O -a axis,time,c,c,T $@

${ZW3_DIR}/nenv-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc : ${ZW3_DIR}/nenv-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	ncatted -O -a axis,time,c,c,T $@


### Generate the table/database of interesting results ###
#    - Average meridional max of env and nenv, env and nenv extent/coverage <= calc_wave_stats.py
#    - Phase and amplitude of each Fourier component (for a selected latitude band or range)  <= calc_fourier_transform.py
#    - Raphael ZW3 index <= calc_index.py


## Step 1: Calculate the wave statistics (average env & nenv, extent/coverage of nenv) ##

${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va-stats-threshold${THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc : ${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< va $@ --threshold ${THRESH}

${ZW3_DIR}/nenv-${ENV_WAVE_LABEL}-va-stats-threshold${THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc : ${ZW3_DIR}/nenv-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< va $@ --threshold ${THRESH}

## Step 2: Calculate the phase and amplitude of each Fourier component ##

${ZW3_DIR}/fourier-${COE_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc : ${PDATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	${FOURIER_METHOD} $< va $@ ${COE_SEARCH}

## Step 3: Calculate the ZW3 index of Raphael (2004) ## 

${PDATA_DIR}/zg_${DATASET}_500hPa_daily-zonal-anom_native.nc : ${PDATA_DIR}/zg_${DATASET}_500hPa_daily_native.nc       
	${ZONAL_ANOM_METHOD} $< zg $@
	ncatted -O -a axis,time,c,c,T $@

${PDATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc : ${PDATA_DIR}/zg_${DATASET}_500hPa_daily-zonal-anom_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

${ZW3_DIR}/zw3-zg_${DATASET}_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc : ${PDATA_DIR}/zg_${DATASET}_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py ZW3 $< zg $@

# Step 4: Put it all in a common table/database

${ZW3_DIR}/zw3-${ENV_WAVE_LABEL}-va-stats-threshold${THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv : ${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va-stats-threshold${THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc ${ZW3_DIR}/nenv-${ENV_WAVE_LABEL}-va-stats-threshold${THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc ${ZW3_DIR}/zw3-zg_${DATASET}_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc ${ZW3_DIR}/fourier-${COE_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	${PYTHON} ${DATA_SCRIPT_DIR}/create_zw3_table.py $(word 1,$^) $(word 2,$^) $(word 3,$^) $(word 4,$^) $@
