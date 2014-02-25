# psa_climatology.mk
#
# To execute:
#   make -n -f psa_climatology.mk  (-n is a dry run)
#   (must be run from the directory that the relevant matlab scripts are in)

## Define marcos ##

include config.mk

NPLAT=$(word 2, ${NP})
NPLON=$(word 3, ${NP})
NP_LABEL=np${NPLAT}-${NPLON}
GRID_LABEL=y$(word 3,${GRID})x$(word 6,${GRID})
CLIP_LABEL=${GRID_LABEL}_${NP_LABEL}
LON_LABEL=lon$(word 2,${LON_SEARCH})-$(word 3,${LON_SEARCH})
LAT_LABEL=lat$(word 2,${LAT_SEARCH})-$(word 3,${LAT_SEARCH})

## Core PSA climatology process ##

# Phony target
all : ${PDATA_DIR}/hov-vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}_${CLIP_LABEL}_${LON_LABEL}_${LAT_LABEL}.csv 

# Step 1: Calculate the rotated meridional wind
## (5 years at a time!!!)
${PDATA_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}_${NP_LABEL}.nc : ${DATA_DIR}/ua_Merra_250hPa_daily_native.nc ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	${CDAT} calc_vwind_rotation.py $< ua $(word 2,$^) va $@ ${NP} ${GRID}
	
# Step 2: Calculate the rotated meridional wind anomaly
${PDATA_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc : ${PDATA_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}_${NP_LABEL}.nc
	cdo ydaysub $< -ydayavg $< $@

# Step 3: Extract the wave envelope
## (5 years at a time!!!)
## (look into this SEARCH option and why it isn't included in output file name)
${PDATA_DIR}/vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc : ${PDATA_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc
	${CDAT} calc_envelope.py $< vrot $@ ${SEARCH_LON}

# Step 4: Calculate the hovmoller diagram
${PDATA_DIR}/hov-vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}_${CLIP_LABEL}_${LON_LABEL}_${LAT_LABEL}.nc : ${PDATA_DIR}/vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc
	${CDAT} calc_hovmoller.py $< env ${CLIP_METHOD} ${CLIP_THRESH} $@ ${LAT_SEARCH} ${LON_SEARCH} 

# Step 5: Implement the ROIM method
${PDATA_DIR}/hov-vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}_${CLIP_LABEL}_${LON_LABEL}_${LAT_LABEL}.csv : ${PDATA_DIR}/hov-vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}_${CLIP_LABEL}_${LON_LABEL}_${LAT_LABEL}.nc
	matlab -nodesktop -nojvm -nosplash -r "run_roim('$<', '$@', ${ROIM_START}, ${ROIM_TRES}, ${ROIM_ZRES})"



## Optional extras ##
