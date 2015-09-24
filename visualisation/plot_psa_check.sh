function usage {
    echo "USAGE: bash $0 dates sffile sflong vrotfile vrotlong vrotvar outdir python_exe code_dir"
    echo "   dates:       File containing the list of dates to plot"
    echo "   sffile:      Streamfunction input file for contour plot"
    echo "   sflong:      Streamfunction long name for contour plot"
    echo "   vrotfile:    Rotated meridional wind input file name"
    echo "   vrotlong:    Rotated meridional wind long name"
    echo "   vrotvar:     Rotated meridional wind variable name"
    echo "   outdir:      Directory for output files"
    echo "   python_exe:  Python executable"
    echo "   code_dir:    Directory that plot_map.py is in"
    exit 1
}

# bash plot_psa_check.sh datefile.txt sffile.nc streamfunction vrotfile.nc rotated_northward_wind vrot 
# /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/ /usr/local/anaconda/bin/python 
# ~/climate-analysis/visualisation


nargs=9

if [ $# -ne $nargs ] ; then
  usage
fi

datefile=$1
sffile=$2
sflong=$3
vrotfile=$4
vrotlong=$5
vrotvar=$6
outdir=$7
python_exe=$8
code_dir=$9
  
sf_ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"
vrot_ticks="-10 -8 -6 -4 -2 0 2 4 6 8 10"


while IFS= read -r datetime; do
 
    date=`echo ${datetime} | cut -d 'T' -f 1`
    year=`echo ${date} | cut -d '-' -f 1`

    yroutdir=${outdir}/${year}_10S-10N_PSAactive
    mkdir -p ${yroutdir}

    ofile_sfanom=${yroutdir}/psa_check_${date}_10S-10N_sfanom.png
    echo ${ofile_sfanom}

    ${python_exe} ${code_dir}/plot_map.py 1 3 \
    --output_projection PlateCarree_Dateline Orthographic SouthPolarStereo \
    --infile ${sffile} ${sflong} ${date} ${date} none contour0 1 PlateCarree \
    --infile ${sffile} ${sflong} ${date} ${date} none contour0 2 PlateCarree \
    --infile ${sffile} ${sflong} ${date} ${date} none contour0 3 PlateCarree \
    --region sh None None \
    --ofile ${ofile_sfanom} \
    --title ${date} \
    --contour_levels ${sf_ticks} \
    --spstereo_limit -20 \
    --figure_size 16.0 6.5 \
    --line -10 -10 115 235 green solid RotatedPole_260E_20N low \
    --line 10 10 115 235 green solid RotatedPole_260E_20N low \
    --line -10 10 115 115 green solid RotatedPole_260E_20N low \
    --line -10 10 235 235 green solid RotatedPole_260E_20N low 

    # fix required if I want high-res line

    ofile_vrot=${yroutdir}/psa_check_${date}_10S-10N_vrot.png
    echo ${ofile_vrot}

    ${python_exe} ${code_dir}/plot_map.py 1 1 \
    --output_projection RotatedPole_260E_20N_shift180 \
    --infile ${vrotfile} ${vrotlong} ${date} ${date} none colour0 1 RotatedPole_260E_20N \
    --ofile ${ofile_vrot} \
    --title ${date} \
    --colour_type pixels \
    --colourbar_ticks ${vrot_ticks} \
    --palette RdBu_r \
    --no_grid_lines \
    --figure_size 8.0 5.0 \
    --line -10 -10 115 235 green solid RotatedPole_260E_20N low \
    --line 10 10 115 235 green solid RotatedPole_260E_20N low \
    --line -10 10 115 115 green solid RotatedPole_260E_20N low \
    --line -10 10 235 235 green solid RotatedPole_260E_20N low 

    # fix required if I want to use contourf
    # fix required if I want high res line

    ofile_hilbert=${yroutdir}/psa_check_${date}_10S-10N_hilbert.png
    echo ${ofile_hilbert}

    ${python_exe} ${code_dir}/plot_hilbert.py ${vrotfile} ${vrotvar} \
    ${ofile_hilbert} 1 1 --latitude -10 10 --dates ${date} --highlights 4 5 6 7 --valid_lon 115 235 \
    --periodogram --wavenumbers 1 8 --envelope 4 7

done < "${datefile}"

