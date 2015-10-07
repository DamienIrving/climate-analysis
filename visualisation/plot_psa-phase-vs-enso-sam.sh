#
# Description: Create ENSO/SAM scatter plots for various phase ranges
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 sam_file enso_file enso_var colour_file colour_var fourier_file freq outfile python_exe code_dir vis_dir temp_dir"
    echo "   sam_file:     SAM file"
    echo "   enso_file:    ENSO file"
    echo "   enso_var:     ENSO variable"
    echo "   colour_file:  File for colouring the dots on the scatterplot"
    echo "   colour_var:   Colour variable"
    echo "   fourier_file: Fourier transform file name"
    echo "   freq:         Frequency to filter phase against"
    echo "   outfile:      Output file name, which includes the word phase-range which will be replaced"
    echo "   python_exe:   Python executable"
    echo "   code_dir:     Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:      Directory that plot_map.py is in"
    echo "   temp_dir:     Directory to store temporary data files"
    exit 1
}

nargs=12

if [ $# -ne $nargs ] ; then
  usage
fi

sam_file=$1
enso_file=$2
enso_var=$3
colour_file=$4
colour_var=$5
fourier_file=$6
freq=$7
outfile=$8
python_exe=$9
code_dir=${10}
vis_dir=${11}
temp_dir=${12}

central_phases=(13 30 44 57)


# Generate a date list and calculate composite for each phase range

for central_phase in "${central_phases[@]}"; do
    start_phase=`expr $central_phase - 5`
    end_phase=`expr $central_phase + 5`
    
    temp_outfile=`echo ${outfile} | sed s/phase-range/phase${start_phase}-${end_phase}/`

    temp_date_file=${temp_dir}/dates_phase${start_phase}-${end_phase}.txt

    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${vis_dir}/plot_scatter.py ${sam_file} sam ${enso_file} ${enso_var} ${temp_outfile} \
    --colour ${colour_file} ${colour_var} --zero_lines --cmap Greys --ylabel ${enso_var} --xlabel SAM \
    --date_filter ${temp_date_file} --quadrant_text

    rm ${temp_date_file}
done

