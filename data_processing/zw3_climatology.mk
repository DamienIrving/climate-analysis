# zw3_climatology.mk
#
# To execute:
#   make -n -f zw3_climatology.mk  (-n is a dry run)
#   (must be run from the directory that the relevant matlab scripts are in)

### Define marcos ###

include zw3_climatology_config.mk


### Core zonal wave 3 climatology process ###

## Phony target
all : ${RWID_DIR}/zw3-dates_Merra_250hPa_daily-anom-wrt-all_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}_${CLIP_LABEL}.txt
	
## Step 1: Calculate the daily meridional wind anomaly
${PDATA_DIR}/va_Merra_250hPa_daily-anom-wrt-all_native.nc : ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	cdo ydaysub $< -ydayavg $< $@

## Step 2: Regrid 
${PDATA_DIR}/va_Merra_250hPa_daily-anom-wrt-all_{GRID}.nc : ${PDATA_DIR}/va_Merra_250hPa_daily-anom-wrt-all_native.nc
	cdo remapcon2,${GRID} $< $@

## Step 3: Extract the wave envelope
${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_daily-anom-wrt-all_${GRID}.nc : ${PDATA_DIR}/va_Merra_250hPa_daily-anom-wrt-all_{GRID}.nc
	${ENV_METHOD} $< va $@ ${WAVE_SEARCH}

## Step 4: Calculate the hovmoller diagram
${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_daily-anom-wrt-all_${GRID}-hov_${LAT_LABEL}_${CLIP_LABEL}.nc : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_daily-anom-wrt-all_${GRID}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_hovmoller.py $< env ${CLIP_METHOD} ${CLIP_THRESH} $@ ${LAT_SEARCH}

## Step 5: Implement the ROIM method
${RWID_DIR}/zw3-roim-stats_Merra_250hPa_daily-anom-wrt-all_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}_${CLIP_LABEL}.csv : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_daily-anom-wrt-all_${GRID}-hov_${LAT_LABEL}_${CLIP_LABEL}.nc
	matlab -nodesktop -nojvm -nosplash -r "run_roim('$<', '$@', ${ROIM_START}, ${ROIM_TRES}, ${ROIM_ZRES})"

## Step 6: Generate a list of PSA-active dates
# (requires pandas)
# (can also generate a duration histogram with roim_stat.py)
${RWID_DIR}/zw3-dates_Merra_250hPa_daily-anom-wrt-all_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}_${CLIP_LABEL}.txt : ${RWID_DIR}/zw3-roim-stats_Merra_250hPa_daily-anom-wrt-all_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}_${CLIP_LABEL}.csv
	python ${ROIM_SCRIPT_DIR}/roim_stat.py $< --date_list startpoint_temporal endpoint_temporal $@



## Optional extras ##

# plot_envelope.py    --   plot the wave envelope with other variables overlayed
# roim_stat.py        --   plot the event duration histogram
# parse_dates.py      --   calculate some statistics from a list of dates (monthly totals, seasonal totals, etc)
# plot_composite.py   --   plot a composite

## Unit testing ##

# /home/dbirving/testing/unittest_coordinate_rotation.py
# /home/dbirving/testing/unittest_vwind_rotation.py

## Visualising the process ##

# /home/dbirving/testing/plot_vwind_rotation.py
# /home/dbirving/testing/plot_coordinate_rotation.py   
