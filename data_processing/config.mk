# config-vortex.mk

# System configuration
DATA_DIR=/mnt/meteo0/data/simmonds/dbirving/${DATASET}/data
PDATA_DIR=${DATA_DIR}/processed
RWID_DIR=${PDATA_DIR}/rwid
CDAT=/usr/local/uvcdat/1.2.0rc1/bin/cdat
DATA_SCRIPT_DIR=~/phd/data_processing
ROIM_SCRIPT_DIR=${DATA_SCRIPT_DIR}/roim

# Dataset
DATASET=Merra

# Grid rotation
NP=--north_pole 20 260
GRID=--grid -90.0 181 1.0 0.0 360 1.0

# Envelope extraction
LON_SEARCH=--longitude 225 335
LAT_SEARCH=--latitude -10 10
LON_LABEL=lon$(word 2,${LON_SEARCH})E$(word 3,${LON_SEARCH})E
LAT_LABEL=lat10S10N
WAVENUMS=567

# Rossby wve train identification
CLIP_THRESH=14
CLIP_METHOD=absolute
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




