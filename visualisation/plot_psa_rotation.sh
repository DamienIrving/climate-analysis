function usage {
    echo "USAGE: bash $0 sf_file vrot_file date outfile python_exe code_dir"
    echo "   sf_file:     Streamfunction anomaly file"
    echo "   vrot_file    Rotated meridional wind anomaly file" 
    echo "   date         Date to plot (e.g. 2006-05-18)"
    echo "   out_dir:     Directory for output file"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    exit 1
}

nargs=6

if [ $# -ne $nargs ] ; then
  usage
fi

sf_file=$1
vrot_file=$2
date=$3
out_dir=$4
python_exe=$5
code_dir=$6
  

${python_exe} ${code_dir}/plot_map.py 2 1 \
--infile ${sf_file} streamfunction ${date} ${date} none contour0 1 PlateCarree \
--infile ${vrot_file} rotated_northward_wind ${date} ${date} none colour0 2 RotatedPole_260E_20N \
--ofile ${out_dir}/rotation_example_${date}.png \
--output_projection PlateCarree_Dateline RotatedPole_260E_20N_shift180 \
--colour_type pixels \
--colourbar_ticks -10 -8 -6 -4 -2 0 2 4 6 8 10 \
--palette RdBu_r \
--line 0 0 0 359 green dashed RotatedPole_260E_20N low \
--line -10 -10 115 235 green solid RotatedPole_260E_20N low \
--line 10 10 115 235 green solid RotatedPole_260E_20N low \
--line -10 10 115 115 green solid RotatedPole_260E_20N low \
--line -10 10 235 235 green solid RotatedPole_260E_20N low \
--contour_levels -12 -9 -6 -3 0 3 6 9 12 \
--contour_colours 0.15 \
--contour_width 1.2 \
--subplot_headings streamfunction_anomaly rotated_meridional_wind_anomaly \
--no_grid_lines --figure_size 6 8 --line_width 1.5 --dpi 500
