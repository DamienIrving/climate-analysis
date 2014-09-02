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
${PDATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily-zonal-anom_native.nc : ${PDATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily_native.nc       
	${ZONAL_ANOM_METHOD} $< ${CONTOUR_VAR} $@
	ncatted -O -a axis,time,c,c,T $@

# Step 2: Apply temporal averaging to the zonal contour data
${PDATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-zonal_anom_native.nc : ${PDATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_daily-zonal-anom_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

# Step 3: Plot the envelope
${FIG_DIR}/env/${TSCALE_LABEL}/env-${ENV_WAVE_LABEL}-va-${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}_${PLOT_END}.png : ${ZW3_DIR}/env-${ENV_WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc ${PDATA_DIR}/${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-zonal_anom_native.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_envelope.py $< va ${TSTEP} --contour $(word 2,$^) ${CONTOUR_VAR} --timescale ${TSCALE_LABEL} --time ${PLOT_START} ${PLOT_END} none --projection spstere --stride ${STRIDE} --raphael --ofile $@



## Use the database to do interesting things ### 
#    - Date lists for composites   <= parse_wave_stats.py 
#    - Plots of key stats    <= parse_wave_stats.py
#
## Step 6: Generate list of dates for use in composite creation
#${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt : #${RWID_DIR}/zw3-stats_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
#	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --date_list $@
#
## Step 6a: Plot the extent histogram
#${RWID_DIR}/figures/zw3-extent-histogram_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.png : #${RWID_DIR}/zw3-stats_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
#	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --extent_histogram $@
#
## Step 6b: Plot the monthly totals histogram
#${RWID_DIR}/figures/zw3-monthly-totals-histogram_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.png : #${RWID_DIR}/zw3-stats_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
#	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --monthly_totals_histogram $@
#
## Step 6c: Plot the seasonal values line graph
#${RWID_DIR}/figures/zw3-seasonal-values-line_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.png : #${RWID_DIR}/zw3-stats_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
#	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --seasonal_values_line $@ --annual
#
###  ###
#
## Step 8: Calculate composites
# Envelope
#${RWID_DIR}/env-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${RWID_DIR}/env-${WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< env $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
# Zonal streamfunction anomaly
#${RWID_DIR}/sf-zonal-anom-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${PDATA_DIR}/sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}-zonal-anom_native.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< sf $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
# Sea ice anomaly
#${PDATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/sic_${DATASET}_surface_daily_native.nc
#	cdo ${TSCALE} $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${PDATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${PDATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}_native.nc
#	cdo ydaysub $< -ydayavg $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${RWID_DIR}/sic-anom-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${PDATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< sic $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
# Surface temperature anomaly
#${PDATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/tas_${DATASET}_surface_daily_native.nc
#	cdo ${TSCALE} $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${PDATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${PDATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}_native.nc
#	cdo ydaysub $< -ydayavg $< $@
#	ncatted -O -a axis,time,c,c,T $@
#
#${RWID_DIR}/tas-anom-zw3-composite-mean_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : #${PDATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc #${RWID_DIR}/zw3-dates_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
#	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< tas $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}
#
## Optional extras ##
#
# plot_composite.py   --   plot a composite
