# zw3_climatology.mk
#
# To execute:
#   make -n -B -f zw3_climatology.mk  (-n is a dry run) (-B is a force make)

# Fix:
#   At the moment the data processing (e.g. for the sf and calculation of the
#   running mean) doesn't do all the way back to the original files.


## Define marcos ##
include zw3_climatology_config.mk

## Phony target
all : ${TARGET}

### Calculate the wave envelope ###

## Step 1: Apply temporal averaging to the meridional wind data ##

${PDATA_DIR}/va_Merra_250hPa_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 2: Regrid the meridional wind data ##

${PDATA_DIR}/va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc : ${PDATA_DIR}/va_Merra_250hPa_${TSCALE_LABEL}_native.nc
	cdo remapcon2,${GRID} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 3: Extract the wave envelope (for the entire globe) ##

${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc : ${PDATA_DIR}/va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc
	${ENV_METHOD} $< va $@ ${WAVE_SEARCH}

## Step 4: Normalise the wave envelope (for the entire globe) ##

${RWID_DIR}/nenv-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc
	cdo -ydaydiv -ydaysub $< -ydayavg $< -ydaystd $< $@
	ncatted -O -a axis,time,c,c,T $@
	ncrename -O -v env,nenv $@
    
## Step 5: Calculate the hovmoller diagram ##

${RWID_DIR}/nenv-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc : ${RWID_DIR}/nenv-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	ncatted -O -a axis,time,c,c,T $@


### Generate the database of interesting results ###
#    - Average meridional max nenv, nenv extent/coverage <= calc_wave_stats.py
#    - Phase and amplitude of each Fourier component (for a selected latitude band or range)  <= calc_fft_stats.py (or just calc_fourier_transform.py itself)
#    - Raphael ZW3 index <= calc_index.py


## Step 1: Calculate the wave statistics (average nenv, extent/coverage of nenv) ##

${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv : ${RWID_DIR}/nenv-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< nenv ${AMP_MIN} $@ 




## Step 3: Calculate the ZW3 index of Raphael (2004) ## 

${PDATA_DIR}/zg_Merra_500hPa_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/zg_Merra_500hPa_daily_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

${PDATA_DIR}/zg_Merra_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc : ${PDATA_DIR}/zg_Merra_500hPa_${TSCALE_LABEL}_native.nc       
	${ZONAL_ANOM_METHOD} $< zg $@
	ncatted -O -a axis,time,c,c,T $@

${RWID_DIR}/zw3-zg_Merra_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc : ${PDATA_DIR}/zg_Merra_500hPa_${TSCALE_LABEL}-zonal-anom_native.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_climate_index.py ZW3 $< va $@


### Use the database to do interesting things ### 
#    - Date lists for composites   <= parse_wave_stats.py 
#    - Plots of key stats    <= parse_wave_stats.py

## Step 6: Generate list of dates for use in composite creation
${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --date_list $@

## Step 6a: Plot the extent histogram
${RWID_DIR}/figures/zw3-extent-histogram_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.png : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --extent_histogram $@

## Step 6b: Plot the monthly totals histogram
${RWID_DIR}/figures/zw3-monthly-totals-histogram_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.png : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --monthly_totals_histogram $@

## Step 6c: Plot the seasonal values line graph
${RWID_DIR}/figures/zw3-seasonal-values-line_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.png : ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< --extent_filter ${EXTENT_MIN} ${EXTENT_MAX} --seasonal_values_line $@ --annual


###   ###


## Step 7: Plot the envelope
${RWID_DIR}/figures/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}_${PLOT_END}.png : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc ${RWID_DIR}/zw3-stats_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}.csv ${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}-zonal-anom_native.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_envelope.py $< env ${TSCALE_LABEL} --extent $(word 2,$^) ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --contour $(word 3,$^) sf --time ${PLOT_START} ${PLOT_END} none --projection spstere --ofile $@

## Step 7a: Calculate the streamfunction zonal anomaly
${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}-zonal-anom_native.nc : ${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}_native.nc       
	${ZONAL_ANOM_METHOD} $< sf $@
	ncatted -O -a axis,time,c,c,T $@

## Step 8: Calculate composites
# Envelope
${RWID_DIR}/env-zw3-composite-mean_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}.nc ${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< env $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}

# Zonal streamfunction anomaly
${RWID_DIR}/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : ${PDATA_DIR}/sf_Merra_250hPa_${TSCALE_LABEL}-zonal-anom_native.nc ${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< sf $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}

# Sea ice anomaly
${PDATA_DIR}/sic_Merra_surface_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/sic_Merra_surface_daily_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

${PDATA_DIR}/sic_Merra_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${PDATA_DIR}/sic_Merra_surface_${TSCALE_LABEL}_native.nc
	cdo ydaysub $< -ydayavg $< $@
	ncatted -O -a axis,time,c,c,T $@

${RWID_DIR}/sic-anom-zw3-composite-mean_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : ${PDATA_DIR}/sic_Merra_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc ${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< sic $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}

# Surface temperature anomaly
${PDATA_DIR}/tas_Merra_surface_${TSCALE_LABEL}_native.nc : ${DATA_DIR}/tas_Merra_surface_daily_native.nc
	cdo ${TSCALE} $< $@
	ncatted -O -a axis,time,c,c,T $@

${PDATA_DIR}/tas_Merra_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc : ${PDATA_DIR}/tas_Merra_surface_${TSCALE_LABEL}_native.nc
	cdo ydaysub $< -ydayavg $< $@
	ncatted -O -a axis,time,c,c,T $@

${RWID_DIR}/tas-anom-zw3-composite-mean_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}_${COMPOSITE_PLACEHOLDER}.nc : ${PDATA_DIR}/tas_Merra_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc ${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}_env-${WAVE_LABEL}-va-ampmin${AMP_MIN}-extentmin${EXTENT_MIN}-${EXTENT_MAX}.txt 
	bash ${DATA_SCRIPT_DIR}/calc_composite.sh $< tas $(word 2,$^) $@ ${COMPOSITE_TIMESCALE}

## Optional extras ##

# plot_composite.py   --   plot a composite
