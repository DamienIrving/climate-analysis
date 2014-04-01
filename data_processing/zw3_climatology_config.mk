# zw3_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data/processed
PDATA_DIR=${DATA_HOME}/data/processed
RWID_DIR=${PDATA_DIR}/rwid/zw3
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
SCRIPT_DIR=~/phd/data_processing
ENV_METHOD=bash ${SCRIPT_DIR}/calc_envelope.sh   #${CDAT} ${SCRIPT_DIR}/calc_envelope.py

# Dataset
DATASET=Merra
GRID=r360x181
TSCALE=30day-runmean

# Envelope extraction
LAT_SEARCH=-70,-40
LAT_LABEL=lat70S40S
WAVE_SEARCH=--wavenumbers 2 4
WAVE_LABEL=w234

# Extent statistics
AMP_MIN=7
EXTENT_MIN=1




