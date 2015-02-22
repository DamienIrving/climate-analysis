# psa_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_DIR}/processed
RWID_DIR=${PDATA_DIR}/rwid/psa
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/local/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
ENV_METHOD=bash ${DATA_SCRIPT_DIR}/calc_fourier_transform.sh
VROT_METHOD=bash ${DATA_SCRIPT_DIR}/calc_vwind_rotation.sh

# Dataset
DATASET=Merra

# Grid rotation
NP=--north_pole 20 260
NPLAT=$(word 2, ${NP})
NPLON=$(word 3, ${NP})
NP_LABEL=np${NPLAT}N${NPLON}E
GRID=--grid -90.0 181 1.0 0.0 360 1.0
GRID_LABEL=y$(word 3,${GRID})x$(word 6,${GRID})

# Temporal smoothing
TSCALE=runmean,30
TSCALE_LABEL=daily
#30day-runmean

# Envelope extraction
LON_SEARCH_MIN=225
LON_SEARCH_MAX=335
LON_SEARCH=--longitude ${LON_SEARCH_MIN} ${LON_SEARCH_MAX}
LON_LABEL=lon${LON_SEARCH_MIN}E${LON_SEARCH_MAX}E
WAVE_SEARCH=--filter 5 7 --outtype hilbert
WAVE_LABEL=w567

# Hovmoller diagram
MER_METHOD=mermax
LAT_SEARCH_MIN=-10
LAT_SEARCH_MAX=10
LAT_LABEL=lat10S10N

# Event statistics
AMP_MIN=6
EVENT_EXTENT=100
DURATION_MIN=1
DURATION_MAX=100

# Plot envelope 
PLOT_START=2002-01-01
PLOT_END=2005-12-31

## Filter date list
#FILTER_REGION=marie-byrd-land
#FILTER_DIRECTION=below
#FILTER_THRESH=-5.0
#FILTER_LABEL=marie-byrd-land-va-below-neg5
#
## Calculate composite
#COMPOSITE_SEASON=SON
#COMPOSITE_VAR=tas
#COMPOSITE_LEVEL=surface

# Target

TARGET=${RWID_DIR}/figures/env-${WAVE_LABEL}-vrot_Merra_250hPa_${TSCALE_LABEL}-anom-wrt-all_${GRID_LABEL}-${NP_LABEL}-${LON_LABEL}_${PLOT_END}.png






