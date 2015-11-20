#
# Description: Calculate composites for various Fourier phases
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 fourier_file sf_file freq outfile psa_pos_start psa_pos_end psa_neg_start psa_neg_end" 
    echo "               min1_start min1_end min2_start min2_end python_exe code_dir vis_dir temp_dir"
    echo "   fourier_file:  Fourier transform file name"
    echo "   sf_file:       Streamfunction file"
    echo "   freq:          Frequency to filter phase against"
    echo "   outfile:       Output file name, which includes the word season which will be replaced"
    echo "   psa_pos_start  Start of PSA positive phase grouping" 
    echo "   psa_pos_end    End of PSA positive phase grouping"
    echo "   psa_neg_start  Start of PSA negative phase grouping" 
    echo "   psa_neg_end    End of PSA negative phase grouping"
    echo "   min1_start     Start of first minima phase grouping" 
    echo "   min1_end       End of first minima phase grouping"
    echo "   min2_start     Start of first minima phase grouping" 
    echo "   min2_end       End of first minima phase grouping"
    echo "   python_exe:    Python executable"
    echo "   code_dir:      Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:       Directory that plot_map.py is in"
    echo "   temp_dir:      Directory to store temporary data files"
    exit 1
}

nargs=16

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
sf_file=$2
freq=$3
outfile=$4
psa_pos_start=$5   
psa_pos_end=$6   
psa_neg_start=$7  
psa_neg_end=$8    
min1_start=$9      
min1_end=${10}       
min2_start=${11}    
min2_end=${12}       
python_exe=${13}
code_dir=${14}
vis_dir=${15}
temp_dir=${16}

temp_files=()


# Generate a date list and calculate composite for each phase range

start_phases=( ${psa_pos_start} ${min1_start} ${psa_neg_start} ${min2_start} )
end_phases=( ${psa_pos_end} ${min1_end} ${psa_neg_end} ${min2_end} )
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
--contour_levels -10.5 -9.0 -7.5 -6.0 -4.5 -3.0 -1.5 0 1.5 3.0 4.5 6.0 7.5 9.0 10.5 \
--figure_size 12 5 --region sh \
--ofile ${outfile}

rm ${temp_files[@]}
