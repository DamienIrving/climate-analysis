# wisconsin_composites.mk
#
# Description: Workflow to create composites for CMMT study
#
# To execute:
#   make -n -B -f wisconsin_composites.mk  (-n is a dry run) (-B is a force make)
#

all : /g/data/r87/dbi599/figures/wisconsin/sf-hus-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_wilkes.png
REGION=wilkes
# ellsworth, enderby, marie-byrd, queen-mary, queen-maud, victoria, wilkes
TITLE=Wilkes_Land
# Ellsworth_Land, Enderby_Land, Marie_Byrd_Land, Queen_Mary_Coast, Queen_Maud_Land, Victoria_Land, Wilkes_Land   



DATA_DIR=/g/data/r87/dbi599/data_eraint/wisconsin_cmmt
VIS_DIR=/home/599/dbi599/climate-analysis/visualisation
PROCESSING_DIR=/home/599/dbi599/climate-analysis/data_processing
WISCONSIN_DIR=/home/599/dbi599/climate-analysis/downloads/wisconsin
PYTHON=/g/data/r87/dbi599/miniconda2/envs/wisconsin/bin/python

DATE_DATA=${WISCONSIN_DIR}/${REGION}_CMMTdatetimes.csv
SF_DATA=${DATA_DIR}/sf_eraint_500hPa_daily-anom-wrt-all_native-reoriented.nc
HUS_DATA=${DATA_DIR}/hus_eraint_500hPa_daily-anom-wrt-all_native-reoriented.nc
UA_DATA=${DATA_DIR}/ua_eraint_500hPa_daily_native-reoriented.nc
VA_DATA=${DATA_DIR}/va_eraint_500hPa_daily_native-reoriented.nc

DATE_LIST=${DATA_DIR}/${REGION}_CMMTdatetimes.txt
${DATE_LIST} : 
	${PYTHON} ${WISCONSIN_DIR}/cmmt_date_list.py ${DATE_DATA} $@

SF_COMPOSITE=${DATA_DIR}/sf-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_${REGION}.nc
${SF_COMPOSITE} : ${DATE_LIST}
	${PYTHON} ${PROCESSING_DIR}/calc_composite.py ${SF_DATA} sf $@ --date_file $< --no_sig

HUS_COMPOSITE=${DATA_DIR}/hus-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_${REGION}.nc
${HUS_COMPOSITE} : ${DATE_LIST}
	${PYTHON} ${PROCESSING_DIR}/calc_composite.py ${HUS_DATA} hus $@ --date_file $< --no_sig

UA_COMPOSITE=${DATA_DIR}/ua-composite_eraint_500hPa_daily_native-reoriented_${REGION}.nc
${UA_COMPOSITE} : ${DATE_LIST}
	${PYTHON} ${PROCESSING_DIR}/calc_composite.py ${UA_DATA} ua $@ --date_file $< --no_sig

VA_COMPOSITE=${DATA_DIR}/va-composite_eraint_500hPa_daily_native-reoriented_${REGION}.nc
${VA_COMPOSITE} : ${DATE_LIST}
	${PYTHON} ${PROCESSING_DIR}/calc_composite.py ${VA_DATA} va $@ --date_file $< --no_sig

COMPOSITE_PLOT=/g/data/r87/dbi599/figures/wisconsin/sf-hus-composite_eraint_500hPa_daily-anom-wrt-all_native-reoriented_${REGION}.png
${COMPOSITE_PLOT} : ${SF_COMPOSITE} ${HUS_COMPOSITE} ${UA_COMPOSITE} ${VA_COMPOSITE}
	${PYTHON} ${VIS_DIR}/plot_map.py 3 2 --infile $(word 1,$^) streamfunction_annual none none none contour0 1 PlateCarree --infile $(word 1,$^) streamfunction_DJF none none none contour0 3 PlateCarree --infile $(word 1,$^) streamfunction_MAM none none none contour0 4 PlateCarree --infile $(word 1,$^) streamfunction_JJA none none none contour0 5 PlateCarree --infile $(word 1,$^) streamfunction_SON none none none contour0 6 PlateCarree --output_projection SouthPolarStereo --subplot_headings Annual none DJF MAM JJA SON --infile $(word 2,$^) specific_humidity_annual none none none colour0 1 PlateCarree --infile $(word 2,$^) specific_humidity_DJF none none none colour0 3 PlateCarree --infile $(word 2,$^) specific_humidity_MAM none none none colour0 4 PlateCarree --infile $(word 2,$^) specific_humidity_JJA none none none colour0 5 PlateCarree --infile $(word 2,$^) specific_humidity_SON none none none colour0 6 PlateCarree --infile $(word 3,$^) eastward_wind_annual none none none uwind0 1 PlateCarree --infile $(word 3,$^) eastward_wind_DJF none none none uwind0 3 PlateCarree --infile $(word 3,$^) eastward_wind_MAM none none none uwind0 4 PlateCarree --infile $(word 3,$^) eastward_wind_JJA none none none uwind0 5 PlateCarree --infile $(word 3,$^) eastward_wind_SON none none none uwind0 6 PlateCarree --figure_size 9 16 --infile $(word 4,$^) northward_wind_annual none none none vwind0 1 PlateCarree --infile $(word 4,$^) northward_wind_DJF none none none vwind0 3 PlateCarree --infile $(word 4,$^) northward_wind_MAM none none none vwind0 4 PlateCarree --infile $(word 4,$^) northward_wind_JJA none none none vwind0 5 PlateCarree --infile $(word 4,$^) northward_wind_SON none none none vwind0 6 PlateCarree --flow_type streamlines --contour_levels -20 -19 -18 -17 -16 -15 -14 -13 -12 -11 -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 --exclude_blanks --streamline_colour 0.7 --palette BrBG --colourbar_ticks -0.00020 -0.00016 -0.00012 -0.00008 -0.00004 0 0.00004 0.00008 0.00012 0.00016 0.00020 --extend both --units kgkg-1 --title ${TITLE} --ofile ${COMPOSITE_PLOT} 


