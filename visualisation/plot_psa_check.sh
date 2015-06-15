function usage {
    echo "USAGE: bash $0 contfile contvar ufile uvar vfile vvar python_exe code_dir"
    echo "   contfile:    Input file for contour plot"
    echo "   contvar:     Variable for contour plot"
    echo "   ufile:       Input file name for zonal wind"
    echo "   uvar:        Variable for zonal wind"
    echo "   vfile:       Input file name for meridional wind"
    echo "   vvar:        Variable for meridional wind"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    echo "   e.g. bash $0 zg_data.nc zg ua_data.nc ua va_data.nc va box.txt /usr/local/anaconda/bin/python ~/climate-analysis/visualisation"
    exit 1
}

# bash plot_psa_check.sh /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/sf_ERAInterim_500hPa_030day-runmean-anom-wrt-all_native.nc sf /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/ua_ERAInterim_500hPa_030day-runmean_native.nc ua /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/va_ERAInterim_500hPa_030day-runmean_native.nc va /usr/local/anaconda/bin/python ~/climate-analysis/visualisation


nargs=8

if [ $# -ne $nargs ] ; then
  usage
fi

cfile=$1
cvar=$2
ufile=$3
uvar=$4
vfile=$5
vvar=$6
python_exe=$7
code_dir=$8
  
if [[ $cvar == 'zg' ]] ; then
    ticks="-150 -120 -90 -60 -30 0 30 60 90 120 150"     
elif [[ $cvar == 'sf' ]] ; then
    #ticks="-6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6"
    ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"
else
    echo "Unknown variable: $cvar"
    exit 1
fi


years=(2005)    
#years=(2005 2006)

months=(01)
#months=(01 02 03 04 05 06 07 08 09 10 11 12)

days=(02 07)
#days=(02 07 12 17 22 27)

for year in "${years[@]}"; do
    for month in "${months[@]}"; do
        for day in "${days[@]}"; do

            date=${year}-${month}-${day}
            ofile=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}.png

	    ${python_exe} ${code_dir}/plot_map.py 1 3 \
	    --output_projection PlateCarree_Dateline Orthographic SouthPolarStereo \
	    --infile ${cfile} ${cvar} ${date} ${date} none contour0 1 \
            --infile ${cfile} ${cvar} ${date} ${date} none contour0 2 \
            --infile ${cfile} ${cvar} ${date} ${date} none contour0 3 \
	    --ofile ${ofile} \
	    --title ${date} \
	    --contour_levels ${ticks} \
	    --contour_colours 0.3 \
            --line -10 -10 115 225 blue solid RotatedPole_260E_20N \
            --line 10 10 115 225 blue solid RotatedPole_260E_20N \
            --line -10 10 115 115 blue solid RotatedPole_260E_20N \
            --line -10 10 225 225 blue solid RotatedPole_260E_20N \
            --spstereo_limit -20 \
            --figure_size 16.0 6.5 \
            --region sh None None
            
            echo ${ofile}
	    
        done
    done
done

#	    --infile ${ufile} ${uvar} ${date} ${date} none uwind0 1 \
#	    --infile ${vfile} ${vvar} ${date} ${date} none vwind0 1 \
#           --flow_type streamlines \
