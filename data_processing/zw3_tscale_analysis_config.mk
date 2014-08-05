# zw3_tscale_analysis_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_HOME}/data/processed
RWID_DIR=${PDATA_DIR}/rwid/zw3
FIG_DIR=${RWID_DIR}/figures/tscale_anal
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
ZONAL_ANOM_METHOD=bash ${DATA_SCRIPT_DIR}/calc_zonal_anomaly.sh

# Dataset
DATASET=Merra
GRID=r360x181
TSCALE=runmean,30
PERIOD=seldate,2000-01-01,2004-12-31
TSCALE_LABEL_LONG=30day-runmean-2000-2004
TSCALE_LABEL_SHORT=30day-runmean

# Envelope extraction
WAVE_SEARCH=--filter 2 9 --outtype hilbert
WAVE_LABEL=w29

# Plot envelope 
PLOT_START=2002-06-01
PLOT_END=2002-06-30

# Plot fourier transform
LAT=-50
LAT_LABEL=50S
TSTEP=daily

# Target
#TARGET=${FIG_DIR}/env/${TSCALE_LABEL_SHORT}/env-${WAVE_LABEL}-va_Merra_250hPa_${TSCALE_LABEL_SHORT}_${GRID}_${PLOT_END}.png
TARGET=${FIG_DIR}/hilbert/${TSCALE_LABEL_SHORT}/hilbert-va_Merra_250hPa_${TSCALE_LABEL_SHORT}_${GRID}-${LAT_LABEL}_${PLOT_END}.png
