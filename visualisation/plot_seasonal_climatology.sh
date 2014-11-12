function usage {
    echo "USAGE: bash $0 infile var outfile"
    echo "   varfile:    Input file name for colour plot"
    echo "   var:        Variable for colour plot"
    echo "   outfile:    Output file name"
    echo "   e.g. bash $0 data.nc tas plot.png"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

varfile=$1
var=$2
outfile=$3
  

if [  $var == 'envva' ] ; then
    palette=hot_r
    ticks="0 1 2 3 4 5 6 7 8"
    extend=max
else
    echo "Unknown variable: $var"
    exit 1
fi


/usr/local/anaconda/bin/python ~/phd/visualisation/plot_map2.py ${varfile} ${var}_annual none none none colour 1 3 2 --infiles ${varfile} ${var}_DJF none none none colour 3 --infiles ${varfile} ${var}_MAM none none none colour 4 --infiles ${varfile} ${var}_JJA none none none colour 5 --infiles ${varfile} ${var}_SON none none none colour 6 --palette ${palette} --output_projection SouthPolarStereo --subplot_headings Annual none DJF MAM JJA SON --figure_size 9 16 --colourbar_ticks ${ticks} --extend ${extend} --ofile ${outfile}

