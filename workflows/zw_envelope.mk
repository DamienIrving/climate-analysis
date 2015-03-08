# zw_envelople.mk
#
# Description: All analyses that look in detail at the wave envelope
#  and/or Fourier transform
#
# To execute:
#   make -n -B -f zw_envelope.mk  (-n is a dry run) (-B is a force make)

# Define marcos
include zw_config.mk
include zw_base.mk

all : ${TARGET}


# Envelope plots

## Plot the envelope for a selection of timesteps
ENV_PLOT=${MAP_DIR}/env/${TSCALE_LABEL}/${VAR}/env${VAR}-${ENV_WAVE_LABEL}-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}_${PLOT_DATE1}_${PLOT_DATE2}.png 
${ENV_PLOT}: ${ENV_3D} ${CONTOUR_ZONAL_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_envelope.sh $< env${VAR} $(word 2,$^) ${CONTOUR_VAR} ${PLOT_DATE1} ${PLOT_DATE2} ${LAT_SINGLE} $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## Plot the climatological mean envelope
ENV_CLIM=${ZW3_DIR}/env${VAR}_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-clim_${GRID}.nc
${ENV_CLIM} : ${ENV_3D} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< env${VAR} $@ --region sh

ENV_CLIM_PLOT=${MAP_DIR}/env${VAR}_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-clim_${GRID}.png
${ENV_CLIM_PLOT} : ${ENV_CLIM}
	bash ${VIS_SCRIPT_DIR}/plot_seasonal_climatology.sh $< env${VAR} $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## Plot the Hilbert transform
HILBERT_PLOT=${INDEX_DIR}/hilbert/${TSCALE_LABEL}/hilbert_zw3_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${LAT_LABEL}_${PLOT_DATE1}_${PLOT_DATE2}.png 
${HILBERT_PLOT}: ${V_RUNMEAN}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_hilbert.py $< ${VAR} $@ ${PLOT_DIMS} --latitude ${LAT_SINGLE} --dates ${PLOT_DATE1} ${PLOT_DATE2} --wavenumbers ${WAVE_MIN} ${WAVE_MAX} --figure_size 15 6


# PWI climatology stats

## Seasonal and monthly summaries
SEAS_MON_SUMMARY_PLOT=${INDEX_DIR}/clim/montots-seasvals_zw3_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png 
${SEAS_MON_SUMMARY_PLOT} : ${WAVE_STATS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --plot_name $@ --plot_types monthly_totals_histogram seasonal_values_line --metric_threshold ${METRIC_HIGH_THRESH} --scale_annual 0.25 --figure_size 16 6


# Composite envelope (with contour overlay)

## Step 1: Get the composite mean envelope
COMP_ENV_FILE=${COMP_DIR}/env${VAR}-composite_zw3_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}.nc 
${COMP_ENV_FILE} : ${ENV_3D} ${DATE_LIST} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< env${VAR} $@ --date_file $(word 2,$^) 

## Step 2: Get the composite mean contour
CONTOUR_ZONAL_ANOM_RUNMEAN_COMP=${COMP_DIR}/${CONTOUR_VAR}-composite_zw3_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc 
${CONTOUR_ZONAL_ANOM_RUNMEAN_COMP} : ${CONTOUR_ZONAL_ANOM_RUNMEAN} ${DATE_LIST} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< ${CONTOUR_VAR} $@ --date_file $(word 2,$^)

## Step 3: Plot
COMP_ENV_PLOT=${COMP_DIR}/env${VAR}-composite_zw3_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}-${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-zonal-anom.png
${COMP_ENV_PLOT} : ${COMP_ENV_FILE} ${CONTOUR_ZONAL_ANOM_RUNMEAN_COMP}
	bash ${VIS_SCRIPT_DIR}/plot_composite.sh $(word 1,$^) env${VAR} $(word 2,$^) ${CONTOUR_VAR} $@ ${PYTHON} ${VIS_SCRIPT_DIR}


# Periodograms

## Mutli-timescale spectrum
TSCALE_SPECTRUM=${SPECTRA_DIR}/${VAR}-r2spectrum_${DATASET}_${LEVEL}_daily_${GRID}.png
${TSCALE_SPECTRUM}: ${V_ORIG}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_timescale_spectrum.py $< ${VAR} $@ --latitude ${LAT_SINGLE} --runmean 1 5 10 15 30 60 90 180 365 --scaling R2

## Mutli-file spectrum
MULTIFILE_SPECTRUM=${SPECTRA_DIR}/${METRIC}-r2spectrum_zw3_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.png
${MULTIFILE_SPECTRUM} : ${WAVE_STATS}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_multifile_spectrum.py $< ${METRIC} $@ --scaling R2 --xlim 0 200 


