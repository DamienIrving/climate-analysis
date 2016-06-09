# ohc_config.mk

# System configuration

PYTHON=/g/data/r87/dbi599/miniconda2/envs/default/bin/python

MY_DATA_DIR=/g/data/r87/dbi599
UA6_DATA_DIR=/g/data/ua6
CMIP5_DIR_START=/drstree/CMIP5/GCM
MY_CMIP5_DIR=${MY_DATA_DIR}${CMIP5_DIR_START}
UA6_CMIP5_DIR=${UA6_DATA_DIR}${CMIP5_DIR_START}

DATA_SCRIPT_DIR=~/climate-analysis/data_processing
VIS_SCRIPT_DIR=~/climate-analysis/visualisation

FIG_TYPE=png

# Analysis details
ORGANISATION=CSIRO-QCCCE
MODEL=CSIRO-Mk3-6-0
EXPERIMENT=historical
RUN=r10i1p1
CONTROL_RUN=r1i1p1
VOLUME_RUN=r0i0p0

MAX_DEPTH=2000
START_DATE=1956-01-01
END_DATE=2005-12-31

METRIC=ohc-metrics-globe60equiv
REF=--ref_region globe60

TARGET=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/${METRIC}/${RUN}/${METRIC}_Omon_${MODEL}_${EXPERIMENT}_${RUN}_all.nc
