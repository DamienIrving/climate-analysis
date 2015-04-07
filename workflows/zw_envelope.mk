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


# Planetary wave index and other wave stats

## Collapse the meridional dimension

ENV_2D=${ZW_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
${ENV_2D} : ${ENV_3D}
	cdo ${MER_METHOD} -sellonlatbox,0,360,${LAT_SEARCH_MIN},${LAT_SEARCH_MAX} $< $@
	bash ${CDO_FIX_SCRIPT} $@ env${VAR}

## Calculate the PWI and other wave statistics (mean & max, extent/coverage, etc)

WAVE_STATS=${ZW_DIR}/wavestats_zw_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.nc
${WAVE_STATS} : ${ENV_2D}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_wave_stats.py $< env${VAR} $@ --threshold ${EXTENT_THRESH}

## Generate list of dates exceeding some PWI threshold (for later use in composite creation)

DATE_LIST=${COMP_DIR}/dates_zw_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.txt
${DATE_LIST}: ${WAVE_STATS}
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --date_list $@ --metric_threshold ${METRIC_HIGH_THRESH}

## Common table/database

TABLE=${ZW_DIR}/table_zw_${ENV_WAVE_LABEL}-extent${EXTENT_THRESH}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv
${TABLE} : ${WAVE_STATS} ${ZW3_INDEX} ${FOURIER_INFO}
	${PYTHON} ${DATA_SCRIPT_DIR}/create_zw_table.py $(word 1,$^) $(word 2,$^) $(word 3,$^) $@


# Envelope plots

## Plot the envelope for a selection of timesteps

ENV_PLOT=${MAP_DIR}/env/${TSCALE_LABEL}/${VAR}/env${VAR}-${ENV_WAVE_LABEL}-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}_${PLOT_DATE1}_${PLOT_DATE2}.png 
${ENV_PLOT}: ${ENV_3D} ${CONTOUR_ZONAL_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_envelope.sh $< env${VAR} $(word 2,$^) ${CONTOUR_VAR} ${PLOT_DATE1} ${PLOT_DATE2} ${LAT_SINGLE} $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## Plot the climatological mean envelope

ENV_CLIM=${ZW_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-clim_${GRID}.nc
${ENV_CLIM} : ${ENV_3D} 
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_composite.py $< env${VAR} $@ --region sh

ENV_CLIM_PLOT=${MAP_DIR}/env${VAR}_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}-clim_${GRID}.png
${ENV_CLIM_PLOT} : ${ENV_CLIM}
	bash ${VIS_SCRIPT_DIR}/plot_seasonal_climatology.sh $< env${VAR} $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## Plot the Hilbert transform

HILBERT_PLOT=${ZWINDEX_DIR}/hilbert/${TSCALE_LABEL}/hilbert_zw_${ENV_WAVE_LABEL}_${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${LAT_LABEL}_${PLOT_DATE1}_${PLOT_DATE2}.png 
${HILBERT_PLOT}: ${V_RUNMEAN}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_hilbert.py $< ${VAR} $@ ${PLOT_DIMS} --latitude ${LAT_SINGLE} --dates ${PLOT_DATE1} ${PLOT_DATE2} --wavenumbers ${WAVE_MIN} ${WAVE_MAX} --figure_size 15 6


# PWI climatology stats

## Seasonal and monthly summaries

SEAS_MON_SUMMARY_PLOT=${ZWINDEX_DIR}/clim/montots-seasvals_zw_${METRIC}${METRIC_HIGH_THRESH}-${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png 
${SEAS_MON_SUMMARY_PLOT} : ${WAVE_STATS} 
	${PYTHON} ${DATA_SCRIPT_DIR}/parse_wave_stats.py $< ${METRIC} --plot_name $@ --plot_types monthly_totals_histogram seasonal_values_line --metric_threshold ${METRIC_HIGH_THRESH} --scale_annual 0.25 --figure_size 16 6


# Periodograms

## Mutli-timescale and composite spectrum

V_SPECTRUM=${SPECTRA_DIR}/va-r2spectrum_${DATASET}_${LEVEL}_daily_native-${LAT_LABEL}.png
${V_SPECTRUM}: ${V_ORIG} ${DATES_${INDEX_CAPS}_HIGH} ${DATES_${INDEX_CAPS}_LOW}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_timescale_spectrum.py $< va $(word 2,$^) $(word 3,$^) $@ --latitude ${LAT_SINGLE} --runmean 1 5 10 15 30 60 90 180 365 --scaling R2


## Mutli-file spectrum

MULTIFILE_SPECTRUM=${SPECTRA_DIR}/${METRIC}-r2spectrum_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.png
${MULTIFILE_SPECTRUM} : ${WAVE_STATS}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_multifile_spectrum.py $< ${METRIC} $@ --scaling R2 --xlim 0 200 


