# zw3_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_HOME}/data/processed
RWID_DIR=${PDATA_DIR}/rwid/zw3
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.py
#FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh   
ZONAL_ANOM_METHOD=${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh

# Dataset
DATASET=Merra
LEVEL=250hPa
GRID=r360x181
TSCALE=runmean,30
TSCALE_LABEL=030day-runmean

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
AMP_MIN=7
EXTENT_MIN=300
EXTENT_MAX=360

# Plot envelope 
PLOT_START=2001-01-01
PLOT_END=2003-12-31

# Composite
COMPOSITE_TIMESCALE=monthly
COMPOSITE_PLACEHOLDER=JAN

# Target
TARGET=${RWID_DIR}/figures/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL}_${GRID}_${PLOT_END}.png
