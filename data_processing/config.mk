# config-vortex.mk

# Processing options
DATASET=Merra
NP=--north_pole 20 260
GRID=--grid -90.0 181 1.0 0.0 360 1.0
LON_SEARCH=--longitude 225 335
LAT_SEARCH=--latitude -10 10
WAVENUMS=567
CLIP_THRESH=14
CLIP_METHOD=absolute

# System configuration
DATA_DIR=/mnt/meteo0/data/simmonds/dbirving/${DATASET}/data
PDATA_DIR=${DATA_DIR}/processed
CDAT=/usr/local/uvcdat/1.2.0rc1/bin/cdat


