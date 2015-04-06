function usage {
    echo "USAGE: bash $0 contfile contvar ufile uvar vfile vvar outfile plot_type python_exe code_dir"
    echo "   contfile:    Input file for contour plot"
    echo "   contvar:     Variable for contour plot"
    echo "   ufile:       Input file name for zonal wind"
    echo "   uvar:        Variable for zonal wind"
    echo "   vfile:       Input file name for meridional wind"
    echo "   vvar:        Variable for meridional wind"
    echo "   outfile:     Output file name"
    echo "   plot_type:   quivers or streamlines"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    echo "   e.g. bash $0 zg_data.nc zg ua_data.nc ua va_data.nc va plot.png /usr/local/anaconda/bin/python ~/climate-analysis/visualisation"
    exit 1
}

nargs=10

if [ $# -ne $nargs ] ; then
  usage
fi

cfile=$1
cvar=$2
ufile=$3
uvar=$4
vfile=$5
vvar=$6
outfile=$7
plot_type=$8
python_exe=$9
code_dir=${10}
  
if [[ $cvar == 'zg' ]] ; then
    ticks="-150 -120 -90 -60 -30 0 30 60 90 120 150"     
elif [[ $cvar == 'sf' ]] ; then
    #ticks="-6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6"
    ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"
else
    echo "Unknown variable: $cvar"
    exit 1
fi



if [[ $plot_type == 'quivers' ]] ; then
    extend=both
    palette=RdBu_r
    ${python_exe} ${code_dir}/plot_map.py ${cfile} ${cvar}_annual none none none colour0 1 3 2 \
--infiles ${cfile} ${cvar}_DJF none none none colour0 3 \
--infiles ${cfile} ${cvar}_MAM none none none colour0 4 \
--infiles ${cfile} ${cvar}_JJA none none none colour0 5 \
--infiles ${cfile} ${cvar}_SON none none none colour0 6 \
--palette ${palette} \
--extend ${extend} \
--output_projection SouthPolarStereo \
--subplot_headings Annual none DJF MAM JJA SON \
--infiles ${ufile} ${uvar}_annual none none none uwind0 1 \
--infiles ${ufile} ${uvar}_DJF none none none uwind0 3 \
--infiles ${ufile} ${uvar}_MAM none none none uwind0 4 \
--infiles ${ufile} ${uvar}_JJA none none none uwind0 5 \
--infiles ${ufile} ${uvar}_SON none none none uwind0 6 \
--figure_size 9 16 \
--infiles ${vfile} ${vvar}_annual none none none vwind0 1 \
--infiles ${vfile} ${vvar}_DJF none none none vwind0 3 \
--infiles ${vfile} ${vvar}_MAM none none none vwind0 4 \
--infiles ${vfile} ${vvar}_JJA none none none vwind0 5 \
--infiles ${vfile} ${vvar}_SON none none none vwind0 6 \
--ofile ${outfile} \
--colourbar_ticks ${ticks}

elif [[ $plot_type == 'streamlines' ]] ; then
    
    ${python_exe} ${code_dir}/plot_map.py ${cfile} ${cvar}_annual none none none contour0 1 3 2 \
--infiles ${cfile} ${cvar}_DJF none none none contour0 3 \
--infiles ${cfile} ${cvar}_MAM none none none contour0 4 \
--infiles ${cfile} ${cvar}_JJA none none none contour0 5 \
--infiles ${cfile} ${cvar}_SON none none none contour0 6 \
--output_projection SouthPolarStereo \
--subplot_headings Annual none DJF MAM JJA SON \
--infiles ${ufile} ${uvar}_annual none none none uwind0 1 \
--infiles ${ufile} ${uvar}_DJF none none none uwind0 3 \
--infiles ${ufile} ${uvar}_MAM none none none uwind0 4 \
--infiles ${ufile} ${uvar}_JJA none none none uwind0 5 \
--infiles ${ufile} ${uvar}_SON none none none uwind0 6 \
--figure_size 9 16 \
--infiles ${vfile} ${vvar}_annual none none none vwind0 1 \
--infiles ${vfile} ${vvar}_DJF none none none vwind0 3 \
--infiles ${vfile} ${vvar}_MAM none none none vwind0 4 \
--infiles ${vfile} ${vvar}_JJA none none none vwind0 5 \
--infiles ${vfile} ${vvar}_SON none none none vwind0 6 \
--ofile ${outfile} \
--flow_type streamlines \
--streamline_bounds 0 30 \
--contour_levels ${ticks} \
--contour_colours 0.3


else
    echo "Unknown plot type: ${plot_type}"
    exit 1
fi
