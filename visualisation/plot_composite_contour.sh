function usage {
    echo "USAGE: bash $0 contfile contvar outfile"
    echo "   contfile:   Input file name for contour plot"
    echo "   contvar:    Variable for contour plot"
    echo "   outfile:    Output file name"
    echo "   e.g. bash $0 zg_data.nc zg plot.png"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

contfile=$1
contvar=$2
outfile=$3
  

if [ $contvar == 'zg' ] ; then
    levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
else
    echo "Unknown variable: $contvar"
    exit 1
fi


/usr/local/anaconda/bin/python ~/phd/visualisation/plot_map2.py ${contfile} ${contvar}_annual none none none contour 1 3 2 --output_projection SouthPolarStereo --subplot_headings Annual none DJF MAM JJA SON --infiles ${contfile} ${contvar}_DJF none none none contour 3 --infiles ${contfile} ${contvar}_MAM none none none contour 4 --infiles ${contfile} ${contvar}_JJA none none none contour 5 --infiles ${contfile} ${contvar}_SON none none none contour 6 --contour_levels ${levels} --figure_size 9 16 --ofile ${outfile} --boxes zw31 blue solid --boxes zw32 blue solid --boxes zw33 blue solid 

