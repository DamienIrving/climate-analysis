#
# Description: Create seasonaly histograms for various Fourier phases
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 fourier_file freq outfile psa_pos_start psa_pos_end psa_neg_start psa_neg_end python_exe code_dir vis_dir temp_dir"
    echo "   fourier_file:  Fourier transform file name"
    echo "   freq:          Frequency to filter phase against"
    echo "   outfile:       Output file name, which includes the word group which will be replaced"
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

nargs=11

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
freq=$2
outfile=$3
psa_pos_start=$4   
psa_pos_end=$5   
psa_neg_start=$6  
psa_neg_end=$7 
python_exe=$8
code_dir=$9
vis_dir=${10}
temp_dir=${11}

temp_files=()

# Generate a date list and calculate composite for each phase range

file_tags=( psa-pos psa-neg )
start_phases=( ${psa_pos_start} ${psa_neg_start} )
end_phases=( ${psa_pos_end} ${psa_neg_end} )
for idx in "${!start_phases[@]}"; do
    
    start_phase=${start_phases[$idx]}
    end_phase=${end_phases[$idx]}
   
    new_outfile=`echo ${outfile} | sed s/group/${file_tags[$idx]}/`

    temp_date_file=${temp_dir}/dates_temp.txt
    
    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${vis_dir}/plot_date_list.py ${temp_date_file} ${new_outfile} \
    --start 1979-01-01 --end 2015-01-31 --figure_size 7 9 --y_buffer 1.1

    rm $temp_date_file
done

