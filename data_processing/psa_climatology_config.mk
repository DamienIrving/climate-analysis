# psa_climatology_config.mk

# System configuration
DATA_HOME=/mnt/meteo0/data/simmonds/dbirving/${DATASET}
DATA_DIR=${DATA_HOME}/data
PDATA_DIR=${DATA_DIR}/data/processed
RWID_DIR=${PDATA_DIR}/rwid/psa
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/bin/anaconda/bin/python
DATA_SCRIPT_DIR=~/phd/data_processing
VIS_SCRIPT_DIR=~/phd/visualisation
ENV_METHOD=bash ${DATA_SCRIPT_DIR}/calc_envelope.sh
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
TSCALE_LABEL=30day-runmean

# Envelope extraction
LON_SEARCH=--longitude 225 335
LON_LABEL=lon$(word 2,${LON_SEARCH})E$(word 3,${LON_SEARCH})E
WAVE_SEARCH=--wavenumbers 5 7
WAVE_LABEL=w567

# Hovmoller diagram
MER_METHOD=mermax
LAT_SEARCH_MIN=-10
LAT_SEARCH_MAX=10
LAT_LABEL=lat10S10N

# Extent statistics
AMP_MIN=7
EXTENT_MIN=0
EXTENT_MAX=360


# Filter date list
FILTER_REGION=marie-byrd-land
FILTER_DIRECTION=below
FILTER_THRESH=-5.0
FILTER_LABEL=marie-byrd-land-va-below-neg5

# Calculate composite
COMPOSITE_SEASON=SON
COMPOSITE_VAR=tas
COMPOSITE_LEVEL=surface







