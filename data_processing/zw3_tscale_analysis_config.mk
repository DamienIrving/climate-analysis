# zw3_tscale_analysis_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_HOME}/data/processed
RWID_DIR=${PDATA_DIR}/zw3
FIG_DIR=${RWID_DIR}/figures/tscale_anal
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
ZONAL_ANOM_METHOD=bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh

# Dataset
DATASET=ERAInterim
LEVEL=500hPa
GRID=native
TSTEP=daily
TSCALE=runmean,090
PERIOD=seldate,2000-01-01,2004-12-31
TSCALE_LABEL_LONG=090day-runmean-2000-2004
TSCALE_LABEL_SHORT=090day-runmean

# Envelope extraction
WAVE_SEARCH=--filter 2 9 --outtype hilbert
WAVE_LABEL=w29
LAT_RANGE=-70 -40
LAT_LABEL=55S

# Ploting 
CONTOUR_VAR=sf
PLOT_START=2001-01-01
PLOT_END=2003-12-31
STRIDE=1


# Target
TARGET=${FIG_DIR}/env/${TSCALE_LABEL_SHORT}/env-${WAVE_LABEL}-va-${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL_SHORT}_${GRID}_${PLOT_END}.png

