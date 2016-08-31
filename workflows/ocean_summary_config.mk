# ocean_summary_config.mk

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

# Analysis details (broad)

ORIG_VARIABLE_DIR=${MY_CMIP5_DIR}
ORIG_CONTROL_DIR=${UA6_CMIP5_DIR}
ORIG_FX_DIR=${UA6_CMIP5_DIR}

VAR=so
LONG_NAME=sea_water_salinity

ORGANISATION=CCCMA
MODEL=CanESM2
EXPERIMENT=historicalGHG
RUN=r3i1p1
CONTROL_RUN=r1i1p1
FX_RUN=r0i0p0

# Analysis details (specific)

MAX_DEPTH=2000
START_DATE=1950-01-01
END_DATE=2000-12-31

METRIC=ohc-metrics-globe60equiv
REF=--ref_region globe60

ZM_TICK_MAX=0.0035
ZM_TICK_STEP=0.0005
VM_TICK_MAX=0.1
VM_TICK_STEP=0.02
PALETTE=BrBG_r

TARGET=${MY_CMIP5_DIR}/${ORGANISATION}/${MODEL}/${EXPERIMENT}/mon/ocean/${VAR}-maps/${RUN}/${VAR}-maps-vertical-mean_Omon_${MODEL}_${EXPERIMENT}_${RUN}_${START_DATE}_${END_DATE}.${FIG_TYPE}

