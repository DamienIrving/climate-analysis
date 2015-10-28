#
# Description: Calculate tas, pr and sic composites for various Fourier phase groupings
#

function usage {
    echo "USAGE: bash $0 fourier_file sf_file tas_file pr_file sic_file freq outfile" 
    echo "               psa_pos_start psa_pos_end psa_neg_start psa_neg_end"
    echo "               python_exe code_dir vis_dir temp_dir"
    echo " "
    echo "   fourier_file:  Fourier transform file name"
    echo "   sf_file:       Streamfunction file"
    echo "   tas_file:      Surface air temperature anomaly file"
    echo "   pr_file:       Precipitation anomaly file"
    echo "   sic_file:      Sea ice fraction anomaly file"
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

nargs=15

if [ $# -ne $nargs ] ; then
  usage
fi

fourier_file=$1
sf_file=$2
tas_file=$3
pr_file=$4
sic_file=$5
freq=$6
outfile=$7
psa_pos_start=$8   
psa_pos_end=$9   
psa_neg_start=${10}  
psa_neg_end=${11}   
python_exe=${12}
code_dir=${13}
vis_dir=${14}
temp_dir=${15}

temp_files=()


start_phases=( ${psa_pos_start} ${psa_neg_start} )
end_phases=( ${psa_pos_end} ${psa_neg_end} )
for idx in "${!start_phases[@]}"; do
    
    start_phase=${start_phases[$idx]}
    end_phase=${end_phases[$idx]}
    
    temp_date_file=${temp_dir}/dates_phase-group${idx}.txt
    temp_sfcomp_file=${temp_dir}/sf-composite_phase-group${idx}.nc
    temp_tascomp_file=${temp_dir}/tas-composite_phase-group${idx}.nc
    temp_prcomp_file=${temp_dir}/pr-composite_phase-group${idx}.nc
    temp_siccomp_file=${temp_dir}/sic-composite_phase-group${idx}.nc
    
    ${python_exe} ${code_dir}/psa_date_list.py ${fourier_file} ${temp_date_file} \
    --freq ${freq} --phase_filter ${start_phase} ${end_phase}
    
    ${python_exe} ${code_dir}/calc_composite.py ${sf_file} sf ${temp_sfcomp_file} \
    --date_file ${temp_date_file} --region sh --no_sig
    
    ${python_exe} ${code_dir}/calc_composite.py ${tas_file} tas ${temp_tascomp_file} \
    --date_file ${temp_date_file} --region sh
    
    ${python_exe} ${code_dir}/calc_composite.py ${pr_file} pr ${temp_prcomp_file} \
    --date_file ${temp_date_file} --region sh
    
    ${python_exe} ${code_dir}/calc_composite.py ${sic_file} sic ${temp_siccomp_file} \
    --date_file ${temp_date_file} --region sh
    
    temp_files+=(${temp_date_file} ${temp_sfcomp_file} ${temp_tascomp_file} ${temp_prcomp_file} ${temp_siccomp_file})
done

levels="-6 -5 -4 -3 -2 -1 0 1 2 3 4 5 6" 

tas_ticks="-2.5 -2.0 -1.5 -1.0 -0.5 0 0.5 1.0 1.5 2.0 2.5" 
tas_palette=RdBu_r

sic_ticks="-0.13 -0.11 -0.09 -0.07 -0.05 -0.03 -0.01 0.01 0.03 0.05 0.07 0.09 0.11 0.13"
sic_palette=RdBu_r

pr_ticks="-1.0 -0.8 -0.6 -0.4 -0.2 0 0.2 0.4 0.6 0.8 1.0" 
pr_palette=BrBG


${python_exe} ${vis_dir}/plot_map.py 2 3 \
--infile ${temp_dir}/tas-composite_phase-group0.nc surface_air_temperature_annual none none none colour0 1 PlateCarree \
--infile ${temp_dir}/pr-composite_phase-group0.nc precipitation_annual none none none colour0 2 PlateCarree \
--infile ${temp_dir}/sic-composite_phase-group0.nc sea_ice_fraction_annual none none none colour0 3 PlateCarree \
--infile ${temp_dir}/tas-composite_phase-group1.nc surface_air_temperature_annual none none none colour0 4 PlateCarree \
--infile ${temp_dir}/pr-composite_phase-group1.nc precipitation_annual none none none colour0 5 PlateCarree \
--infile ${temp_dir}/sic-composite_phase-group1.nc sea_ice_fraction_annual none none none colour0 6 PlateCarree \
--colourbar_type individual \
--infile ${temp_dir}/tas-composite_phase-group0.nc p_value_annual none none none hatching0 1 PlateCarree \
--infile ${temp_dir}/pr-composite_phase-group0.nc p_value_annual none none none hatching0 2 PlateCarree \
--infile ${temp_dir}/sic-composite_phase-group0.nc p_value_annual none none none hatching0 3 PlateCarree \
--infile ${temp_dir}/tas-composite_phase-group1.nc p_value_annual none none none hatching0 4 PlateCarree \
--infile ${temp_dir}/pr-composite_phase-group1.nc p_value_annual none none none hatching0 5 PlateCarree \
--infile ${temp_dir}/sic-composite_phase-group1.nc p_value_annual none none none hatching0 6 PlateCarree \
--output_projection SouthPolarStereo \
--subplot_headings surface_temperature precipitation sea_ice_fraction none none none \
--infile ${temp_dir}/sf-composite_phase-group0.nc streamfunction_annual none none none contour0 1 PlateCarree \
--infile ${temp_dir}/sf-composite_phase-group0.nc streamfunction_annual none none none contour0 2 PlateCarree \
--infile ${temp_dir}/sf-composite_phase-group0.nc streamfunction_annual none none none contour0 3 PlateCarree \
--infile ${temp_dir}/sf-composite_phase-group1.nc streamfunction_annual none none none contour0 4 PlateCarree \
--infile ${temp_dir}/sf-composite_phase-group1.nc streamfunction_annual none none none contour0 5 PlateCarree \
--infile ${temp_dir}/sf-composite_phase-group1.nc streamfunction_annual none none none contour0 6 PlateCarree \
--ofile ${outfile} \
--hatch_bounds 0.0 0.01 \
--hatch_styles bwdlines_tight \
--contour_levels ${levels} \
--figure_size 12 12 

#--colourbar_ticks ${ticks} \
#--palette ${palette} \

#--extend ${extend} \


#rm ${temp_files[@]}
