#
# Description: Script for running the ohc_base.mk workflow for a given model/experiment combo
#

function usage {
    echo "USAGE: bash $0 model experiments"
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
    if [[ ${model} == 'CSIRO-' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 r1i1p2 )
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-' && ${experiment} == 'historical' ]] ; then
        runs=
        organisation=

    else
        echo "Unrecognised model (${model}) / experiment (${experiment}) combination"
        exit 1
fi
done


sed -i "s/^\(RUN\s*=\s*\).*$/\RUN=$RUN/" ohc_config.mk
