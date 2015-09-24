function usage {
    echo "USAGE: bash $0 eoffile outfile python_exe code_dir"
    echo "   eoffile:     Input file name"
    echo "   outfile:     Output file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    exit 1
}

nargs=4

if [ $# -ne $nargs ] ; then
  usage
fi

infile=$1
outfile=$2
python_exe=$3
code_dir=$4
  

${python_exe} ${code_dir}/plot_map.py 2 2 \
--infile ${infile} empirical_orthogonal_function_1 none none none colour0 1 PlateCarree \
--infile ${infile} empirical_orthogonal_function_2 none none none colour0 2 PlateCarree \
--infile ${infile} empirical_orthogonal_function_3 none none none colour0 3 PlateCarree \
--infile ${infile} empirical_orthogonal_function_4 none none none colour0 4 PlateCarree \
--palette RdBu_r \
--subplot_headings EOF_1 EOF_2 EOF_3 EOF_4 \
--figure_size 10 5 \
--ofile ${outfile} \
--region sh \
--units correlation \
--colourbar_ticks -1 -0.8 -0.6 -0.4 -0.2 0 0.2 0.4 0.6 0.8 1.0 \
--line -10 -10 115 235 green solid RotatedPole_260E_20N low \
--line 10 10 115 235 green solid RotatedPole_260E_20N low \
--line -10 10 115 115 green solid RotatedPole_260E_20N low \
--line -10 10 235 235 green solid RotatedPole_260E_20N low \

#--output_projection SouthPolarStereo \
