#
# Description: Script for running the ohc_base.mk workflow for a given model/experiment combo
#

function usage {
    echo "USAGE: bash $0 model experiments"
    echo " "
    echo " "
    echo "   e.g. bash $0 ACCESS1-0 historical rcp85 historicalMisc"
    exit 1
}

# Read inputs

nargs=2
if [ $# -ne $nargs ] ; then
  usage
fi

model=$1
shift
experiments=$@


# Determine runs based on model and experiment

for experiment in "${experiments[@]}"; do
    if [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 )
        organization='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'noAA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 r6i1p3 r7i1p3 r8i1p3 r9i1p3 r10i1p3 )
        organization='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4 r6i1p4 r7i1p4 r8i1p4 r9i1p4 r10i1p4 )
        organization='CSIRO-QCCCE'

    elif [[ ${model} == 'ACCESS1-0' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 ) # incomplete
        organization='CSIRO-BOM'

    else
        echo "Unrecognised model (${model}) / experiment (${experiment}) combination"
        exit 1
    fi

    for run in "${runs[@]}"; do
        sed -i "s/^\(ORGANIZATION\s*=\s*\).*$/\ORGANIZATION=${organization}/" ohc_config.mk
        sed -i "s/^\(MODEL\s*=\s*\).*$/\MODEL=${model}/" ohc_config.mk
        sed -i "s/^\(PERIMENT\s*=\s*\).*$/\PERIMENT=${experiment}/" ohc_config.mk
        sed -i "s/^\(RUN\s*=\s*\).*$/\RUN=${run}/" ohc_config.mk
        make -f ohc_base.mk
    done
done






