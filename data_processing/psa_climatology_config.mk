# psa_climatology_config.mk

# System configuration
DATA_DIR=/mnt/meteo0/data/simmonds/dbirving/${DATASET}/data
PDATA_DIR=${DATA_DIR}/processed
RWID_DIR=${PDATA_DIR}/rwid/psa
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
DATA_SCRIPT_DIR=~/phd/data_processing
ROIM_SCRIPT_DIR=${DATA_SCRIPT_DIR}/roim
VROT_METHOD=bash ${DATA_SCRIPT_DIR}/calc_vwind_rotation.sh   #${CDAT} ${DATA_SCRIPT_DIR}/calc_vwind_rotation.py                               
ENV_METHOD=bash ${DATA_SCRIPT_DIR}/calc_envelope.sh   #${CDAT} ${DATA_SCRIPT_DIR}/calc_envelope.py

# Dataset
DATASET=Merra

# Grid rotation
NP=--north_pole 20 260
NPLAT=$(word 2, ${NP})
NPLON=$(word 3, ${NP})
NP_LABEL=np${NPLAT}N${NPLON}E
GRID=--grid -90.0 181 1.0 0.0 360 1.0
GRID_LABEL=y$(word 3,${GRID})x$(word 6,${GRID})

# Envelope extraction
LON_SEARCH=--longitude 225 335
LAT_SEARCH=--latitude -10 10
LON_LABEL=lon$(word 2,${LON_SEARCH})E$(word 3,${LON_SEARCH})E
LAT_LABEL=lat10S10N
WAVE_SEARCH=--wavenumbers 5 7
WAVE_LABEL=w567

# Rossby wve train identification
CLIP_THRESH=14
CLIP_METHOD=absolute
CLIP_LABEL=${CLIP_METHOD}${CLIP_THRESH}
ROIM_START=1979010100
ROIM_TRES=24
ROIM_ZRES=1

# Filter date list
FILTER_REGION=marie-byrd-land
FILTER_DIRECTION=below
FILTER_THRESH=-5.0
FILTER_LABEL=marie-byrd-land-va-below-neg5

# Calculate composite
COMPOSITE_SEASON=SON
COMPOSITE_VAR=tas
COMPOSITE_LEVEL=surface







