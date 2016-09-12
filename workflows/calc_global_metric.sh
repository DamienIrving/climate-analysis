#
# Description: Script for calculating global metrics
#

function usage {
    echo "USAGE: bash $0 model variable experiment runs"
    echo "   e.g. bash $0 CSIRO-Mk3-6-0 tas historical r1i1p1 r1i1p2 r1i1p3"
    exit 1
}

model=$1
variable=$2
experiment=$3
shift
shift
shift
runs=( $@ )

python=/g/data/r87/dbi599/miniconda2/envs/default/bin/python
area_run=r0i0p0
tas_dir='ua6'
sos_dir='ua6'
pr_dir='ua6'
prOmon_dir='ua6'
evspsbl_dir='ua6'
area_dir='ua6'
if [[ "${model}" == "CSIRO-Mk3-6-0" ]] ; then
    institution="CSIRO-QCCCE"
elif [[ "${model}" == "IPSL-CM5A-LR" ]] ; then
    institution="IPSL"
fi

for run in "${runs[@]}"; do
    
    if [[ "${model}" == "CSIRO-Mk3-6-0" && "${experiment}" == "historicalMisc" ]] ; then
        physics=`echo ${run} | cut -d p -f 2`
        area_run=r0i0p${physics}
    elif [[ "${model}" == "IPSL-CM5A-LR" && "${experiment}" == "historicalMisc" ]] ; then
        sos_dir='r87/dbi599'
        prOmon_dir='r87/dbi599'
        evspsbl_dir='r87/dbi599'
        area_dir='r87/dbi599'
    fi

    if [[ "${variable}" == "sos" ]] ; then
        data_file=`ls /g/data/${sos_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/ocean/sos/${run}/sos_Omon_${model}_${experiment}_${run}*.nc`
        area_file=/g/data/${area_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/fx/ocean/areacello/${area_run}/areacello_fx_${model}_${experiment}_${area_run}.nc
        standard_name=sea_surface_salinity
        metric=amplification
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/sos_/sos-global-amp_/`
        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/ocean/sos/${run}
        out_file=${outdir}/${outname}
    elif [[ "${variable}" == "tas" ]] ; then
        data_file=`ls /g/data/${tas_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/atmos/tas/${run}/tas_Amon_${model}_${experiment}_${run}*.nc`
        area_file=/g/data/${area_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/fx/atmos/areacella/${area_run}/areacella_fx_${model}_${experiment}_${area_run}.nc
        standard_name=air_temperature
        metric=mean
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/tas_/tas-global-mean_/`
        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/atmos/tas/${run}
        out_file=${outdir}/${outname}
    elif [[ "${variable}" == "pr" ]] ; then
        data_file=`ls /g/data/${pr_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/atmos/pr/${run}/pr_Amon_${model}_${experiment}_${run}*.nc`
        area_file=/g/data/${area_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/fx/atmos/areacella/${area_run}/areacella_fx_${model}_${experiment}_${area_run}.nc
        standard_name=precipitation_flux
        metric=mean
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/pr_/pr-global-mean_/`
        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/atmos/pr/${run}
        out_file=${outdir}/${outname}
    elif [[ "${variable}" == "evspsbl" ]] ; then
        data_file=`ls /g/data/${evspsbl_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/atmos/evspsbl/${run}/evspsbl_Amon_${model}_${experiment}_${run}*.nc`
        area_file=/g/data/${area_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/fx/atmos/areacella/${area_run}/areacella_fx_${model}_${experiment}_${area_run}.nc
        standard_name=water_evaporation_flux
        metric=mean
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/evspsbl_/evspsbl-global-mean_/`
        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/atmos/evspsbl/${run}
        out_file=${outdir}/${outname}
    elif [[ "${variable}" == "prOmon" ]] ; then
        data_file=`ls /g/data/${prOmon_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/ocean/pr/${run}/pr_Omon_${model}_${experiment}_${run}*.nc`
        area_file=/g/data/${area_dir}/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/fx/ocean/areacello/${area_run}/areacello_fx_${model}_${experiment}_${area_run}.nc
        standard_name=precipitation_flux
        metric=mean
        outname=`echo ${data_file} | rev | cut -d / -f 1 | rev | sed s/pr_/pr-global-mean_/`
        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${experiment}/mon/ocean/pr/${run}
        out_file=${outdir}/${outname}
    fi

    echo ${out_file}
    mkdir -p ${outdir}
    ${python} ~/climate-analysis/data_processing/calc_global_metric.py ${data_file} ${standard_name} ${metric} ${out_file} --area_file ${area_file}

done
