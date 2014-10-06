# zw3_tscale_analysis_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
RWID_DIR=${DATA_DIR}/zw3
FIG_DIR=${RWID_DIR}/figures/tscale_anal
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/local/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
ZONAL_ANOM_METHOD=bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh

# Dataset
VAR=va
DATASET=ERAInterim
LEVEL=500hPa
GRID=native
TSTEP=daily
TSCALE=runmean,030
PERIOD=seldate,1984-01-01,1988-12-31
TSCALE_LABEL_LONG=030day-runmean-1984-1988
TSCALE_LABEL_SHORT=030day-runmean

# Envelope extraction
WAVE_SEARCH=--filter 1 9 --outtype hilbert
WAVE_LABEL=w19
LAT_RANGE=-70 -40
LAT_LABEL=55S

# Ploting 
CONTOUR_VAR=zg
PLOT_START=1985-01-01
PLOT_END=1987-12-31
STRIDE=4


# Target
TARGET=${FIG_DIR}/hilbert/${TSCALE_LABEL_SHORT}/hilbert-va_${DATASET}_${LEVEL}_${TSCALE_LABEL_SHORT}_${GRID}-${LAT_LABEL}_${PLOT_END}.png

