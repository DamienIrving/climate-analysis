# zw3_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_HOME}/data/processed
ZW3_DIR=${PDATA_DIR}/zw3
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh
#FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.py   
ZONAL_ANOM_METHOD=bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh

# Dataset
DATASET=ERAInterim
LEVEL=500hPa
GRID=native
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

# Target
TARGET=${ZW3_DIR}/zw3-${ENV_WAVE_LABEL}-va-stats-threshold${THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}-${LAT_LABEL}.csv
