#
# Description: Script for plotting the GHG - AA trend comparison
#

function usage {
    echo "USAGE: bash $0 model variable plot_type"
    echo "   e.g. bash $0 IPSL-CM5A-LR thetao vertical"
    exit 1
}

model=$1
variable=$2
plot_type=$3  # vertical or zonal

if [[ "${variable}" == "so" ]] ; then
    long_name='sea_water_salinity'
    palette='RdGy_r'
    if [[ "${plot_type}" == "zonal" ]] ; then
        tick_max='1.5'
        tick_step='0.25'
        tick_label='zm'
    elif [[ "${plot_type}" == "vertical" ]] ; then
        tick_max='5'
        tick_step='1'
        tick_label='vm'
    fi
elif [[ "${variable}" == 'thetao' ]] ; then
    long_name='sea_water_potential_temperature'
    palette='RdGy_r'
    if [[ "${plot_type}" == "zonal" ]] ; then
        tick_max='10'
        tick_step='2'
        tick_label='zm'
    elif [[ "${plot_type}" == "vertical" ]] ; then
        tick_max='25'
        tick_step='5'
        tick_label='vm'
    fi
fi

if [[ "${model}" == "IPSL-CM5A-LR" ]] ; then
    organisation='IPSL'
    run='r1'
    aa_physics='p3'
elif [[ "${model}" == 'CSIRO-Mk3-6-0' ]] ; then
    organisation='CSIRO-QCCCE'
    run='ensmean-'
    aa_physics='p4'
elif [[ "${model}" == 'CanESM2' ]] ; then
    organisation='CCCMA'
    run='ensmean-'
    aa_physics='p4'
elif [[ "${model}" == 'NorESM1-M' ]] ; then
    organisation='NCC'
    run='r1'
    aa_physics='p1'
elif [[ "${model}" == 'GFDL-ESM2M' ]] ; then
    organisation='NOAA-GFDL'
    run='r1'
    aa_physics='p5'
elif [[ "${model}" == 'FGOALS-g2' ]] ; then
    organisation='LASG-CESS'
    run='r1'  #manually edit to r2 for AA
    aa_physics='p1'
fi

python=/g/data/r87/dbi599/miniconda2/envs/default/bin/python 
model_dir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${organisation}/${model}
file_GHG=${model_dir}/historicalGHG/yr/ocean/${variable}-maps/${run}i1p1/${variable}-maps-global-tas-trend_Oyr_${model}_historicalGHG_${run}i1p1_1950-01-01_2000-12-31.nc
outfile=/g/data/r87/dbi599/figures/${variable}-maps-global-tas-trend-${plot_type}-mean_Oyr_${model}_historicalGHG-minus-AA_${run}i1_1950-01-01_2000-12-31.png
climatology=${model_dir}/historical/yr/ocean/${variable}-maps/${run}i1p1/${variable}-maps-clim_Oyr_${model}_historical_${run}i1p1_all.nc
file_AA=${model_dir}/historicalMisc/yr/ocean/${variable}-maps/${run}i1${aa_physics}/${variable}-maps-global-tas-trend_Oyr_${model}_historicalMisc_${run}i1${aa_physics}_1950-01-01_2000-12-31.nc


echo ${python} ~/climate-analysis/visualisation/plot_ocean_trend.py ${file_GHG} ${long_name} ${plot_type}_mean ${outfile} --palette ${palette} --sub_file ${file_AA} --climatology_file ${climatology} --${tick_label}_ticks ${tick_max} ${tick_step} 

