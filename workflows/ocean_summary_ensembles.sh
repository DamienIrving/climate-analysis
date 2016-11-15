#
# Description: Script for calculating ensemble mean fields produced from ocean_summary_bash.sh
#

function usage {
    echo "USAGE: bash $0 institution model misc_physics_vals"
    echo "   e.g. bash $0 CSIRO-QCCCE CSIRO-Mk3-6-0 1 4"
    exit 1
}


institution=$1
model=$2
shift
shift
physics=( $@ )

### Atmospheric global metrics

experiments=(historical historicalNat historicalGHG)  # 
variables=(pr evspsbl tas)
for exp in "${experiments[@]}"; do
    for var in "${variables[@]}"; do

        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/atmos/${var}/ensmean-i1p1
        outfile=${outdir}/${var}-global-mean_Ayr_${model}_${exp}_ensmean-i1p1_all.nc

        mkdir -p ${outdir}
        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/atmos/${var}/r*i1p1/${var}-global-mean_Ayr_${model}_${exp}_r*i1p1_all.nc ${outfile}

        echo ${outfile}

    done
done

exp=historicalMisc
variables=(pr evspsbl tas)
for phys in "${physics[@]}"; do
    for var in "${variables[@]}"; do

        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/atmos/${var}/ensmean-i1p${phys}
        outfile=${outdir}/${var}-global-mean_Ayr_${model}_${exp}_ensmean-i1p${phys}_all.nc

        mkdir -p ${outdir}
        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/atmos/${var}/r*i1p${phys}/${var}-global-mean_Ayr_${model}_${exp}_r*i1p${phys}_all.nc ${outfile}

        echo ${outfile}

    done
done


### Oceanic global metrics

experiments=(historical historicalNat historicalGHG) #  
for exp in "${experiments[@]}"; do

    outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/sos/ensmean-i1p1
    outfile=${outdir}/sos-global-amp_Oyr_${model}_${exp}_ensmean-i1p1_all.nc

    mkdir -p ${outdir} 
    cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/sos/r*i1p1/sos-global-amp_Oyr_${model}_${exp}_r*i1p1_all.nc ${outfile}

    echo ${outfile}

done


exp=historicalMisc
for phys in "${physics[@]}"; do

    outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/sos/ensmean-i1p${phys}
    outfile=${outdir}/sos-global-amp_Oyr_${model}_${exp}_ensmean-i1p${phys}_all.nc

    mkdir -p ${outdir} 
    cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/sos/r*i1p${phys}/sos-global-amp_Oyr_${model}_${exp}_r*i1p${phys}_all.nc ${outfile}

    echo ${outfile}

done


### Ocean maps

experiments=(historical historicalGHG)  # 
variables=(so thetao)
for exp in "${experiments[@]}"; do
    for var in "${variables[@]}"; do

        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/ensmean-i1p1
        outfile=${outdir}/${var}-maps-time-trend_Oyr_${model}_${exp}_ensmean-i1p1_1950-01-01_2000-12-31.nc
        climfile=${outdir}/${var}-maps-clim_Oyr_${model}_${exp}_ensmean-i1p1_all.nc
        tasfile=${outdir}/${var}-maps-global-tas-trend_Oyr_${model}_${exp}_ensmean-i1p1_1950-01-01_2000-12-31.nc

        mkdir -p ${outdir}
        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/r*i1p1/${var}-maps-time-trend_Oyr_${model}_${exp}_r*i1p1_1950-01-01_2000-12-31.nc ${outfile}
        echo ${outfile}

        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/r*i1p1/${var}-maps-clim_Oyr_${model}_${exp}_r*i1p1_all.nc ${climfile}
        echo ${climfile}

        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/r*i1p1/${var}-maps-global-tas-trend_Oyr_${model}_${exp}_r*i1p1_1950-01-01_2000-12-31.nc ${tasfile}
        echo ${tasfile}

    done
done


exp=historicalMisc
variables=(so thetao)
for phys in "${physics[@]}"; do
    for var in "${variables[@]}"; do

        outdir=/g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/ensmean-i1p${phys}
        outfile=${outdir}/${var}-maps-time-trend_Oyr_${model}_${exp}_ensmean-i1p${phys}_1950-01-01_2000-12-31.nc
        climfile=${outdir}/${var}-maps-clim_Oyr_${model}_${exp}_ensmean-i1p${phys}_all.nc
        tasfile=${outdir}/${var}-maps-global-tas-trend_Oyr_${model}_${exp}_ensmean-i1p${phys}_1950-01-01_2000-12-31.nc

        mkdir -p ${outdir}
        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/r*i1p${phys}/${var}-maps-time-trend_Oyr_${model}_${exp}_r*i1p${phys}_1950-01-01_2000-12-31.nc ${outfile}
        echo ${outfile}

        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/r*i1p${phys}/${var}-maps-clim_Oyr_${model}_${exp}_r*i1p${phys}_all.nc ${climfile}
        echo ${climfile}

        cdo ensmean /g/data/r87/dbi599/drstree/CMIP5/GCM/${institution}/${model}/${exp}/yr/ocean/${var}-maps/r*i1p${phys}/${var}-maps-global-tas-trend_Oyr_${model}_${exp}_r*i1p${phys}_1950-01-01_2000-12-31.nc ${tasfile}
        echo ${tasfile}

    done
done



