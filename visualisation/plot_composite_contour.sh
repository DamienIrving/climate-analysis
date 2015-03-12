function usage {
    echo "USAGE: bash $0 contfile contvar outfile python_exe code_dir"
    echo "   contfile:    Input file name for contour plot"
    echo "   contvar:     Variable for contour plot"
    echo "   outfile:     Output file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    echo "   e.g. bash $0 zg_data.nc zg plot.png /usr/local/anaconda/bin/python ~/climate-analysis/visualisation/"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

contfile=$1
contvar=$2
outfile=$3
python_exe=$4
code_dir=$5
  

if [ $contvar == 'zg' ] ; then
    levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
else
    echo "Unknown variable: $contvar"
    exit 1
fi


${python_exe} ${code_dir}/plot_map.py ${contfile} ${contvar}_annual none none none contour0 1 3 2 \
--output_projection SouthPolarStereo \
--subplot_headings Annual none DJF MAM JJA SON \
--infiles ${contfile} ${contvar}_DJF none none none contour0 3 \
--infiles ${contfile} ${contvar}_MAM none none none contour0 4 \
--infiles ${contfile} ${contvar}_JJA none none none contour0 5 \
--infiles ${contfile} ${contvar}_SON none none none contour0 6 \
--contour_levels ${levels} \
--figure_size 9 16 \
--ofile ${outfile} \
--boxes zw31 blue solid \
--boxes zw32 blue solid \
--boxes zw33 blue solid

