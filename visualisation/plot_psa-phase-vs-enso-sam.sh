#
# Description: Create ENSO/SAM scatter plots for various phase ranges
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 sam_file enso_file enso_var fourier_file freq outfile psa_pos_start psa_pos_end psa_neg_start psa_neg_end python_exe code_dir vis_dir temp_dir"
    echo "   sam_file:      SAM file"
    echo "   enso_file:     ENSO file"
    echo "   enso_var:      ENSO variable"
    echo "   fourier_file:  Fourier transform file name"
    echo "   freq:          Frequency to filter phase against"
    echo "   outfile:       Output file name, which includes the word phase-range which will be replaced"
    echo "   psa_pos_start  Start of PSA positive phase grouping" 
    echo "   psa_pos_end    End of PSA positive phase grouping"
    echo "   psa_neg_start  Start of PSA negative phase grouping" 
    echo "   psa_neg_end    End of PSA negative phase grouping"
    echo "   python_exe:    Python executable"
    echo "   code_dir:      Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:       Directory that plot_map.py is in"
    echo "   temp_dir:      Directory to store temporary data files"
    exit 1
}

nargs=14

if [ $# -ne $nargs ] ; then
  usage
fi

sam_file=$1
enso_file=$2
enso_var=$3
fourier_file=$4
freq=$5
outfile=$6
psa_pos_start=$7   
psa_pos_end=$8 
psa_neg_start=$9 
psa_neg_end=${10} 
python_exe=${11}
code_dir=${12}
vis_dir=${13}
temp_dir=${14}

temp_files=()

# Generate a date list and calculate composite for each phase range

start_phases=( ${psa_pos_start} ${psa_neg_start} )
end_phases=( ${psa_pos_end} ${psa_neg_end} )
for idx in "${!start_phases[@]}"; do
    
    start_phase=${start_phases[$idx]}
    end_phase=${end_phases[$idx]}
    
    temp_date_file=${temp_dir}/dates_phase${idx}.txt

    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    temp_files+=(${temp_date_file})
done


${python_exe} ${vis_dir}/plot_scathist.py ${sam_file} sam ${enso_file} ${enso_var} ${outfile} --subset all --subset ${temp_dir}/dates_phase0.txt --subset ${temp_dir}/dates_phase1.txt --ylabel Nino_3.4_index --xlabel SAM_index

rm ${temp_files[@]}
