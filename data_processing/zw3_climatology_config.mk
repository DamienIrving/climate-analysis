# zw3_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
ZW3_DIR=${DATA_DIR}/zw3
MAP_DIR=${ZW3_DIR}/figures/maps
INDEX_DIR=${ZW3_DIR}/figures/indexes
COMP_DIR=${ZW3_DIR}/figures/composites
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/local/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh
#FOURIER_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.py   
ZONAL_ANOM_METHOD=bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh


## Climatology

# Dataset
VAR=va
DATASET=ERAInterim
LEVEL=500hPa
GRID=native
TSTEP=daily
TSCALE=runmean,30
TSCALE_LABEL=030day-runmean

# Envelope extraction
MER_METHOD=mermax
LAT_SEARCH_MIN=-70
LAT_SEARCH_MAX=-40
LAT_LABEL=lat70S40S
ENV_SEARCH=--filter 1 9 --outtype hilbert
ENV_WAVE_LABEL=w19

# Fourier coefficients
COE_SEARCH=--filter 1 9 --outtype coefficients 
COE_WAVE_LABEL=w19
LAT_RANGE=-70 -40
LAT_LABEL=55S

# Extent statistics
EXTENT_THRESH=75pct


## Applications

# Plot envelope 
PLOT_START=2002-01-01
PLOT_END=2005-12-31
CONTOUR_VAR=zg
STRIDE=2

# Climatology
METRIC=env_amp_median
METRIC_THRESH=90pct


## Target
TARGET=${INDEX_DIR}/clim/${METRIC}-seasonal-values_zw3-${ENV_WAVE_LABEL}-${VAR}-stats-extent${EXTENT_THRESH}-filter${METRIC_THRESH}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png
