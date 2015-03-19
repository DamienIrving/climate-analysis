function usage {
    echo "USAGE: bash $0 zgfile zgvar contfile contvar outfile python_exe code_dir"
    echo "   zgfile:      Input file for zg zonal anomaly"
    echo "   zgvar:       Variable for zg zonal anomaly"
    echo "   ufile:       Input file name for zonal wind"
    echo "   uvar:        Variable for zonal wind"
    echo "   vfile:       Input file name for meridional wind"
    echo "   vvar:        Variable for meridional wind"
    echo "   outfile:     Output file name"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    echo "   e.g. bash $0 zg_data.nc zg ua_data.nc ua va_data.nc va plot.png /usr/local/anaconda/bin/python ~/climate-analysis/visualisation"
    exit 1
}

nargs=9

if [ $# -ne $nargs ] ; then
  usage
fi

zgfile=$1
zgvar=$2
ufile=$3
uvar=$4
vfile=$5
vvar=$6
outfile=$7
python_exe=$8
code_dir=$9
  

ticks="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
extend=both
palette=RdBu_r

${python_exe} ${code_dir}/plot_map.py ${zgfile} ${zgvar}_annual none none none colour0 1 3 2 \
--infiles ${zgfile} ${zgvar}_DJF none none none colour0 3 \
--infiles ${zgfile} ${zgvar}_MAM none none none colour0 4 \
--infiles ${zgfile} ${zgvar}_JJA none none none colour0 5 \
--infiles ${zgfile} ${zgvar}_SON none none none colour0 6 \
--palette ${palette} \
--colourbar_ticks ${ticks} \
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
