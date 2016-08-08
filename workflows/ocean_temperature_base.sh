#
# Description: Script for running the ohc_base.mk workflow for a given model/experiment combo
#

function usage {
    echo "USAGE: bash $0 model experiments"
    echo "   e.g. bash $0 CSIRO-Mk3-6-0 historical noAA"
    exit 1
}

# Read inputs

OPTIND=1 
options=' '
while getopts ":nB" opt; do
  case $opt in
    n)
      options+=' -n' >&2
      ;;
    B)
      options+=' -B' >&2
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done
shift $((OPTIND-1))

model=$1
shift
experiments=( $@ )

# Determine runs based on model and experiment

for experiment in "${experiments[@]}"; do

    fxrun='r0i0p0'
    controlrun='r1i1p1'

    if [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 ) 
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 ) 
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 ) 
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'
        fxrun='r0i0p1'

    #elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'NoOz' ]] ; then
    #    experiment='historicalMisc'
    #    runs=( r1i1p2 r2i1p2 r3i1p2 )
    #    #r4i1p2 r5i1p2 r6i1p2 r7i1p2 r8i1p2 r9i1p2 r10i1p2
    #    organisation='CSIRO-QCCCE'
    #    fxrun='r0i0p2'
    #branches from historical experiment

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'noAA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p3 )
        #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 r6i1p3 r7i1p3 r8i1p3 r9i1p3 r10i1p3
        organisation='CSIRO-QCCCE'
        fxrun='r0i0p3'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p4 r3i1p4 r4i1p4 r5i1p4 r6i1p4 r7i1p4 r8i1p4 r9i1p4 r10i1p4 )
        #r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4 r6i1p4 r7i1p4 r8i1p4 r9i1p4 r10i1p4
        organisation='CSIRO-QCCCE'
        fxrun='r0i0p4'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'historical' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4 )
        #r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'historicalNat' ]] ; then
        experiment='historicalNat'
        runs=( r2i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historical' ]] ; then
        experiment='historical'
        runs=( r1i1p1 )
        # r1i1p1 r1i2p1 r1i2p2 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1
        organisation='NCAR'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 )
        # r1i1p1 r4i1p1 r6i1p1
        organisation='NCAR'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historicalNat' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 )
        # r1i1p1 r2i1p1 r4i1p1 r6i1p1
        organisation='NCAR'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historicalAA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p10 )
        # r1i1p10; missing r4i1p10 r6i1p10
        organisation='NCAR'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historicalAnt' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p11 )
        # r1i1p11 r2i1p11; missing r4i1p11 r6i1p11
        organisation='NCAR'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'historical' ]] ; then
        runs=( r2i1p1 r3i1p1 r4i1p1 r5i1p1 ) 
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 r3i1p1 ) 
        #r1i1p1 r3i1p1 r5i1p1 (r5 I had to download myself)
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 r3i1p1 r5i1p1 ) 
        #r1i1p1 r3i1p1 r5i1p1
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p1 r3i1p1 r5i1p1 )
        #r1i1p1 r3i1p1 r5i1p1
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p2 r3i1p2 r5i1p2 )
        #r1i1p2 r3i1p2 r5i1p2
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p5 )
        #r1i1p5
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p2 )
        #r1i1p2
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'historical' ]] ; then
        experiment='historical'
        runs=( r1i1p1 )
        #r1i1p1
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 )
        #r1i1p1
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'historicalNat' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 )
        #r1i1p1
        organisation='NOAA-GFDL'

    elif [[ ${model} == 'FGOALS-g2' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p1 )
        #r2i1p1
        organisation='LASG-CESS'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'AA-direct' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p106 r2i1p106 r3i1p106 r4i1p106 r5i1p106 )
        #r1i1p106 r2i1p106 r3i1p106 r4i1p106 r5i1p106
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'AA-conc' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107 )
        #r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'AA-emis' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310 )
        #r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310
        organisation='NASA-GISS'
        controlrun='r1i1p3'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalp3' ]] ; then
        experiment='historical'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )
        #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalp1' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controlrun='r1i1p1'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalNatp3' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )
        #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalNatp1' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controlrun='r1i1p1'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'AA-direct' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p106 r3i1p106 r4i1p106 r5i1p106 )
        #r1i1p106 r2i1p106 r3i1p106 r4i1p106 r5i1p106
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'AA-conc' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p107 r3i1p107 r4i1p107 r5i1p107 )
        #r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'AA-emis' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310 )
        #r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310
        organisation='NASA-GISS'
        controlrun='r1i1p3'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p109 r2i1p109 r3i1p109 r4i1p109 r5i1p109 )
        #r1i1p109 r2i1p109 r3i1p109 r4i1p109 r5i1p109
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'Oz' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p105 r2i1p105 r3i1p105 r4i1p105 r5i1p105 )
        #r1i1p105 r2i1p105 r3i1p105 r4i1p105 r5i1p105
        organisation='NASA-GISS'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalp3' ]] ; then
        experiment='historical'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )
        #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalp1' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controlrun='r1i1p1'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalNatp3' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )
        #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalNatp1' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controlrun='r1i1p1'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p3 )
        #r1i1p3
        organisation='IPSL'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p2 )
        #r1i1p2; missing r2i1p2 r3i1p2  
        organisation='IPSL'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 )
        #r1i1p1 (and probably more)  
        organisation='IPSL'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'historical' ]] ; then
        experiment='historical'
        runs=( r2i1p1 r3i1p1 r4i1p1 )
        #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1
        organisation='IPSL'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'historicalNat' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 )
        #r1i1p1 r2i1p1 r3i1p1
        organisation='IPSL'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'noAA' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p4 )
        #r1i1p4 r2i1p4 r3i1p4 r4i1p4
        organisation='IPSL'
        controlrun='r2i1p1'

    elif [[ ${model} == 'NorESM1-M' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p1 )
        #r1i1p1
        organisation='NCC'

    else
        echo "Unrecognised model (${model}) / experiment (${experiment}) combination"
        usage
    fi

    for run in "${runs[@]}"; do
        sed -i "s/^\(ORGANISATION\s*=\s*\).*$/\ORGANISATION=${organisation}/" ocean_temperature_config.mk
        sed -i "s/^\(MODEL\s*=\s*\).*$/\MODEL=${model}/" ocean_temperature_config.mk
        sed -i "s/^\(EXPERIMENT\s*=\s*\).*$/EXPERIMENT=${experiment}/" ocean_temperature_config.mk
        sed -i "s/^\(RUN\s*=\s*\).*$/\RUN=${run}/" ocean_temperature_config.mk
        sed -i "s/^\(FX_RUN\s*=\s*\).*$/\FX_RUN=${fxrun}/" ocean_temperature_config.mk
        sed -i "s/^\(CONTROL_RUN\s*=\s*\).*$/\CONTROL_RUN=${controlrun}/" ocean_temperature_config.mk
        make ${options} -f ocean_temperature_base.mk
        echo "DONE: ${model} ${experiment} ${run}: make ${options} -f ohc_base.mk"
    done
done






