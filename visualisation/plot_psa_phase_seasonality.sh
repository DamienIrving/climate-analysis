#
# Description: Create seasonaly histograms for various Fourier phases
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 fourier_file freq outfile python_exe code_dir vis_dir temp_dir"
    echo "   fourier_file: Fourier transform file name"
    echo "   freq:         Frequency to filter phase against"
    echo "   outfile:      Output file name, which includes the word season which will be replaced"
    echo "   python_exe:   Python executable"
    echo "   code_dir:     Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:      Directory that plot_map.py is in"
    echo "   temp_dir:     Directory to store temporary data files"
    exit 1
}

nargs=7

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
freq=$2
outfile=$3
python_exe=$4
code_dir=$5
vis_dir=$6
temp_dir=$7

central_phases=(13 30 44 57)
temp_files=()

# Generate a date list and calculate composite for each phase range

for central_phase in "${central_phases[@]}"; do
    start_phase=`expr $central_phase - 5`
    end_phase=`expr $central_phase + 5`
   
    new_outfile=`echo ${outfile} | sed s/phase-range/phase${start_phase}-${end_phase}/`

    temp_date_file=${temp_dir}/dates_phase${start_phase}-${end_phase}.txt
    
    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${vis_dir}/plot_date_list.py ${temp_date_file} ${new_outfile} \
    --plot_types monthly_totals_histogram seasonal_values_stackplot --start 1979-01-01 --end 2015-01-31

    rm $temp_date_file
done

