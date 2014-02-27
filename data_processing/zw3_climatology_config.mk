# zw3_climatology_config.mk

# System configuration
DATA_DIR=/mnt/meteo0/data/simmonds/dbirving/${DATASET}/data
PDATA_DIR=${DATA_DIR}/processed
RWID_DIR=${PDATA_DIR}/rwid
CDAT=/usr/local/uvcdat/1.2.0rc1/bin/cdat
DATA_SCRIPT_DIR=~/phd/data_processing
ROIM_SCRIPT_DIR=${DATA_SCRIPT_DIR}/roim
ENV_METHOD=bash ${DATA_SCRIPT_DIR}/calc_envelope.sh   #${CDAT} ${DATA_SCRIPT_DIR}/calc_envelope.py

# Dataset
DATASET=Merra
GRID=r360x181

# Envelope extraction
LAT_SEARCH=--latitude -70 -50
LAT_LABEL=lat70S50S
WAVE_SEARCH=--wavenumbers 2 4
WAVE_LABEL=w234

# Rossby wve train identification
CLIP_THRESH=14
CLIP_METHOD=absolute
CLIP_LABEL=${CLIP_METHOD}${CLIP_THRESH}

ROIM_START=1979010100
ROIM_TRES=24
ROIM_ZRES=1




