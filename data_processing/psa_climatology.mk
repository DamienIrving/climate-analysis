# psa_climatology.mk
#
# To execute:
#   make -n -f psa_climatology.mk  (-n is a dry run)
#   (must be run from the directory that the relevant matlab scripts are in)

## Define marcos ##

include config.mk

NPLAT=$(word 2, ${NP})
NPLON=$(word 3, ${NP})
NP_LABEL=np${NPLAT}N${NPLON}E
GRID_LABEL=y$(word 3,${GRID})x$(word 6,${GRID})
CLIP_LABEL=${CLIP_METHOD}${CLIP_THRESH}


## Core PSA climatology process ##

# Phony target
all : ${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.csv

# Step 1: Calculate the rotated meridional wind
## (5 years at a time!!!)
${RWID_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}-${NP_LABEL}.nc : ${DATA_DIR}/ua_Merra_250hPa_daily_native.nc ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	${CDAT} calc_vwind_rotation.py $< ua $(word 2,$^) va $@ ${NP} ${GRID}
	
# Step 2: Calculate the rotated meridional wind anomaly
${RWID_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}-${NP_LABEL}.nc
	cdo ydaysub $< -ydayavg $< $@

# Step 3: Extract the wave envelope
## (5 years at a time!!!)
## (look into how the longitude search bit works here - it's not captured in the file names)
${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc : ${RWID_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc
	${CDAT} calc_envelope.py $< vrot $@ ${SEARCH_LON}

# Step 4: Calculate the hovmoller diagram
${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.nc : ${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}.nc
	${CDAT} calc_hovmoller.py $< env ${CLIP_METHOD} ${CLIP_THRESH} $@ ${LAT_SEARCH} ${LON_SEARCH} 

# Step 5: Implement the ROIM method
${RWID_DIR}/psa-dates_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov-env-w${WAVENUMS}-vrot_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.csv : ${RWID_DIR}/env-w${WAVENUMS}-vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-hov_${LON_LABEL}_${LAT_LABEL}_${CLIP_LABEL}.nc
	matlab -nodesktop -nojvm -nosplash -r "run_roim('$<', '$@', ${ROIM_START}, ${ROIM_TRES}, ${ROIM_ZRES})"



## Optional extras ##
