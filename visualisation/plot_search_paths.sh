
/usr/local/anaconda/bin/python plot_map.py 1 3 \
--output_projection PlateCarree_Dateline Orthographic SouthPolarStereo \
--region sh None None \
--ofile search_paths_EW.png \
--figure_size 16.0 6.5 \
--spstereo_limit -20 \
--line -10 -10 115 230 green solid RotatedPole_260E_20N low \
--line 10 10 115 230 green solid RotatedPole_260E_20N low \
--line -10 10 115 115 green solid RotatedPole_260E_20N low \
--line -10 10 230 230 green solid RotatedPole_260E_20N low \
--line -10 -10 115 230 blue solid RotatedPole_250E_20N low \
--line 10 10 115 230 blue solid RotatedPole_250E_20N low \
--line -10 10 115 115 blue solid RotatedPole_250E_20N low \
--line -10 10 230 230 blue solid RotatedPole_250E_20N low \
--line -10 -10 115 230 red solid RotatedPole_270E_20N low \
--line 10 10 115 230 red solid RotatedPole_270E_20N low \
--line -10 10 115 115 red solid RotatedPole_270E_20N low \
--line -10 10 230 230 red solid RotatedPole_270E_20N low \

/usr/local/anaconda/bin/python plot_map.py 1 3 \
--output_projection PlateCarree_Dateline Orthographic SouthPolarStereo \
--region sh None None \
--ofile search_paths_NS.png \
--figure_size 16.0 6.5 \
--spstereo_limit -20 \
--line -10 -10 115 230 green solid RotatedPole_260E_20N low \
--line 10 10 115 230 green solid RotatedPole_260E_20N low \
--line -10 10 115 115 green solid RotatedPole_260E_20N low \
--line -10 10 230 230 green solid RotatedPole_260E_20N low \
--line -10 -10 115 230 orange solid RotatedPole_260E_15N low \
--line 10 10 115 230 orange solid RotatedPole_260E_15N low \
--line -10 10 115 115 orange solid RotatedPole_260E_15N low \
--line -10 10 230 230 orange solid RotatedPole_260E_15N low \
