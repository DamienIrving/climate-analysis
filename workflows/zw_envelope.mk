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
ENV_PLOT=${MAP_DIR}/envva-${ENV_WAVE_LABEL}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native_${PLOT_DATE1}_${PLOT_DATE2}.png 
${ENV_PLOT}: ${ENV_RUNMEAN} ${SF_ZONAL_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_envelope.sh $< envva $(word 2,$^) sf ${PLOT_DATE1} ${PLOT_DATE2} ${LAT_SINGLE} $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## Plot the Hilbert transform

HILBERT_PLOT=${ZW_DIR}/figures/hilbert_zw_${ENV_WAVE_LABEL}_va_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-${LAT_LABEL}_${PLOT_DATE1}_${PLOT_DATE2}.png 
${HILBERT_PLOT}: ${V_RUNMEAN}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_hilbert.py $< va $@ ${PLOT_DIMS} --latitude ${LAT_SINGLE} --dates ${PLOT_DATE1} ${PLOT_DATE2} --wavenumbers ${WAVE_MIN} ${WAVE_MAX} --figure_size 15 6


# Periodograms

## Mutli-timescale and composite spectrum

V_SPECTRUM=${SPECTRA_DIR}/va-r2spectrum_${DATASET}_${LEVEL}_daily_native-${LAT_LABEL}.png
${V_SPECTRUM}: ${V_ORIG} ${DATES_${INDEX_CAPS}_HIGH} ${DATES_${INDEX_CAPS}_LOW}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_timescale_spectrum.py $< va $(word 2,$^) $(word 3,$^) $@ --latitude ${LAT_SINGLE} --runmean 365 180 90 60 30 15 10 5 1 --scaling R2




