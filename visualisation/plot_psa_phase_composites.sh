#
# Description: Calculate composites for various Fourier phases
# (on abyss and/or vortex.earthsci.unimelb.edu.au) 
#

function usage {
    echo "USAGE: bash $0 fourier_file sf_file freq duration outfile python_exe code_dir vis_dir temp_dir"
    echo "   fourier_file: Fourier transform file name"
    echo "   sf_file:      Streamfunction file"
    echo "   freq:         Frequency to filter phase against"
    echo "   duration:     Minimum event duration"
    echo "   outfile:      Output file name, which includes the word season which will be replaced"
    echo "   python_exe:   Python executable"
    echo "   code_dir:     Directory that psa_date_list.py and calc_composite.py are in"
    echo "   vis_dir:      Directory that plot_map.py is in"
    echo "   temp_dir:     Directory to store temporary data files"
    exit 1
}

nargs=9

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
sf_file=$2
freq=$3
duration=$4
outfile=$5
python_exe=$6
code_dir=$7
vis_dir=$8
temp_dir=$9

start_phases=(0 10 20 30 40 50)
temp_files=()

# Generate a date list and calculate composite for each phase range

for start_phase in "${start_phases[@]}"; do
    end_phase=`expr $start_phase + 10`
    
    temp_date_file=${temp_dir}/dates_phase${start_phase}-${end_phase}.txt
    temp_sfcomp_file=${temp_dir}/sf-composite_phase${start_phase}-${end_phase}.nc
    
    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --duration_filter ${duration} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${code_dir}/calc_composite.py ${sf_file} sf ${temp_sfcomp_file} \
    --date_file ${temp_date_file} --region sh --no_sig
    
    temp_files+=(${temp_date_file} ${temp_sfcomp_file})
done

# Generate the plot

for season in DJF MAM JJA SON annual; do

    new_outfile=`echo ${outfile} | sed s/season/${season}/`

    ${python_exe} ${vis_dir}/plot_map.py 3 2 \
    --output_projection PlateCarree_Dateline --subplot_headings 0-10 10-20 20-30 30-40 40-50 50-60 \
    --infile ${temp_dir}/sf-composite_phase0-10.nc streamfunction_${season} none none none contour0 1 PlateCarree \
    --infile ${temp_dir}/sf-composite_phase10-20.nc streamfunction_${season} none none none contour0 2 PlateCarree \
    --infile ${temp_dir}/sf-composite_phase20-30.nc streamfunction_${season} none none none contour0 3 PlateCarree \
    --infile ${temp_dir}/sf-composite_phase30-40.nc streamfunction_${season} none none none contour0 4 PlateCarree \
    --infile ${temp_dir}/sf-composite_phase40-50.nc streamfunction_${season} none none none contour0 5 PlateCarree \
    --infile ${temp_dir}/sf-composite_phase50-60.nc streamfunction_${season} none none none contour0 6 PlateCarree \
    --contour_levels -12 -10 -8 -6 -4 -2 0 2 4 6 8 10 12 \
    --figure_size 12 8 --exclude_blanks --region sh --title ${season}\
    --ofile ${new_outfile}
done
rm ${temp_files[@]}
