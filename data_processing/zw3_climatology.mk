# zw3_climatology.mk
#
# To execute:
#   make -n -f zw3_climatology.mk  (-n is a dry run)
#   (must be run from the directory that the relevant matlab scripts are in)

### Define marcos ###

include zw3_climatology_config.mk


### Core zonal wave 3 climatology process ###

## Phony target
all : ${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE}_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}_${CLIP_LABEL}.txt

## Step 1: Regrid the meridional wind data
${PDATA_DIR}/va_Merra_250hPa_${TSCALE}_${GRID}.nc : ${DATA_DIR}/va_Merra_250hPa_${TSCALE}_native.nc
    cdo remapcon2,${GRID} $< $@
    ncatted -O -a axis,time,c,c,T $@

## Step 2: Extract the wave envelope
${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}.nc : ${PDATA_DIR}/va_Merra_250hPa_${TSCALE}_${GRID}.nc
    ${ENV_METHOD} $< va $@ ${WAVE_SEARCH}

## Step 3: Calculate the hovmoller diagram
${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}-hov_${LAT_LABEL}.nc : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}.nc
    cdo mermean -sellatlonbox,0,360,${LAT_SEARCH} $< $@

## Step 4: Calculate the extent
${RWID_DIR}/zw3-extent${EXTENT_THRESH}_Merra_250hPa_${TSCALE}_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}.csv : ${RWID_DIR}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE}_${GRID}-hov_${LAT_LABEL}.nc
    ${CDAT} ${SCRIPT_DIR}/calc_extent.py $< env ${EXTENT_THRESH} $@ 


####

## Step 5: Generate a list of PSA-active dates
# (requires pandas)
# (can also generate a duration histogram with roim_stat.py)
#${RWID_DIR}/zw3-dates_Merra_250hPa_${TSCALE}_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}.txt : #${RWID_DIR}/zw3-roim-stats_Merra_250hPa_${TSCALE}_${GRID}-hov-env-${WAVE_LABEL}-va_${LAT_LABEL}.csv
#	${PYTHON} ${ROIM_SCRIPT_DIR}/roim_stat.py $< --date_list startpoint_temporal endpoint_temporal $@



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
