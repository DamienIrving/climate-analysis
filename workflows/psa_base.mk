# zw_base.mk
#
# Description: Basic workflow that underpins all other zonal wave (zw) workflows 
#
# To execute:
#	make -n -B -f zw_base.mk  (-n is a dry run) (-B is a force make)

# Pre-processing:
#	The regirdding (if required) needs to be done beforehand 
#	(probably using cdo remapcon2,r360x181 in.nc out.nc)
#	So does the zonal anomaly


# Define marcos
include psa_config.mk

all : ${TARGET}



# Core variables

V_ORIG=${DATA_DIR}/va_${DATASET}_${LEVEL}_daily_native.nc
U_ORIG=${DATA_DIR}/ua_${DATASET}_${LEVEL}_daily_native.nc

## Streamfunction

SF_ORIG=${DATA_DIR}/sf_${DATASET}_${LEVEL}_daily_native.nc
${SF_ORIG} : ${U_ORIG} ${V_ORIG}
	bash ${DATA_SCRIPT_DIR}/calc_wind_quantities.sh streamfunction $< ua $(word 2,$^) va $@ ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

SF_ANOM_RUNMEAN=${DATA_DIR}/sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native.nc
${SF_ANOM_RUNMEAN} : ${SF_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

SF_ZONAL_ANOM=${DATA_DIR}/sf_${DATASET}_${LEVEL}_daily_native-zonal-anom.nc
${SF_ZONAL_ANOM} : ${SF_ORIG}		
	bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh $< sf $@ ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

SF_ZONAL_ANOM_RUNMEAN=${DATA_DIR}/sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-zonal-anom.nc 
${SF_ZONAL_ANOM_RUNMEAN} : ${SF_ZONAL_ANOM}
	cdo ${TSCALE} $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

## Rotated meridional wind

VROT_ORIG=${DATA_DIR}/vrot_${DATASET}_${LEVEL}_daily_native-${NPLABEL}.nc
${VROT_ORIG} : ${U_ORIG} ${V_ORIG}
	bash ${DATA_SCRIPT_DIR}/calc_vrot.sh ${NPLAT} ${NPLON} $< eastward_wind $(word 2,$^) northward_wind $@ ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

VROT_ANOM_DAILY=${DATA_DIR}/vrot_${DATASET}_${LEVEL}_daily-anom-wrt-all_native-${NPLABEL}.nc
${VROT_ANOM_DAILY} : ${VROT_ORIG} 
	cdo ydaysub $< -ydayavg $< $@

VROT_ANOM_RUNMEAN=${DATA_DIR}/vrot_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.nc
${VROT_ANOM_RUNMEAN} : ${VROT_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

## Composite variables (tas, pr, sic)

TAS_ORIG=${DATA_DIR}/tas_${DATASET}_surface_daily_native.nc
TAS_ANOM_RUNMEAN=${DATA_DIR}/tas_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc
${TAS_ANOM_RUNMEAN} : ${TAS_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

PR_ORIG=${DATA_DIR}/pr_${DATASET}_surface_daily_native.nc
PR_ANOM_RUNMEAN=${DATA_DIR}/pr_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc
${PR_ANOM_RUNMEAN} : ${PR_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

SIC_ORIG=${DATA_DIR}/sic_${DATASET}_surface_daily_native.nc
SIC_ANOM_RUNMEAN=${DATA_DIR}/sic_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc
${SIC_ANOM_RUNMEAN} : ${SIC_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

## Southern Annular Mode

PSL_ORIG=${DATA_DIR}/psl_${DATASET}_surface_daily_native-shextropics30.nc
PSL_RUNMEAN=${DATA_DIR}/psl_${DATASET}_surface_${TSCALE_LABEL}_native-shextropics30.nc
${PSL_RUNMEAN} : ${PSL_ORIG}
	cdo ${TSCALE} $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

SAM_INDEX=${INDEX_DIR}/sam_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${SAM_INDEX} : ${PSL_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climate_index.py SAM $< psl $@

## Nino 3.4

TOS_ORIG=${DATA_DIR}/tos_${DATASET}_surface_daily_native-tropicalpacific.nc
TOS_RUNMEAN=${DATA_DIR}/tos_${DATASET}_surface_${TSCALE_LABEL}_native-tropicalpacific.nc
${TOS_RUNMEAN} : ${TOS_ORIG}
	cdo ${TSCALE} $< $@
	bash ${DATA_SCRIPT_DIR}/fix_time_bounds.sh $@ ${PYTHON} ${DATA_SCRIPT_DIR}

NINO34_INDEX=${INDEX_DIR}/nino34_${DATASET}_surface_${TSCALE_LABEL}_native.nc 
${NINO34_INDEX} : ${TOS_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_climate_index.py NINO34 $< tos $@



# PSA identification

## Phase and amplitude of each Fourier component

FOURIER_COEFFICIENTS=${PSA_DIR}/fourier-vrot_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.nc 
${FOURIER_COEFFICIENTS} : ${VROT_ANOM_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_fourier_transform.py $< vrot $@ 1 10 coefficients --latitude ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --valid_lon ${LON_SEARCH_MIN} ${LON_SEARCH_MAX} --avelat --env_max 4 7

## Hilbert transformed signal

INVERSE_FT=${PSA_DIR}/ift-${WAVE_LABEL}-vrot_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.nc  
${INVERSE_FT} : ${VROT_ANOM_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_fourier_transform.py $< vrot $@ ${WAVE_MIN} ${WAVE_MAX} hilbert --latitude ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --valid_lon ${LON_SEARCH_MIN} ${LON_SEARCH_MAX} --avelat

## PSA date lists

ALL_DATES_PSA=${PSA_DIR}/dates-psa_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.txt 
${ALL_DATES_PSA} : ${FOURIER_COEFFICIENTS}
	${PYTHON} ${DATA_SCRIPT_DIR}/psa_date_list.py $< $@ 

FILTERED_DATES_PSA=${PSA_DIR}/dates-psa_duration-gt${DURATION}_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.txt 
${FILTERED_DATES_PSA} : ${FOURIER_COEFFICIENTS}
	${PYTHON} ${DATA_SCRIPT_DIR}/psa_date_list.py $< $@ --duration_filter ${DURATION}  

## PSA stats lists

ALL_STATS_PSA=${PSA_DIR}/stats-psa_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.csv 
${ALL_STATS_PSA} : ${FOURIER_COEFFICIENTS}
	${PYTHON} ${DATA_SCRIPT_DIR}/psa_date_list.py $< $@ --full_stats



# PSA demonstration

## EOF analysis (would need to manually edit for monthly tstep data)

EOF_ANAL=${PSA_DIR}/eof-sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.nc
${EOF_ANAL} : ${SF_ZONAL_ANOM_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_eof.py --maxlat 0.0 --time 1979-01-01 2014-12-31 --eof_scaling 3 --pc_scaling 1 $< streamfunction $@

PLOT_EOF=${PSA_DIR}/eof-sf_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native-sh-zonal-anom.${FIG_TYPE}
${PLOT_EOF} : ${EOF_ANAL}
	bash ${VIS_SCRIPT_DIR}/plot_eof.sh $< $@ ${PYTHON} ${VIS_SCRIPT_DIR}

## Rotation example

.PHONY : plot_rotation
plot_rotation : ${SF_ANOM_RUNMEAN} ${VROT_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_psa_rotation.sh $< $(word 2,$^) ${EXAMPLE_DATE} ${MAP_DIR} ${PYTHON} ${VIS_SCRIPT_DIR}

## PSA check (spatial map and FT for given dates)

.PHONY : psa_check
psa_check : ${FILTERED_DATES_PSA} ${SF_ANOM_RUNMEAN} ${VROT_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_psa_check.sh $< $(word 2,$^) streamfunction $(word 3,$^) rotated_northward_wind vrot 1986 1988 ${MAP_DIR} ${PYTHON} ${VIS_SCRIPT_DIR}



# Results visualisation

## Timescale spectrum

PLOT_SPECTRUM=${PSA_DIR}/figures/vrot-r2spectrum_${DATASET}_${LEVEL}_daily-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE}
${PLOT_SPECTRUM} : ${VROT_ANOM_DAILY}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_timescale_spectrum.py $< vrot $@ --latitude ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --runmean 365 180 90 60 30 15 10 5 1 --scaling R2 --valid_lon ${LON_SEARCH_MIN} ${LON_SEARCH_MAX} --window 10 --figure_size 7 6

## PSA phase plot (histogram)

PLOT_PSA_PHASE_HIST=${PSA_DIR}/psa-phase-histogram_wave${FREQ}_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE}
${PLOT_PSA_PHASE_HIST} : ${ALL_STATS_PSA}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_psa_stats.py $< phase_distribution $@ --epochs --phase_res 0.75 --subset_width 20 --phase_group 4.5 19.5 --phase_group 37.5 52.5

## PSA phase plot (composites)

PLOT_PSA_PHASE_COMP=${PSA_DIR}/psa-phase-composites_wave${FREQ}_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE}
${PLOT_PSA_PHASE_COMP} : ${FOURIER_COEFFICIENTS} ${SF_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_psa_phase_composites.sh $< $(word 2,$^) ${FREQ} $@ ${PSA_POS_START} ${PSA_POS_END} ${PSA_NEG_START} ${PSA_NEG_END} ${MIN1_START} ${MIN1_END} ${MIN2_START} ${MIN2_END} ${PYTHON} ${DATA_SCRIPT_DIR} ${VIS_SCRIPT_DIR} ${TEMPDATA_DIR}

## PSA seasonality plot (histogram)

PLOT_SEASONALITY=${PSA_DIR}/psa-seasonality-group_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE} 
${PLOT_SEASONALITY} : ${FOURIER_COEFFICIENTS}
	bash ${VIS_SCRIPT_DIR}/plot_psa_phase_seasonality.sh $< ${FREQ} $@ ${PSA_POS_START} ${PSA_POS_END} ${PSA_NEG_START} ${PSA_NEG_END} ${PYTHON} ${DATA_SCRIPT_DIR} ${VIS_SCRIPT_DIR} ${TEMPDATA_DIR}

## Event phase/amplitude plot wiith duration historgram (line graph)

EVENT_PLOT=${PSA_DIR}/psa-event-summary_wave${FREQ}-duration-gt${DURATION}_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE}
${EVENT_PLOT} : ${ALL_STATS_PSA}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_psa_stats.py $< event_summary $@ --min_duration ${DURATION} --gradient_limit 0.25

## PSA variable composites plot (spatial)

PLOT_VARCOMPS=${PSA_DIR}/psa-${VAR_SHORT}-composite-phase-range_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE} 
${PLOT_VARCOMPS} : ${FOURIER_COEFFICIENTS} ${SF_ANOM_RUNMEAN} ${VAR_ANOM_RUNMEAN}
	bash ${VIS_SCRIPT_DIR}/plot_psa_var_composites.sh $< $(word 2,$^) $(word 3,$^) ${VAR_SHORT} ${VAR_LONG} ${FREQ} $@ ${PYTHON} ${DATA_SCRIPT_DIR} ${VIS_SCRIPT_DIR} ${TEMPDATA_DIR}

PLOT_VARCOMPS_ALL=${PSA_DIR}/psa-var-composites-phase-range_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.${FIG_TYPE} 
${PLOT_VARCOMPS_ALL} : ${FOURIER_COEFFICIENTS} ${SF_ANOM_RUNMEAN} ${TAS_ANOM_RUNMEAN} ${PR_ANOM_RUNMEAN} ${SIC_ANOM_RUNMEAN} 
	bash ${VIS_SCRIPT_DIR}/plot_psa_var_composite_combo.sh $< $(word 2,$^) $(word 3,$^) $(word 4,$^) $(word 5,$^) ${FREQ} $@ ${PSA_POS_START} ${PSA_POS_END} ${PSA_NEG_START} ${PSA_NEG_END} ${PYTHON} ${DATA_SCRIPT_DIR} ${VIS_SCRIPT_DIR} ${TEMPDATA_DIR}

## SAM vs ENSO plot

SAM_VS_NINO34_PLOT=${PSA_DIR}/nino34-vs-sam_psa-phases_ERAInterim_surface_030day-runmean_native.${FIG_TYPE}
${SAM_VS_NINO34_PLOT} : ${SAM_INDEX} ${NINO34_INDEX} ${FOURIER_COEFFICIENTS} 
	bash ${VIS_SCRIPT_DIR}/plot_psa-phase-vs-enso-sam.sh $< $(word 2,$^) nino34 $(word 3,$^) ${FREQ} $@ ${PSA_POS_START} ${PSA_POS_END} ${PSA_NEG_START} ${PSA_NEG_END} ${PYTHON} ${DATA_SCRIPT_DIR} ${VIS_SCRIPT_DIR} ${TEMPDATA_DIR}

