# zw_climatology_config.mk

# System configuration

DATA_HOME=/mnt/meteo0/data/simmonds/dbirving
TEMPDATA_DIR=${DATA_HOME}/temp
DATA_DIR=${DATA_HOME}/${DATASET}/data
PSA_DIR=${DATA_DIR}/psa
INDEX_DIR=${DATA_DIR}/indexes
MAP_DIR=${PSA_DIR}/figures/maps
COMP_DIR=${PSA_DIR}/figures/composites
SPECTRA_DIR=${PSA_DIR}/figures/spectra
PYTHON=/usr/local/anaconda/bin/python
DATA_SCRIPT_DIR=~/climate-analysis/data_processing
VIS_SCRIPT_DIR=~/climate-analysis/visualisation


# Analysis details

## Dataset
DATASET=ERAInterim
LEVEL=500hPa
TSTEP=daily
TSCALE=runmean,30
TSCALE_LABEL=030day-runmean

## Analysis
NPLAT=20
NPLON=260
NPLABEL=np20N260E

LAT_SEARCH_MIN=-10
LAT_SEARCH_MAX=10
LAT_LABEL=lat10S10Nmean
LON_SEARCH_MIN=115
LON_SEARCH_MAX=235
LON_LABEL=lon115E235Ezeropad

WAVE_MIN=4
WAVE_MAX=7
WAVE_LABEL=w${WAVE_MIN}${WAVE_MAX}

FREQ=6
DURATION=10

VAR_SHORT=tas
VAR_LONG=surface_air_temperature
VAR_ANOM_RUNMEAN=${DATA_DIR}/${VAR_SHORT}_${DATASET}_surface_${TSCALE_LABEL}-anom-wrt-all_native.nc

## Phase groupings

PSA_POS_START=4.5
PSA_POS_END=19.5

PSA_NEG_START=37.5
PSA_NEG_END=52.5

MIN1_START=22.5
MIN1_END=37.5

MIN2_START=50.25
MIN2_END=6.0


TARGET=${PSA_DIR}/psa-var-composites-phase-range_${DATASET}_${LEVEL}-${LAT_LABEL}-${LON_LABEL}_${TSCALE_LABEL}-anom-wrt-all_native-${NPLABEL}.png
