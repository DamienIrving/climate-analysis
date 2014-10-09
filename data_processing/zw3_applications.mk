#EXTENT_MIN=300
#EXTENT_MAX=360
#
# Composite
#COMPOSITE_TIMESCALE=monthly
#COMPOSITE_PLACEHOLDER=JAN


## Define marcos ##
include zw3_climatology_config.mk

## Phony target
all : ${TARGET}

## Plot the envelope ##

# Step 1: Calculate the contour zonal anomaly
${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native-zonal-anom.nc : ${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native.nc       
	${ZONAL_ANOM_METHOD} $< ${CONTOUR_VAR} $@
	ncatted -O -a axis,time,c,c,T $@

# Step 2: Apply temporal averaging to the zonal contour data
${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc : ${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native-zonal-anom.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

# Step 3: Plot the envelope
${MAP_DIR}/env/${TSCALE_LABEL}/${VAR}/env-${ENV_WAVE_LABEL}-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}_${PLOT_END}.png : ${ZW3_DIR}/env_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc ${DATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_envelope.py $< ${VAR} ${TSTEP} --contour $(word 2,$^) ${CONTOUR_VAR} --timescale ${TSCALE_LABEL} --time ${PLOT_START} ${PLOT_END} none --projection spstere --stride ${STRIDE} --raphael --ofile $@


## Plot the Hilbert transform ##

# Step 1: Calculate the running mean

${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_daily_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

# Step 2: Plot the Hilbert transform

${INDEX_DIR}/hilbert/${TSCALE_LABEL}/hilbert_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${LAT_LABEL}_${PLOT_END}.png : ${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_hilbert.py $< ${VAR} ${TSTEP} $@ --timescale ${TSCALE_LABEL} --time ${PLOT_START} ${PLOT_END} none --latitude ${LAT_RANGE} --stride ${STRIDE}


## Plot the climatological stats ##

# Step 1: Plot the monthly totals histogram

${INDEX_DIR}/clim/montots_zw3_${METRIC}${METRIC_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png : ${ZW3_DIR}/table_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv 
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --monthly_totals_histogram $@ --metric_filter ${METRIC_THRESH}

# Step 2: Plot the seaonal values line graph

${INDEX_DIR}/clim/seasvals_zw3_${METRIC}${METRIC_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png : ${ZW3_DIR}/table_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv 
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --seasonal_values_line $@ --metric_filter ${METRIC_THRESH}

## Composites

## Step 1: Generate list of dates for use in composite creation
${COMP_DIR}/dates_zw3_${METRIC}${METRIC_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.txt : ${ZW3_DIR}/table_zw3_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --date_list $@ --metric_filter ${METRIC_THRESH}

## Step 2: Calculate the composite file

# Apply temporal averaging to composite variable
${DATA_DIR}/${COMP_VAR}_${DATASET}_surface_${TSCALE_LABEL}_${GRID}.nc : ${DATA_DIR}/${COMP_VAR}_${DATASET}_surface_daily_${GRID}.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

# Calculate composite
${COMP_DIR}/tas-composite_zw3_${METRIC}${METRIC_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.nc : ${DATA_DIR}/${COMP_VAR}_${DATASET}_surface_${TSCALE_LABEL}_${GRID}.nc  ${COMP_DIR}/dates_zw3_${METRIC}${METRIC_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.txt 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< tas $@ --date_file $(word 2,$^) 

###  ###
#
## Step 8: Calculate composites
# Envelope
#${RWID_DIR}/env-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${RWID_DIR}/env-${WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< env $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
# Zonal streamfunction anomaly
#${RWID_DIR}/sf-zonal-anom-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${DATA_DIR}/sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}-zonal-anom_native.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< sf $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
# Sea ice anomaly
#${DATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/sic_${DATASET}_surface_daily_native.nc
#	cdo ${TSCALE} $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${DATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${DATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}_native.nc
#	cdo ydaysub $< -ydayavg $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${RWID_DIR}/sic-anom-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${DATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< sic $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
# Surface temperature anomaly
#${DATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/tas_${DATASET}_surface_daily_native.nc
#	cdo ${TSCALE} $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${DATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${DATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}_native.nc
#	cdo ydaysub $< -ydayavg $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${RWID_DIR}/tas-anom-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${DATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< tas $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
## Optional extras ##
#
# plot_composite.py   --   plot a composite
