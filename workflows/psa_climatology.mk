# psa_climatology.mk
#
# To execute:
#   make -n -f psa_climatology.mk  (-n is a dry run)

## Define marcos ##

include psa_climatology_config.mk


### Core PSA climatology process ###

## Phony target
all : ${TARGET}


# Old ZW process
#
## Wave envelope & PWI
#
## Step 1: Apply temporal averaging to the meridional wind data
#V_ORIG=${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_daily_${GRID}.nc
#V_RUNMEAN=${DATA_DIR}/${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
#${V_RUNMEAN} : ${V_ORIG}
#	cdo ${TSCALE} $< $@
#	bash ${CDO_FIX_SCRIPT} $@ ${VAR}
#
### Step 2: Extract the wave envelope (for the entire globe)
#ENV_3D=${ZW_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc
#${ENV_3D} : ${V_RUNMEAN}
#	bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh $< ${VAR} $@ ${CDO_FIX_SCRIPT} ${WAVE_MIN} ${WAVE_MAX} hilbert ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}
#
### Step 3: Collapse the meridional dimension
#ENV_2D=${ZW_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
#${ENV_2D} : ${ENV_3D}
#	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
#	bash ${CDO_FIX_SCRIPT} $@ env${VAR}
#
### Step 4: Calculate the PWI and other wave statistics (mean & max, extent/coverage, etc)
#WAVE_STATS=${ZW_DIR}/wavestats_zw_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc 
#${WAVE_STATS} : ${ENV_2D}
#	${PYTHON} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< env${VAR} $@ --threshold ${EXTENT_THRESH}
#
### Step 5: Generate list of dates exceeding some PWI threshold (for later use in composite creation)
#DATE_LIST=${COMP_DIR}/dates_zw_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.txt 
#${DATE_LIST}: ${WAVE_STATS}
#	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --date_list $@ --metric_threshold ${METRIC_HIGH_THRESH}
#
## Common table/database
#
#TABLE=${ZW_DIR}/table_zw_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv 
#${TABLE} : ${WAVE_STATS} ${ZW3_INDEX} ${FOURIER_INFO}
#	${PYTHON} ${DATA_SCRIPT_DIR}/create_zw_table.py $(word 1,$^) $(word 2,$^) $(word 3,$^) $@




## Step 1: Calculate the rotated meridional wind
${RWID_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}-${NP_LABEL}.nc : ${DATA_DIR}/ua_Merra_250hPa_daily_native.nc ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	${VROT_METHOD} $< ua $(word 2,$^) va $@ ${NP} ${GRID}
	
## Step 2: Calculate the rotated meridional wind anomaly
${RWID_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}-${NP_LABEL}.nc
	cdo ydaysub $< -ydayavg $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 3: Apply temporal averaging to the rotated meridional wind anomaly data
ifneq (${TSCALE_LABEL},daily)
	${RWID_DIR}/vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc
		cdo ${TSCALE} $< $@
		ncatted -O -a axis,time,c,c,T $@
endif

## Step 4: Extract the wave envelope
${RWID_DIR}/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc
	${ENV_METHOD} $< vrot $@ ${WAVE_SEARCH} ${LON_SEARCH}

## Step 5: Calculate the hovmoller diagram
${RWID_DIR}/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}.nc : ${RWID_DIR}/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}.nc
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 6: Calculate the wave statistics
${RWID_DIR}/psa-stats_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}.csv : ${RWID_DIR}/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< env ${AMP_MIN} $@ 

## Step 6: Generate list of dates for use in composite creation
${RWID_DIR}/psa-dates_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt : ${RWID_DIR}/psa-stats_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --date_list $@

## Step 6a: Plot the duration histogram
${RWID_DIR}/figures/psa-duration-historgram_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}-eventextent${EVENT_EXTENT}-duration${DURATION_MIN}-${DURATION_MAX}.png : ${RWID_DIR}/psa-stats_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --event_extent ${EVENT_EXTENT} --duration_filter ${DURATION_MIN} ${DURATION_MAX} --duration_histogram $@

## Step 6b: Plot the monthly totals histogram
${RWID_DIR}/figures/psa-monthly-totals-historgram_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}-eventextent${EVENT_EXTENT}-duration${DURATION_MIN}-${DURATION_MAX}.png : ${RWID_DIR}/psa-stats_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --event_extent ${EVENT_EXTENT} --duration_filter ${DURATION_MIN} ${DURATION_MAX} --monthly_totals_histogram $@

## Step 6c: Plot the seasonal values line graph
${RWID_DIR}/figures/psa-seasonal-values-line_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}-eventextent${EVENT_EXTENT}-duration${DURATION_MIN}-${DURATION_MAX}.png : ${RWID_DIR}/psa-stats_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --event_extent ${EVENT_EXTENT} --duration_filter ${DURATION_MIN} ${DURATION_MAX} --annual --seasonal_values_line $@

## Step 7: Plot the envelope
${RWID_DIR}/figures/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}_${PLOT_END}.png : ${RWID_DIR}/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}.nc ${RWID_DIR}/psa-stats_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-vrot-ampmin${AMP_MIN}.csv ${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_native.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_envelope.py $< env ${TSCALE_LABEL} --time ${PLOT_START} ${PLOT_END} none --rotation ${NPLAT} ${NPLON} 0.0 0.0 --extent $(word 2,$^) ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --contour $(word 3,$^) sf --region world-psa --projection cyl --search_region ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} ${LON_SEARCH_MIN} ${LON_SEARCH_MAX} --ofile $@ 

## Step 7a: Calculate the streamfunction anomaly data
ifneq (${TSCALE_LABEL},daily)
	${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}_native.nc : ${PDATA_DIR}/sf_Merra_250hPa_daily_native.nc
		cdo ${TSCALE} $< $@
endif

${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}_native.nc
	cdo ydaysub $< -ydayavg $< $@
	ncatted -O -a axis,time,c,c,T $@


### Step 8: Calculate the composite
## Prepare the original composite variable data
#${PDATA_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-1979-2012_native.nc : ${DATA_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily_native.nc
#	cdo ydaysub $< -ydayavg $< $@
#
## Calculate the actual composite
#${RWID_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-all-composite-mean_${GRID_LABEL}-${NP_LABEL}-hov-env-${WAVE_LABEL}-vrot-250hPa_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}_psa-dates-${FILTER_LABEL}.nc : #${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-${WAVE_LABEL}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}_${FILTER_LABEL}.txt #${PDATA_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-1979-2012_native.nc
#	${CDAT} ${DATA_SCRIPT_DIR}/calc_composite.py $(word 2,$^) ${COMPOSITE_VAR} $< $@ --time 1979-01-01 2012-12-31 ${COMPOSITE_SEASON}


## Optional extras ##

# plot_composite.py   --   plot a composite

## Unit testing ##

# /home/dbirving/testing/unittest_coordinate_rotation.py
# /home/dbirving/testing/unittest_vwind_rotation.py

## Visualising the process ##

# /home/dbirving/testing/plot_vwind_rotation.py
# /home/dbirving/testing/plot_coordinate_rotation.py   
