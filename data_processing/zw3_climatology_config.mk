# zw3_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_HOME}/data/processed
ZW3_DIR=${PDATA_DIR}/zw3
FIG_DIR=${ZW3_DIR}/figures/maps
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh
#FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.py   
ZONAL_ANOM_METHOD=bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh


## Climatology

# Dataset
DATASET=ERAInterim
LEVEL=500hPa
GRID=native
TSTEP=daily
TSCALE=runmean,90
TSCALE_LABEL=090day-runmean

# Envelope extraction
MER_METHOD=mermax
LAT_SEARCH_MIN=-70
LAT_SEARCH_MAX=-40
LAT_LABEL=lat70S40S
ENV_SEARCH=--filter 2 9 --outtype hilbert
ENV_WAVE_LABEL=w29

# Fourier coefficients
COE_SEARCH=--filter 1 9 --outtype coefficients 
COE_WAVE_LABEL=w19

# Extent statistics
THRESH=75pct


## Applications

# Plot envelope 
PLOT_START=1979-01-01
PLOT_END=2013-12-31
CONTOUR_VAR=sf
STRIDE=4


## Target
TARGET=${FIG_DIR}/env/${TSCALE_LABEL}/env-${ENV_WAVE_LABEL}-va-${CONTOUR_VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}_${PLOT_END}.png
