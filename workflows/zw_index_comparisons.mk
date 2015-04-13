# zw_index_comparisons.mk
#
# Description: Compare various indices
#
# To execute:
#   make -n -B -f zw_index_comparisons.mk  (-n is a dry run) (-B is a force make)

# Define marcos
include zw_config.mk
include zw_base.mk

all : ${TARGET}


# MI vs ZW3 index

PWI_VS_ZW3_PLOT=${INDEX_DIR}/pwi-vs-zw3index_${DATASET}_${LEVEL}_${TSCALE_LABEL}_native.png
${PWI_VS_ZW3_PLOT} : ${PWI_INDEX} ${ZW3_INDEX} ${FOURIER_INFO}
	${PYTHON} ${VIS_SCRIPT_DIR}/plot_scatter.py $(word 1,$^) pwi $(word 2,$^) zw3 $@ --colour $(word 3,$^) wave3_phase --normalise --trend_line --zero_lines --thin 3 --cmap jet --ylabel ZW3_index --xlabel Planetary_Wave_Index --clat ${LAT_SINGLE} ${LAT_SINGLE} none


