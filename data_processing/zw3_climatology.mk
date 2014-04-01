# zw3_climatology.mk
#
# To execute:
#   make -n -f zw3_climatology.mk  (-n is a dry run)
#   (must be run from the directory that the relevant matlab scripts are in)

### Define marcos ###

include zw3_climatology_config.mk


### Core zonal wave 3 climatology process ###

## Phony target
all : ${RWID_DIR}/figures/zw3-seasonal-values-histogram_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}.png

## Step 1: Regrid the meridional wind data
${PDATA_DIR}/va_Merra_250hPa_${TSCALE}_${GRID}.nc : ${DATA_DIR}/va_Merra_250hPa_${TSCALE}_native.nc
	cdo remapcon2,${GRID} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 2: Extract the wave envelope
${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}.nc : ${PDATA_DIR}/va_Merra_250hPa_${TSCALE}_${GRID}.nc
	${ENV_METHOD} $< va $@ ${WAVE_SEARCH}

## Step 3: Calculate the hovmoller diagram
${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}.nc : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}.nc
	cdo mermean -sellonlatbox,0,360,${LAT_SEARCH} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 4: Calculate the wave statistics
${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}.nc
	${CDAT} ${SCRIPT_DIR}/calc_wave_stats.py $< env ${AMP_MIN} $@ 

## Step 5: Generate list of dates for use in composite creation
${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}.txt : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} --date_list $@

## Step 5a: Plot the extent histogram
${RWID_DIR}/figures/zw3-extent-histogram_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}.png : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} --extent_histogram $@

## Step 5b: Plot the monthly totals histogram
${RWID_DIR}/figures/zw3-monthly-totals-histogram_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}.png : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} --monthly_totals_histogram $@

## Step 5c: Plot the monthly totals histogram
${RWID_DIR}/figures/zw3-seasonal-values-histogram_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}.png : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE}_${GRID}-hov-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} --seasonal_values_histogram $@ --annual



## Optional extras ##

# plot_envelope.py    --   plot the wave envelope with other variables overlayed
# plot_composite.py   --   plot a composite
