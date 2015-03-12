/usr/local/anaconda/bin/python /home/STUDENT/dbirving/climate-analysis/visualisation/plot_map.py /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/zg-composite_zw_nino34elnino-ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean_native-zonal-anom.nc zg_annual none none none contour 1 1 1 \
--infiles /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/zg-composite_zw_nino34lanina-ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean_native-zonal-anom.nc zg_annual none none none contour 1 \
--output_projection SouthPolarStereo \
--subplot_headings Annual \
--contour_levels -150 -120 -90 -60 -30 0 30 60 90 120 150 \
--figure_size 9 16 \
--ofile test_lanina-elnino.png


#--infiles /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/zg-composite_zw_ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean_native-zonal-anom.nc zg_annual none none none contour 1 \
#--infiles /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/zg-composite_zw_nino34lanina-ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean_native-zonal-anom.nc zg_annual none none none contour 1 \

