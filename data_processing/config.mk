# config-vortex.mk

# Processing options
DATASET=Merra
NP=--north_pole 20 260
GRID=--grid -90.0 181 1.0 0.0 360 1.0
LON_SEARCH=--longitude 225 335
LAT_SEARCH=--latitude -10 10
LON_LABEL=lon$(word 2,${LON_SEARCH})E$(word 3,${LON_SEARCH})E
LAT_LABEL=lat10S10N

WAVENUMS=567
CLIP_THRESH=14
CLIP_METHOD=absolute
ROIM_START=1979010100
ROIM_TRES=24
ROIM_ZRES=1

# System configuration
DATA_DIR=/mnt/meteo0/data/simmonds/dbirving/${DATASET}/data
PDATA_DIR=${DATA_DIR}/processed
RWID_DIR=${PDATA_DIR}/rwid
CDAT=/usr/local/uvcdat/1.2.0rc1/bin/cdat


