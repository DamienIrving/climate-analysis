function usage {
    echo "USAGE: bash $0 contfile contvar ufile uvar vfile vvar boxfile date outfile plot_type python_exe code_dir"
    echo "   contfile:    Input file for contour plot"
    echo "   contvar:     Variable for contour plot"
    echo "   ufile:       Input file name for zonal wind"
    echo "   uvar:        Variable for zonal wind"
    echo "   vfile:       Input file name for meridional wind"
    echo "   vvar:        Variable for meridional wind"
    echo "   boxfile:     File with search path to plot"
    echo "   date:        Date to plot"
    echo "   outfile:     Output file name"
    echo "   plot_type:   quivers or streamlines"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    echo "   e.g. bash $0 zg_data.nc zg ua_data.nc ua va_data.nc va plot.png /usr/local/anaconda/bin/python ~/climate-analysis/visualisation"
    exit 1
}

nargs=12

if [ $# -ne $nargs ] ; then
  usage
fi

cfile=$1
cvar=$2
ufile=$3
uvar=$4
vfile=$5
vvar=$6
boxfile=$7
date=$8
outfile=$9
plot_type=${10}
python_exe=${11}
code_dir=${12}
  
if [[ $cvar == 'zg' ]] ; then
    ticks="-150 -120 -90 -60 -30 0 30 60 90 120 150"     
elif [[ $cvar == 'sf' ]] ; then
    #ticks="-6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6"
    ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"
else
    echo "Unknown variable: $cvar"
    exit 1
fi



#if [[ $plot_type == 'quivers' ]] ; then
#elif [[ $plot_type == 'streamlines' ]] ; then
#else
#    echo "Unknown plot type: ${plot_type}"
#    exit 1
#fi


${python_exe} ${code_dir}/plot_map.py 1 1 \
--output_projection PlateCarree_Dateline \
--infile ${cfile} ${cvar} ${date} ${date} none contour0 1 \
--infile ${ufile} ${uvar} ${date} ${date} none uwind0 1 \
--infile ${vfile} ${vvar} ${date} ${date} none vwind0 1 \
--ofile ${outfile} \
--subplot_headings ${date} \
--flow_type streamlines \
--contour_levels ${ticks} \
--contour_colours 0.3 \
--predefined_region sh \
--boxes ${boxfile} orange solid \
#--streamline_bounds 0 30 \


