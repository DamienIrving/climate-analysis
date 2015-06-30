function usage {
    echo "USAGE: bash $0 posfile neutralfile negfile var outfile seasons python_exe code_dir"
    echo "   posfile:       Input file name for positive phase contours"
    echo "   neutralfile:   Input file name for neutral phase contours"
    echo "   negfile:       Input file name for negative phase contours"
    echo "   var:           Contour variable"
    echo "   outfile:       Output file name"
    echo "   seasons:       Can plot all or just annual"
    echo "   python_exe:    Python executable"
    echo "   code_dir:      Directory that plot_map.py is in"
    echo "   e.g. bash $0 pos_contour.nc neutral_contour.nc neg_contour.nc zg plot.png /usr/local/anaconda/bin/python ~/climate-analysis/visualisation"
    exit 1
}

nargs=8

if [ $# -ne $nargs ] ; then
  usage
fi

posfile=$1
neutralfile=$2
negfile=$3
var=$4
outfile=$5
seasons=$6
python_exe=$7
code_dir=$8
  
if [[ $var == 'zg' ]] ; then
    levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
elif [[ $var == 'sf' ]] ; then
    levels="-20 -16 -12 -8 -4 0 4 8 12 16 20"
else
    echo "Unknown variable: $var"
    exit 1
fi


if [[ $seasons == 'all' ]] ; then

    ${python_exe} ${code_dir}/plot_map.py 3 2 \
    --infile ${posfile} ${var}_annual none none none contour0 1 \
    --infile ${posfile} ${var}_DJF none none none contour0 3 \
    --infile ${posfile} ${var}_MAM none none none contour0 4 \
    --infile ${posfile} ${var}_JJA none none none contour0 5 \
    --infile ${posfile} ${var}_SON none none none contour0 6 \
    --output_projection SouthPolarStereo \
    --subplot_headings Annual none DJF MAM JJA SON \
    --infile ${neutralfile} ${var}_annual none none none contour1 1 \
    --infile ${neutralfile} ${var}_DJF none none none contour1 3 \
    --infile ${neutralfile} ${var}_MAM none none none contour1 4 \
    --infile ${neutralfile} ${var}_JJA none none none contour1 5 \
    --infile ${neutralfile} ${var}_SON none none none contour1 6 \
    --infile ${negfile} ${var}_annual none none none contour2 1 \
    --infile ${negfile} ${var}_DJF none none none contour2 3 \
    --infile ${negfile} ${var}_MAM none none none contour2 4 \
    --infile ${negfile} ${var}_JJA none none none contour2 5 \
    --infile ${negfile} ${var}_SON none none none contour2 6 \
    --contour_levels ${levels} \
    --figure_size 9 16 \
    --ofile ${outfile} \
    --contour_colours red 0.5 blue

elif [[ $seasons == 'annual' ]] ; then

    ${python_exe} ${code_dir}/plot_map.py 1 1 \
    --infile ${posfile} ${var}_annual none none none contour0 1 \
    --output_projection SouthPolarStereo \
    --infile ${negfile} ${var}_annual none none none contour1 1 \
    --contour_levels ${levels} \
    --ofile ${outfile} \
    --contour_colours 0.7 black

else
    echo "Unknown season: $seasons"
    exit 1
fi
