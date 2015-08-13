/usr/local/anaconda/bin/python plot_map.py 2 3 \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w5-phase08-18_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 1 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w5-phase42-52_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 2 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w5-phase62-70_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 3 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w5-phase08-18_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 4 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w5-phase42-52_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 5 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w5-phase62-70_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 6 PlateCarree \
--contour_levels -9 -7.5 -6 -4.5 -3 -1.5 0 1.5 3 4.5 6 7.5 9 \
--ofile  /mnt/meteo0/data/simmonds/dbirving/temp/sf-composite_wave5.png \
--subplot_headings phase_8_to_18 phase_42_to_52 phase_62_to_70 phase_8_to_18 phase_42_to_52 phase_62_to_70 \
--figure_size 16 9 \
--output_projection PlateCarree_Dateline PlateCarree_Dateline PlateCarree_Dateline SouthPolarStereo SouthPolarStereo SouthPolarStereo


/usr/local/anaconda/bin/python plot_map.py 2 2 \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w6-phase03-13_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 1 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w6-phase40-50_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 2 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w6-phase03-13_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 3 PlateCarree \
--infile /mnt/meteo0/data/simmonds/dbirving/temp/sf-psa-w6-phase40-50_ERAInterim_500hPa-lat10S10Nmean-lon115E230Ezeropad_030day-runmean-anom-wrt-all_native-np20N260E.nc streamfunction_JJA none none none contour0 4 PlateCarree \
--contour_levels -9 -7.5 -6 -4.5 -3 -1.5 0 1.5 3 4.5 6 7.5 9 \
--ofile  /mnt/meteo0/data/simmonds/dbirving/temp/sf-composite_wave6.png \
--subplot_headings phase_3_to_13 phase_40_to_50 phase_3_to_13 phase_40_to_50 \
--figure_size 16 9 \
--output_projection PlateCarree_Dateline PlateCarree_Dateline SouthPolarStereo SouthPolarStereo
