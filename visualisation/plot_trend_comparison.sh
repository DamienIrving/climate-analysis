#
# Description: Script for plotting the GHG - AA trend comparison
#

function usage {
    echo "USAGE: bash $0 model variable"
    echo "   e.g. bash $0 IPSL-CM5A-LR thetao"
    exit 1
}

model=$1
variable=$2

if [[ "${variable}" == "so" ]] ; then
    long_name='sea_water_salinity'
    zm_tick_max='1.5'
    zm_tick_step='0.25'
    vm_tick_max='10'
    vm_tick_step='2'
    palette='RdGy_r'
elif [[ "${variable}" == 'thetao' ]] ; then
    long_name='sea_water_potential_temperature'
    zm_tick_max='10'
    zm_tick_step='2'
    vm_tick_max='25'
    vm_tick_step='5'
    palette='RdGy_r'
fi

if [[ "${model}" == "IPSL-CM5A-LR" ]] ; then
    organisation='IPSL'
    run='r1'
    aa_physics='p3'
elif [[ "${model}" == 'CSIRO-Mk3-6-0' ]] ; then
    organisation='CSIRO-QCCCE'
    run='ensmean-'
    aa_physics='p4'
fi

python=/g/data/r87/dbi599/miniconda2/envs/default/bin/python 
model_dir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${organisation}/${model}
file_GHG=${model_dir}/historicalGHG/yr/ocean/${variable}-maps/${run}i1p1/${variable}-maps-global-tas-trend_Oyr_${model}_historicalGHG_${run}i1p1_1950-01-01_2000-12-31.nc
outfile=/g/data/r87/dbi599/figures/${variable}-maps-global-tas-trend-zonal-mean_Oyr_${model}_historicalGHG-minus-AA_${run}i1_1950-01-01_2000-12-31.png
climatology=${model_dir}/historical/yr/ocean/${variable}-maps/${run}i1p1/${variable}-maps-clim_Oyr_${model}_historical_${run}i1p1_all.nc
file_AA=${model_dir}/historicalMisc/yr/ocean/${variable}-maps/${run}i1${aa_physics}/${variable}-maps-global-tas-trend_Oyr_${model}_historicalMisc_${run}i1${aa_physics}_1950-01-01_2000-12-31.nc


${python} ~/climate-analysis/visualisation/plot_ocean_trend.py ${file_GHG} ${long_name} zonal_mean ${outfile} --zm_ticks ${zm_tick_max} ${zm_tick_step} --palette ${palette} --climatology_file ${climatology} --sub_file ${file_AA}
echo ${outfile}
