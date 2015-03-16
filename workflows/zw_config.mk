# zw_climatology_config.mk

# System configuration

DATA_HOME=/mnt/meteo0/data/simmonds/dbirving
TEMPDATA_DIR=${DATA_HOME}/temp
DATA_DIR=${DATA_HOME}/${DATASET}/data
ZW_DIR=${DATA_DIR}/zw
INDEX_DIR=${DATA_DIR}/indexes
MAP_DIR=${ZW_DIR}/figures/maps
ZWINDEX_DIR=${ZW_DIR}/figures/indexes
COMP_DIR=${ZW_DIR}/figures/composites
SPECTRA_DIR=${ZW_DIR}/figures/spectra
CDAT=/usr/local/uvcdat/1.3.0/bin/cdat
PYTHON=/usr/local/anaconda/bin/python
DATA_SCRIPT_DIR=~/climate-analysis/data_processing
VIS_SCRIPT_DIR=~/climate-analysis/visualisation
CDO_FIX_SCRIPT=${DATA_SCRIPT_DIR}/cdo_fix.sh


# Analysis details

## Dataset
VAR=va
DATASET=ERAInterim
LEVEL=500hPa
GRID=native
TSTEP=daily
TSCALE=runmean,30
TSCALE_LABEL=030day-runmean

## Envelope extraction
MER_METHOD=mermax
LAT_SEARCH_MIN=-70
LAT_SEARCH_MAX=-40
LAT_LABEL=lat70S40S
WAVE_MIN=1
WAVE_MAX=9
ENV_WAVE_LABEL=w${WAVE_MIN}${WAVE_MAX}

## Fourier coefficients
COE_WAVE_LABEL=w${WAVE_MIN}${WAVE_MAX}
LAT_RANGE=-70 -40
LAT_SINGLE=-55
LAT_LABEL=55S

## Extent statistics
EXTENT_THRESH=75pct

## Plot envelope 
PLOT_START=2002-01-01
PLOT_END=2005-12-31
PLOT_DATE1=1986-05-22
PLOT_DATE2=2006-07-29
PLOT_DIMS=1 2
CONTOUR_VAR=zg
STRIDE=2

## Climatology
METRIC=ampmedian
METRIC_HIGH_THRESH=90pct
METRIC_LOW_THRESH=10pct

## Composite
COMP_VAR=pr
COMP_THRESH=90pct

TARGET=${ZWINDEX_DIR}/${METRIC}-vs-vwindamp_zw_${ENV_WAVE_LABEL}_env-${VAR}_${DATASET}_${LEVEL}_${TSCALE_LABEL}_${GRID}-${MER_METHOD}.png