function usage {
    echo "USAGE: bash $0 posfile neutralfile negfile var outfile python_exe code_dir"
    echo "   posfile:       Input file name for positive phase contours"
    echo "   neutralfile:   Input file name for neutral phase contours"
    echo "   negfile:       Input file name for negative phase contours"
    echo "   var:           Contour variable"
    echo "   outfile:       Output file name"
    echo "   python_exe:    Python executable"
    echo "   code_dir:      Directory that plot_map.py is in"
    echo "   e.g. bash $0 pos_contour.nc neutral_contour.nc neg_contour.nc zg plot.png /usr/local/anaconda/bin/python ~/climate-analysis/visualisation"
    exit 1
}

nargs=7

if [ $# -ne $nargs ] ; then
  usage
fi

posfile=$1
neutralfile=$2
negfile=$3
var=$4
outfile=$5
python_exe=$6
code_dir=$7
  
if [ $var == 'zg' ] ; then
    levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
elif [[ $var == 'sf' ]] ; then
    levels="-6 -4.5 -3 -1.5 0 1.5 3 4.5 6"
else
    echo "Unknown variable: $var"
    exit 1
fi

${python_exe} ${code_dir}/plot_map.py ${posfile} ${var}_annual none none none contour0 1 3 2 \
--infiles ${posfile} ${var}_DJF none none none contour0 3 \
--infiles ${posfile} ${var}_MAM none none none contour0 4 \
--infiles ${posfile} ${var}_JJA none none none contour0 5 \
--infiles ${posfile} ${var}_SON none none none contour0 6 \
--output_projection SouthPolarStereo \
--subplot_headings Annual none DJF MAM JJA SON \
--infiles ${neutralfile} ${var}_annual none none none contour1 1 \
--infiles ${neutralfile} ${var}_DJF none none none contour1 3 \
--infiles ${neutralfile} ${var}_MAM none none none contour1 4 \
--infiles ${neutralfile} ${var}_JJA none none none contour1 5 \
--infiles ${neutralfile} ${var}_SON none none none contour1 6 \
--infiles ${negfile} ${var}_annual none none none contour2 1 \
--infiles ${negfile} ${var}_DJF none none none contour2 3 \
--infiles ${negfile} ${var}_MAM none none none contour2 4 \
--infiles ${negfile} ${var}_JJA none none none contour2 5 \
--infiles ${negfile} ${var}_SON none none none contour2 6 \
--contour_levels ${levels} \
--figure_size 9 16 \
--ofile ${outfile} \
--contour_colours red 0.5 blue
