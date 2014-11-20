function usage {
    echo "USAGE: bash $0 varfile var contfile contvar date outfile"
    echo "   envfile:    Input file name for colour plot"
    echo "   var:        Variable for colour plot"
    echo "   contfile:   Input file name for contour plot"
    echo "   contvar:    Variable for contour plot"
    echo "   outfile:    Output file name"
    echo "   date:       Date to plot"
    echo "   e.g. bash $0 env_data.nc env zg_data.nc zg 2002-10-25 plot.png"
    exit 1
}

nargs=6

if [ $# -ne $nargs ] ; then
  usage
fi

envfile=$1
var=$2
contfile=$3
contvar=$4
date=$5
outfile=$6
  

#ticks="0 1.0 2.0 3.0 4.0 5.0 6.0 7.0 8.0 9.0 10.0" 
#extend=max
palette=hot_r
#levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 


echo /usr/local/anaconda/bin/python ~/phd/visualisation/plot_map2.py ${envfile} ${var} ${date} ${date} none colour 1 1 1 --palette ${palette} --output_projection SouthPolarStereo --subplot_headings ${date} --infiles ${contfile} ${contvar} ${date} ${date} none contour 1 --ofile ${outfile} --contour_labels

#--colourbar_ticks ${ticks}
#--figure_size 9 16 --extend ${extend}
