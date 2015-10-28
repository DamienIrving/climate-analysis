#
# Description: Calculate composites for various Fourier phases
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 fourier_file sf_file freq outfile python_exe code_dir vis_dir temp_dir"
    echo "   fourier_file: Fourier transform file name"
    echo "   sf_file:      Streamfunction file"
    echo "   freq:         Frequency to filter phase against"
    echo "   outfile:      Output file name, which includes the word season which will be replaced"
    echo "   python_exe:   Python executable"
    echo "   code_dir:     Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:      Directory that plot_map.py is in"
    echo "   temp_dir:     Directory to store temporary data files"
    exit 1
}

nargs=8

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
sf_file=$2
freq=$3
outfile=$4
python_exe=$5
code_dir=$6
vis_dir=$7
temp_dir=$8

temp_files=()


# Generate a date list and calculate composite for each phase range

start_phases=( 4.5 22.5 37.5 50.25 )
end_phases=( 19.5 37.5 52.5 6.0 )
for idx in "${!start_phases[@]}"; do
    
    start_phase=${start_phases[$idx]}
    end_phase=${end_phases[$idx]}
    
    temp_date_file=${temp_dir}/dates_phase${idx}.txt
    temp_sfcomp_file=${temp_dir}/sf-composite_phase${idx}.nc
    
    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${code_dir}/calc_composite.py ${sf_file} sf ${temp_sfcomp_file} \
    --date_file ${temp_date_file} --region sh --no_sig
    
    temp_files+=(${temp_date_file} ${temp_sfcomp_file})
done

# Generate the plot

${python_exe} ${vis_dir}/plot_map.py 2 2 \
--output_projection PlateCarree_Dateline --subplot_headings positive_PSA minima_1 negative_PSA minima_2 \
--infile ${temp_dir}/sf-composite_phase0.nc streamfunction_annual none none none contour0 1 PlateCarree \
--infile ${temp_dir}/sf-composite_phase1.nc streamfunction_annual none none none contour0 2 PlateCarree \
--infile ${temp_dir}/sf-composite_phase2.nc streamfunction_annual none none none contour0 3 PlateCarree \
--infile ${temp_dir}/sf-composite_phase3.nc streamfunction_annual none none none contour0 4 PlateCarree \
--contour_levels -12 -10 -8 -6 -4 -2 0 2 4 6 8 10 12 \
--figure_size 12 5 --region sh \
--ofile ${outfile}

rm ${temp_files[@]}
