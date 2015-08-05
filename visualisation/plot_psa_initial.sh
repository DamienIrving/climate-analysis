function usage {
    echo "USAGE: bash $0 year month day"
    echo "   year:        e.g 1984"
    echo "   month:       e.g. 06"
    echo "   day:         e.g. 26"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

year=$1
month=$2
day=$3
  
sf_ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"
vrot_ticks="-10 -8 -6 -4 -2 0 2 4 6 8 10"

date=${year}-${month}-${day}
cfile=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/sf_ERAInterim_500hPa_030day-runmean-anom-wrt-all_native.nc
clong=streamfunction
vrotfile=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/vrot_ERAInterim_500hPa_030day-runmean-anom-wrt-all_native-np20N260E.nc
vrotlong=rotated_northward_wind
ofile_sfanom=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}_sfanom.png
ofile_vrot=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}_vrot.png
ofile_hilbert=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}_hilbert-validlons.png
ofile_hilbert_all=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}_hilbert-alllons.png

echo ${ofile_sfanom}

/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_map.py 1 3 \
--output_projection PlateCarree_Dateline Orthographic SouthPolarStereo \
--infile ${cfile} ${clong} ${date} ${date} none contour0 1 PlateCarree \
--infile ${cfile} ${clong} ${date} ${date} none contour0 2 PlateCarree \
--infile ${cfile} ${clong} ${date} ${date} none contour0 3 PlateCarree \
--region sh None None \
--ofile ${ofile_sfanom} \
--title ${date} \
--contour_levels ${sf_ticks} \
--spstereo_limit -20 \
--figure_size 16.0 6.5 \
--line 0 0 115 225 green solid RotatedPole_260E_20N low

# fix required if I want high-res line

echo ${ofile_vrot}

/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_map.py 1 1 \
--output_projection RotatedPole_260E_20N_shift180 \
--infile ${vrotfile} ${vrotlong} ${date} ${date} none colour0 1 RotatedPole_260E_20N \
--ofile ${ofile_vrot} \
--title ${date} \
--line 0 0 115 225 green solid RotatedPole_260E_20N low \
--colour_type pixels \
--colourbar_ticks ${vrot_ticks} \
--palette RdBu_r \
--no_grid_lines \
--figure_size 8.0 5.0 \

# fix required if I want to use contourf
# fix required if I want high res line

#--line -10 -10 115 225 blue solid RotatedPole_260E_20N \
#--line 10 10 115 225 blue solid RotatedPole_260E_20N \
#--line -10 10 115 115 blue solid RotatedPole_260E_20N \
#--line -10 10 225 225 blue solid RotatedPole_260E_20N \

echo ${ofile_hilbert}

/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_hilbert.py ${vrotfile} vrot \
${ofile_hilbert} 1 1 --latitude 0 --dates ${date} --highlights 5 6 7 --valid_lon 115 225 

echo ${ofile_hilbert_all}

/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_hilbert.py ${vrotfile} vrot \
${ofile_hilbert_all} 1 1 --latitude 0 --dates ${date} --highlights 5 6 7 

