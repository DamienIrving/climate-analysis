function usage {
    echo "USAGE: bash $0 sffile sflong vrotfile vrotlong vrotvar outdir python_exe code_dir"
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

# bash plot_psa_check.sh sffile.nc streamfunction vrotfile.nc rotated_northward_wind vrot 
# /mnt/meteo0/data/simmonds/dbirving/ERAInterim/data/psa/figures/maps/ /usr/local/anaconda/bin/python 
# ~/climate-analysis/visualisation


nargs=8

if [ $# -ne $nargs ] ; then
  usage
fi

sffile=$1
sflong=$2
vrotfile=$3
vrotlong=$4
vrotvar=$5
outdir=$6
python_exe=$7
code_dir=$8
  
sf_ticks="-12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5"
vrot_ticks="-10 -8 -6 -4 -2 0 2 4 6 8 10"


years=(2000 2005 2006)

months=(01 02 03 04 05 06 07 08 09 10 11 12)

days=(02 06 10 14 18 22 26)

for year in "${years[@]}"; do
    mkdir -p ${outdir}/${year}_10S-10N
    for month in "${months[@]}"; do
        for day in "${days[@]}"; do

            date=${year}-${month}-${day}

            ofile_sfanom=${outdir}/${year}_10S-10N/psa_check_${date}_10S-10N_sfanom.png
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
	    --line -10 -10 115 230 green solid RotatedPole_260E_20N low \
	    --line 10 10 115 230 green solid RotatedPole_260E_20N low \
	    --line -10 10 115 115 green solid RotatedPole_260E_20N low \
	    --line -10 10 230 230 green solid RotatedPole_260E_20N low 

	    # fix required if I want high-res line

            ofile_vrot=${outdir}/${year}_10S-10N/psa_check_${date}_10S-10N_vrot.png
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
	    --line -10 -10 115 230 green solid RotatedPole_260E_20N low \
	    --line 10 10 115 230 green solid RotatedPole_260E_20N low \
	    --line -10 10 115 115 green solid RotatedPole_260E_20N low \
	    --line -10 10 230 230 green solid RotatedPole_260E_20N low 

	    # fix required if I want to use contourf
	    # fix required if I want high res line

            ofile_hilbert=${outdir}/${year}_10S-10N/psa_check_${date}_10S-10N_hilbert.png
	    echo ${ofile_hilbert}

	    ${python_exe} ${code_dir}/plot_hilbert.py ${vrotfile} ${vrotvar} \
	    ${ofile_hilbert} 1 1 --latitude -10 10 --dates ${date} --highlights 5 6 7 --valid_lon 115 230 --periodogram
	    
        done
    done
done

