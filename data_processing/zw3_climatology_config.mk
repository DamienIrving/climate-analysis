# zw3_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data/processed
PDATA_DIR=${DATA_HOME}/data/processed
RWID_DIR=${PDATA_DIR}/rwid/zw3
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
ENV_METHOD=bash ${SCRIPT_DIR}/calc_envelope.sh   #${CDAT} ${SCRIPT_DIR}/calc_envelope.py
ZONAL_ANOM_METHOD=${SCRIPT_DIR}/calc_zonal_anomaly.sh

# Dataset
DATASET=Merra
GRID=r360x181
TSCALE=30day-runmean

# Envelope extraction
MER_METHOD=mermax
LAT_SEARCH_MIN=-70
LAT_SEARCH_MAX=-40
LAT_LABEL=lat70S40S
WAVE_SEARCH=--wavenumbers 2 4
WAVE_LABEL=w234

# Extent statistics
AMP_MIN=7
EXTENT_MIN=0
EXTENT_MAX=360

# Plot envelope 
PLOT_START=2002-01-01
PLOT_END=2002-12-31




