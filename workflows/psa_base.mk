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

## Rotated meridional wind

VROT_ORIG=${DATA_DIR}/vrot_${DATASET}_${LEVEL}_daily_native-${NPLABEL}.nc
${VROT_ORIG} : ${U_ORIG} ${V_ORIG}
	bash ${DATA_SCRIPT_DIR}/calc_vrot.sh ${NPLAT} ${NPLON} $< eastward_wind $(word 2,$^) northward_wind $@ ${PYTHON} ${DATA_SCRIPT_DIR} ${TEMPDATA_DIR}

VROT_ANOM_RUNMEAN=${DATA_DIR}/vrot_${DATASET}_${LEVEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.nc
${VROT_ANOM_RUNMEAN} : ${VROT_ORIG} 
	cdo ${TSCALE} -ydaysub $< -ydayavg $< $@
	ncatted -O -a bounds,time,d,, $@
	ncks -O -x -v time_bnds $@


# PSA identification

## Phase and amplitude of each Fourier component

FOURIER_COEFFICIENTS=${PSA_DIR}/fourier-vrot_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.nc 
${FOURIER_COEFFICIENTS} : ${VROT_ANOM_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_fourier_transform.py $< vrot $@ 1 10 coefficients --latitude ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --valid_lon ${LON_SEARCH_MIN} ${LON_SEARCH_MAX} --avelat

## Hilbert transformed signal

INVERSE_FT=${PSA_DIR}/ift-${WAVE_LABEL}-vrot_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.nc  
${INVERSE_FT} : ${VROT_ANOM_RUNMEAN}
	${PYTHON} ${DATA_SCRIPT_DIR}/calc_fourier_transform.py $< vrot $@ ${WAVE_MIN} ${WAVE_MAX} hilbert --latitude ${LAT_SEARCH_MIN} ${LAT_SEARCH_MAX} --valid_lon ${LON_SEARCH_MIN} ${LON_SEARCH_MAX} --avelat

## PSA date list
DATES_PSA=${PSA_DIR}/dates-psa_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.txt 
${DATES_PSA} : ${FOURIER_COEFFICIENTS}
	${PYTHON} ${DATA_SCRIPT_DIR}/psa_date_list.py $< $@ 

## PSA phase plot
PLOT_PSA_PHASE=${PSA_DIR}/psa-phase_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.png
${PLOT_PSA_PHASE} : ${FOURIER_COEFFICIENTS} ${DATES_PSA}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_psa_phase.py $< wave7_phase number $(word 2,$^) $@ --seasonal
