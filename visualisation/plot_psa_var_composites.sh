#
# Description: Calculate composites for various Fourier phases
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 fourier_file sf_file var_file var_short var_long freq outfile python_exe code_dir vis_dir temp_dir"
    echo "   fourier_file: Fourier transform file name"
    echo "   sf_file:      Streamfunction file"
    echo "   var_file:     Variable file"
    echo "   var_short:    Variable short name"
    echo "   var_long:     Variable long name"
    echo "   freq:         Frequency to filter phase against"
    echo "   outfile:      Output file name, which includes the word phase-range which will be replaced"
    echo "   python_exe:   Python executable"
    echo "   code_dir:     Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:      Directory that plot_map.py is in"
    echo "   temp_dir:     Directory to store temporary data files"
    exit 1
}

nargs=11

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
sf_file=$2
var_file=$3
var_short=$4
var_long=$5
freq=$6
outfile=$7
python_exe=$8
code_dir=$9
vis_dir=${10}
temp_dir=${11}

central_phases=(13 30 44 57)
temp_files=()


# Generate a date list and calculate composite for each phase range

for central_phase in "${central_phases[@]}"; do
    start_phase=`expr $central_phase - 5`
    end_phase=`expr $central_phase + 5`
    
    temp_outfile=`echo ${outfile} | sed s/phase-range/phase${start_phase}-${end_phase}/`

    temp_date_file=${temp_dir}/dates_phase${start_phase}-${end_phase}.txt
    temp_sfcomp_file=${temp_dir}/sf-composite_phase${start_phase}-${end_phase}.nc
    temp_varcomp_file=${temp_dir}/${var_short}-composite_phase${start_phase}-${end_phase}.nc    

    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${code_dir}/calc_composite.py ${sf_file} sf ${temp_sfcomp_file} \
    --date_file ${temp_date_file} --region sh --no_sig

    ${python_exe} ${code_dir}/calc_composite.py ${var_file} ${var_short} ${temp_varcomp_file} \
    --date_file ${temp_date_file} --region sh
    
    bash ${vis_dir}/plot_composite.sh ${temp_varcomp_file} ${var_long} ${temp_sfcomp_file} streamfunction ${temp_outfile} ${python_exe} ${vis_dir}

    temp_files+=(${temp_date_file} ${temp_sfcomp_file} ${temp_varcomp_file})
done

rm ${temp_files[@]}
