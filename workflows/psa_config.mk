# zw_climatology_config.mk

# System configuration

DATA_HOME=/mnt/meteo0/data/simmonds/dbirving
TEMPDATA_DIR=${DATA_HOME}/temp
DATA_DIR=${DATA_HOME}/${DATASET}/data
PSA_DIR=${DATA_DIR}/psa
INDEX_DIR=${DATA_DIR}/indexes
MAP_DIR=${ZW_DIR}/figures/maps
COMP_DIR=${ZW_DIR}/figures/composites
SPECTRA_DIR=${ZW_DIR}/figures/spectra
PYTHON=/usr/local/anaconda/bin/python
DATA_SCRIPT_DIR=~/climate-analysis/data_processing
VIS_SCRIPT_DIR=~/climate-analysis/visualisation


# Analysis details

## Dataset
DATASET=ERAInterim
LEVEL=500hPa
TSTEP=daily
TSCALE=runmean,30


TARGET=
