

metrics=(value lat lon)
for metric in "${metrics[@]}"; do
  /usr/local/anaconda/bin/python ~/climate-analysis/data_processing/calc_composite.py \
  /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/indexes/asl_psl_ERAInterim_surface_030day-runmean_native.nc asl_${metric} \
  /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/asl${metric}-composite_zw_ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean-anom-wrt-all_native.nc \
  --date_file /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/dates_zw_ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean_native-mermax.txt

  /usr/local/anaconda/bin/python ~/climate-analysis/data_processing/calc_composite.py \
  /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/indexes/asl_psl_ERAInterim_surface_030day-runmean_native.nc asl_${metric} \
  /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/asl${metric}-composite_zw_ampmedian90pctinvert-w19_env-va_ERAInterim_500hPa_030day-runmean-anom-wrt-all_native.nc \
  --date_file /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/zw/figures/composites/dates_zw_ampmedian90pct-w19_env-va_ERAInterim_500hPa_030day-runmean_native-mermax.txt \
  --invert
done

