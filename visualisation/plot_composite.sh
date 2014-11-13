function usage {
    echo "USAGE: bash $0 varfile var contfile contvar outfile"
    echo "   varfile:    Input file name for colour plot"
    echo "   var:        Variable for colour plot"
    echo "   contfile:   Input file name for contour plot"
    echo "   contvar:    Variable for contour plot"
    echo "   outfile:    Output file name"
    echo "   e.g. bash $0 tas_data.nc tas zg_data.nc zg plot.png"
    exit 1
}

nargs=5

if [ $# -ne $nargs ] ; then
  usage
fi

varfile=$1
var=$2
contfile=$3
contvar=$4
outfile=$5
  

if [ $var == 'tas' ] ; then
    ticks="-3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0" 
    extend=both
    palette=RdBu_r
elif [ $var == 'envva' ] ; then
    ticks="0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0" 
    extend=max
    palette=hot_r
else
    echo "Unknown variable: $var"
    exit 1
fi

if [ $contvar == 'zg' ] ; then
    levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
else
    echo "Unknown variable: $contvar"
    exit 1
fi


/usr/local/anaconda/bin/python ~/phd/visualisation/plot_map2.py ${varfile} ${var}_annual none none none colour 1 3 2 --infiles ${varfile} ${var}_DJF none none none colour 3 --infiles ${varfile} ${var}_MAM none none none colour 4 --infiles ${varfile} ${var}_JJA none none none colour 5 --infiles ${varfile} ${var}_SON none none none colour 6 --palette ${palette} --colourbar_ticks ${ticks} --output_projection SouthPolarStereo --subplot_headings Annual none DJF MAM JJA SON --infiles ${contfile} ${contvar}_annual none none none contour 1 --infiles ${contfile} ${contvar}_DJF none none none contour 3 --infiles ${contfile} ${contvar}_MAM none none none contour 4 --infiles ${contfile} ${contvar}_JJA none none none contour 5 --infiles ${contfile} ${contvar}_SON none none none contour 6 --contour_levels ${levels} --figure_size 9 16 --extend ${extend} --ofile ${outfile}

