# psa_climatology.mk
#
# To execute:
#   make -n -f psa_climatology.mk  (-n is a dry run)
#   (must be run from the directory that the relevant matlab scripts are in)

## Define marcos ##

include psa_climatology_config.mk


### Core PSA climatology process ###

## Phony target
all : ${RWID_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-all-composite-mean_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot-250hPa_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}_psa-dates-${FILTER_LABEL}.nc

## Step 1: Calculate the rotated meridional wind
${RWID_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}-${NP_LABEL}.nc : ${DATA_DIR}/ua_Merra_250hPa_daily_native.nc ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	${VROT_METHOD} $< ua $(word 2,$^) va $@ ${NP} ${GRID}
	
## Step 2: Calculate the rotated meridional wind anomaly
${RWID_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}-${NP_LABEL}.nc
	cdo ydaysub $< -ydayavg $< $@

## Step 3: Extract the wave envelope
## (look into how the longitude search bit works here - it's not captured in the file names)
${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc
	${ENV_METHOD} $< vrot $@ ${LON_SEARCH}

## Step 4: Calculate the hovmoller diagram
${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.nc : ${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_hovmoller.py $< env ${CLIP_METHOD} ${CLIP_THRESH} $@ ${LAT_SEARCH} ${LON_SEARCH} 

## Step 5: Implement the ROIM method
${RWID_DIR}/psa-roim-stats_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.csv : ${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.nc
	matlab -nodesktop -nojvm -nosplash -r "run_roim('$<', '$@', ${ROIM_START}, ${ROIM_TRES}, ${ROIM_ZRES})"

## Step 6: Generate a list of PSA-active dates
# (requires pandas)
# (can also generate a duration histogram with roim_stat.py)
${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.txt : ${RWID_DIR}/psa-roim-stats_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.csv
	python ${ROIM_SCRIPT_DIR}/roim_stat.py $< --date_list startpoint_temporal endpoint_temporal $@

## Step 7: Filter the list of dates
${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}_${FILTER_LABEL}.txt : ${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.txt ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	${CDAT} ${DATA_SCRIPT_DIR}/filter_dates.py $< --filter ${FLITER_REGION} $(word 2,$^) va ${FILTER_THRESH} ${FILTER_DIRECTION} --outfile $@ 

## Step 8: Calculate the composite
# Prepare the original composite variable data
${PDATA_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-1979-2012_native.nc : ${DATA_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily_native.nc
	cdo ydaysub $< -ydayavg $< $@

# Calculate the actual composite
${RWID_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-all-composite-mean_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot-250hPa_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}_psa-dates-${FILTER_LABEL}.nc : ${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}_${FILTER_LABEL}.txt ${PDATA_DIR}/${COMPOSITE_VAR}_Merra_${COMPOSITE_LEVEL}_daily-anom-wrt-1979-2012_native.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_composite.py $(word 2,$^) ${COMPOSITE_VAR} $< $@ --time 1979-01-01 2012-12-31 ${COMPOSITE_SEASON}


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
