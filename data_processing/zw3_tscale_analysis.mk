# zw3_tscale_analysis.mk
#
# There are two parts to the timescale analysis. An objective part (using plot_freq_spectrum.py to calculate the average 
# spectra over the entire time period) and a visual part (which is detailed here). 
#
# The overall aim of the visual part is to reproduce the images I showed in a previous meeting with Ian, for 3-years of 
# individual days for a running mean of 1, 5, 30, 90, 180 days. Those images had three panels:
#  - A map of the wave envelope with zonal streamfunction anomaly over the top (plot_envelope.py)
#  - One map of the power spectrum and the other of each component of the Fourier Transform (plot_hilbert.py)
#
# To execute:
#   make -n -B -f zw3_tscale_analysis.mk  (-n is a dry run) (-B is a force make)
#
# Notes:
#  - To thin data use "ncks -d time,0,,1 infile.nc ofile.nc" (this one starts at 0 index and picks every timestep)  
#

### Define marcos ###

include zw3_tscale_analysis_config.mk

## Phony target
all : ${TARGET}

### Wave envelope map (plot_envelope.py) ###

## Step 1a: Apply temporal averaging to the meridional wind data (for a limited time period)
${PDATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}_${GRID}.nc : ${DATA_DIR}/va_${DATASET}_${LEVEL}_daily_${GRID}.nc
	cdo ${TSCALE} -${PERIOD} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 1b: Extract the wave envelope
${RWID_DIR}/env-${WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}_${GRID}.nc : ${PDATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}_${GRID}.nc
	${CDAT} ${DATA_SCRIPT_DIR}/calc_fourier_transform.py $< va $@ ${WAVE_SEARCH}

## Step 2a: Calculate the contour zonal anomaly
${PDATA_DIR}/${CONTOUR-VAR}_${DATASET}_${LEVEL}_daily-zonal-anom_native.nc : ${PDATA_DIR}/${CONTOUR-VAR}_${DATASET}_${LEVEL}_daily_native.nc       
	${ZONAL_ANOM_METHOD} $< sf $@
	ncatted -O -a axis,time,c,c,T $@

## Step 2b: Apply temporal averaging to the zonal contour data (for a limited time period)
${PDATA_DIR}/${CONTOUR-VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}-zonal_anom_native.nc : ${PDATA_DIR}/${CONTOUR-VAR}_${DATASET}_${LEVEL}_daily-zonal-anom_native.nc
	cdo ${TSCALE} -${PERIOD} $< $@
	ncatted -O -a axis,time,c,c,T $@

## Step 3: Plot the envelope
${FIG_DIR}/env/${TSCALE_LABEL_SHORT}/env-${WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL_SHORT}_${GRID}_${PLOT_END}.png : ${RWID_DIR}/env-${WAVE_LABEL}-va_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}_${GRID}.nc ${PDATA_DIR}/${CONTOUR-VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}-zonal_anom_native.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_envelope.py $< va ${TSTEP} --contour $(word 2,$^) ${CONTOUR_VAR} --timescale ${TSCALE_LABEL_SHORT} --time ${PLOT_START} ${PLOT_END} none --projection spstere --stride ${STRIDE} --raphael --ofile $@
	

### Fourier transform visualisation (plot_hilbert.py) ###

# Step 4: Plot the transform

${FIG_DIR}/hilbert/${TSCALE_LABEL_SHORT}/hilbert-va_${DATASET}_${LEVEL}_${TSCALE_LABEL_SHORT}_${GRID}-${LAT_LABEL}_${PLOT_END}.png : ${PDATA_DIR}/va_${DATASET}_${LEVEL}_${TSCALE_LABEL_LONG}_${GRID}.nc
	${CDAT} ${VIS_SCRIPT_DIR}/plot_hilbert.py $< va ${TSTEP} $@ --timescale ${TSCALE_LABEL_SHORT} --time ${PLOT_START} ${PLOT_END} none --latitude ${LAT_RANGE} --stride ${STRIDE}



