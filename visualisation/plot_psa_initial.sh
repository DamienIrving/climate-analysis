function usage {
    echo "USAGE: bash $0 year month day"
    echo "   year:        e.g 1984"
    echo "   month:       e.g. 06"
    echo "   ufile:       Input file name for zonal wind"
    exit 1
}

nargs=3

if [ $# -ne $nargs ] ; then
  usage
fi

year=$1
month=$2
day=$3
  
ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"

date=${year}-${month}-${day}
cfile=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/
cvar=sf
vrotfile=
vrotlong=rotated_northward_wind
ofile_spatial=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}_spatial.png
ofile_hilbert=/mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/${year}/psa_check_${date}_hilbert.png

/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_map.py 2 2 \
--output_projection PlateCarree_Dateline Orthographic SouthPolarStereo RotatedPole_260E_20N_shift180 \
--infile ${cfile} ${cvar} ${date} ${date} none contour0 1 PlateCarree \
--infile ${cfile} ${cvar} ${date} ${date} none contour0 2 PlateCarree \
--infile ${cfile} ${cvar} ${date} ${date} none contour0 3 PlateCarree \
--infile ${vrotfile} ${vrotlong} ${date} ${date} none contour0 4 RotatedPole_260E_20N \
--region sh None None None
--ofile ${ofile} \
--title ${date} \
--contour_levels ${ticks} \
--contour_colours 0.3 \
--spstereo_limit -20 \
--figure_size 16.0 6.5 \
--line 0 0 115 225 blue solid RotatedPole_260E_20N \

#--line -10 -10 115 225 blue solid RotatedPole_260E_20N \
#--line 10 10 115 225 blue solid RotatedPole_260E_20N \
#--line -10 10 115 115 blue solid RotatedPole_260E_20N \
#--line -10 10 225 225 blue solid RotatedPole_260E_20N \

/usr/local/anaconda/bin/python ~/climate-analysis/visualisation/plot_hilbert.py 

