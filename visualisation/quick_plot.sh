function usage {
    echo "USAGE: bash $0 start_date end_date colour_var"
    echo "   start_date:  Start date for plot (YYYY-MM-DD)"
    echo "   end_date:    End date for plot (YYYY-MM-DD)"
    echo "   colour_var:  Variable for the colour plot (which shows the anomaly)"
    echo "   e.g. bash $0 1979-01-01 1979-01-02 pr"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

start_date=$1
end_date=$2
colour_var=$3

data_path=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data
colour_file=${data_path}/${colour_var}_ERAInterim_surface_030day-runmean-anom-wrt-all_native.nc
#contour_file=${data_path}/sf_ERAInterim_500hPa_030day-runmean-anom-wrt-all_native.nc
contour_file=${data_path}/sf_ERAInterim_500hPa_030day-runmean_native-zonal-anom.nc
contour_var=sf
outfile=quick_${colour_var}_${start_date}-${end_date}.png

if [ $colour_var == 'tas' ] ; then
    ticks="-3.0 -2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5 3.0" 
    extend=both
    palette=RdBu_r
elif [ $colour_var == 'sic' ] ; then
    ticks="-0.13 -0.11 -0.09 -0.07 -0.05 -0.03 -0.01 0.01 0.03 0.05 0.07 0.09 0.11 0.13"
    extend=both
    palette=RdBu_r
elif [ $colour_var == 'pr' ] ; then
    ticks="-1.0 -0.8 -0.6 -0.4 -0.2 0 0.2 0.4 0.6 0.8 1.0" 
    extend=both
    palette=BrBG
else
    echo "Unknown variable: $colour_var"
    exit 1
fi

if [ $contour_var == 'zg' ] ; then
    levels="-150 -120 -90 -60 -30 0 30 60 90 120 150" 
elif [ $contour_var == 'sf' ] ; then
    levels="-6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6" 
else
    echo "Unknown variable: $contour_var"
    exit 1
fi


/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_map.py ${colour_file} ${colour_var} ${start_date} ${end_date} none colour0 1 1 1 \
--infiles ${contour_file} ${contour_var} ${start_date} ${end_date} none contour0 1 \
--palette ${palette} \
--output_projection SouthPolarStereo \
--title ${start_date}_to_${end_date} \
--extend ${extend} \
--ofile ${outfile}

echo ${outfile}

#--colourbar_ticks ${ticks} \
#--contour_levels ${levels} \

