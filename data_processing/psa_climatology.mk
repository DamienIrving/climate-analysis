# psa_climatology.mk

include config.mk

NPLAT=$(word 2, ${NP})
NPLON=$(word 3, ${NP})
NP_LABEL=np${NPLAT}-${NPLON}
GRID_LABEL=y$(word 3,${GRID})x$(word 6,${GRID})


# Step 1: Calculate the rotated meridional wind
## (Does this need to be processed 5 years at a time???)
${PDATA_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}_${NP_LABEL}.nc : ${DATA_DIR}/ua_Merra_250hPa_daily_native.nc ${DATA_DIR}/va_Merra_250hPa_daily_native.nc
	${CDAT} calc_vwind_rotation.py $< ua $(word 2,$^) va $@ ${NP} ${GRID}
	
# Step 2: Calculate the rotated meridional wind anomaly
${PDATA_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc : ${PDATA_DIR}/vrot_Merra_250hPa_daily_${GRID_LABEL}_${NP_LABEL}.nc
	cdo ydaysub $< -ydayavg $< $@

# Step 3: Extract the wave envelope
## (look into this SEARCH option and why it isn't included in output file name)
${PDATA_DIR}/vrot-env-w${WAVENUMS}_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc : ${PDATA_DIR}/vrot_Merra_250hPa_daily-anom-wrt-all_${GRID_LABEL}_${NP_LABEL}.nc
	${CDAT} calc_envelope.py $< vrot $@ ${SEARCH}

# Step 4: Calculate the hovmoller diagram
 