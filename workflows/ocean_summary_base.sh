#
# Description: Script for running the ocean_summary_base.mk workflow for a given model/variable/experiments combo
#

function usage {
    echo "USAGE: bash $0 model variable experiments"
    echo "   e.g. bash $0 CSIRO-Mk3-6-0 thetao historical noAA"
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
variable=$2
shift
shift
experiments=( $@ )

if [[ "${variable}" == "so" ]] ; then
    long_name='sea_water_salinity'
    zm_tick_max='3.5'
    zm_tick_step='0.5'
    vm_tick_max='10'
    vm_tick_step='2'
    scale_factor='3'
    palette='BrBG_r'
elif [[ "${variable}" == 'thetao' ]] ; then
    long_name='sea_water_potential_temperature'
    zm_tick_max='15'
    zm_tick_step='3'
    vm_tick_max='25'
    vm_tick_step='5'
    scale_factor='3'
    palette='RdBu_r'
fi

# Determine runs based on model and experiment

for experiment in "${experiments[@]}"; do

    fxrun='r0i0p0'
    controlrun='r1i1p1'
    vardir='ua6'
    controldir='ua6'
    voldir='ua6'
    basindir='ua6'
    depthdir='ua6'
    areaadir='ua6'
    areaodir='ua6'
    tasdir='ua6'
    sosdir='ua6'
    prdir='ua6'
    evspsbldir='ua6'

    # CanESM2

    if [[ ${model} == 'CanESM2' && ${experiment} == 'historical' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4 )  #r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4
        organisation='CCCMA'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'
        evspsbldir='r87/dbi599'
        areaadir='r87/dbi599'
     
    elif [[ ${model} == 'CanESM2' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'
        vardir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        areaadir='r87/dbi599'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'rcp85' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'rcp45' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == 'rcp26' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='CCCMA'

    elif [[ ${model} == 'CanESM2' && ${experiment} == '1pctCO2' ]] ; then
        runs=( r1i1p1 )  #r1i1p1
        organisation='CCCMA'

    # CCSM4 
    ## (No basin files)

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historical' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r4i1p1 r6i1p1 )  # r1i1p1 r1i2p1 r1i2p2 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1
        organisation='NCAR'
        controldir='r87/dbi599'  # for so, because had to fix_salinity_units.sh first

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 r4i1p1 r6i1p1 )  # r1i1p1 r4i1p1 r6i1p1
        organisation='NCAR'
        vardir='r87/dbi599'
        evspsbldir='r87/dbi599'
        sosdir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 r4i1p1 r6i1p1 )  # r1i1p1 r2i1p1 r4i1p1 r6i1p1
        organisation='NCAR'
        evspsbldir='r87/dbi599'
        sosdir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p10 r4i1p10 r6i1p10 )  # r1i1p10 r4i1p10 r6i1p10
        organisation='NCAR'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        prdir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'CCSM4' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p11 r4i1p11 r6i1p11 ) # r1i1p11 r2i1p11 r4i1p11 r6i1p11
        organisation='NCAR'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    # CSIRO-Mk3-6-0
        
    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 ) #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 ) #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1 ) #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1 r7i1p1 r8i1p1 r9i1p1 r10i1p1
        organisation='CSIRO-QCCCE'
        fxrun='r0i0p1'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'noAA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 r6i1p3 r7i1p3 r8i1p3 r9i1p3 r10i1p3 ) #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 r6i1p3 r7i1p3 r8i1p3 r9i1p3 r10i1p3
        organisation='CSIRO-QCCCE'
        fxrun='r0i0p3'

    elif [[ ${model} == 'CSIRO-Mk3-6-0' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4 r6i1p4 r7i1p4 r8i1p4 r9i1p4 r10i1p4 ) #r1i1p4 r2i1p4 r3i1p4 r4i1p4 r5i1p4 r6i1p4 r7i1p4 r8i1p4 r9i1p4 r10i1p4
        organisation='CSIRO-QCCCE'
        fxrun='r0i0p4'

    # FGOALS-g2

    elif [[ ${model} == 'FGOALS-g2' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='LASG-CESS'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'

    elif [[ ${model} == 'FGOALS-g2' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 r2i1p1 r3i1p1
        organisation='LASG-CESS'
        fxdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        areaadir='r87/dbi599'

    elif [[ ${model} == 'FGOALS-g2' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 )  #r1i1p1
        organisation='LASG-CESS'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'FGOALS-g2' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p1 )  #r2i1p1
        organisation='LASG-CESS'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        evspsbldir='r87/dbi599'

    # GFDL-CM3

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 r3i1p1 r5i1p1 ) #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NOAA-GFDL'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 r3i1p1 r5i1p1 )  #r1i1p1 r3i1p1 r5i1p1 (r5 I had to download myself)
        organisation='NOAA-GFDL'
        vardir='r87/dbi599' # for r5
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        #sosdir='r87/dbi599'  # for r5
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 r3i1p1 r5i1p1 )  #r1i1p1 r3i1p1 r5i1p1
        organisation='NOAA-GFDL'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p1 r3i1p1 r5i1p1 ) #r1i1p1 r3i1p1 r5i1p1
        organisation='NOAA-GFDL'
        evspsbldir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        #vardir='r87/dbi599'  # for thetao, because the ua6 data has time axis problems

    elif [[ ${model} == 'GFDL-CM3' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p2 r3i1p2 r5i1p2 ) #r1i1p2 r3i1p2 r5i1p2
        organisation='NOAA-GFDL'
        evspsbldir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'

    # GFDL-ESM2M

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p5 ) #r1i1p5
        organisation='NOAA-GFDL'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p2 ) #r1i1p2
        organisation='NOAA-GFDL'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 ) #r1i1p1
        organisation='NOAA-GFDL'
        areaodir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 )  #r1i1p1
        organisation='NOAA-GFDL'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        depthdir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'

    elif [[ ${model} == 'GFDL-ESM2M' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 )  #r1i1p1
        organisation='NOAA-GFDL'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'

    # GISS-E2-H

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'AA-direct' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p106 r2i1p106 r3i1p106 r4i1p106 r5i1p106 )  #r1i1p106 r2i1p106 r3i1p106 r4i1p106 r5i1p106
        organisation='NASA-GISS'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'AA-conc' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107 )  #r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107
        organisation='NASA-GISS'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'AA-emis' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310 )  #r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310
        organisation='NASA-GISS'
        controlrun='r1i1p3'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalp3' ]] ; then
        experiment='historical'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )  #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'
        sosdir='r87/dbi599'
        voldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalp1' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        voldir='r87/dbi599'
        tasdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalNatp3' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )  #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalNatp1' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controlrun='r1i1p1'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'historicalGHG' ]] ; then
        experiment='historicalGHG'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'Antp3' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p309 r2i1p309 r3i1p309 r4i1p309 r5i1p309 )  #r1i1p309 r2i1p309 r3i1p309 r4i1p309 r5i1p309
        organisation='NASA-GISS'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'
        depthdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-H' && ${experiment} == 'Antp1' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p109 r2i1p109 r3i1p109 r4i1p109 r5i1p109 )  #r1i1p109 r2i1p109 r3i1p109 r4i1p109 r5i1p109
        organisation='NASA-GISS'
        depthdir='r87/dbi599'


    # GISS-E2-R

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'AA-direct' ]] ; then
        experiment='historicalMisc'
        runs=( r2i1p106 r3i1p106 r4i1p106 r5i1p106 )  #r1i1p106 r2i1p106 r3i1p106 r4i1p106 r5i1p106
        organisation='NASA-GISS'
        vardir='r87/dbi599'
        controldir='r87/dbi599'
        basindir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'AA-conc' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107 )  #r1i1p107 r2i1p107 r3i1p107 r4i1p107 r5i1p107
        organisation='NASA-GISS'
        vardir='r87/dbi599'
        controldir='r87/dbi599'
        basindir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'AA-emis' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310 )  #r1i1p310 r2i1p310 r3i1p310 r4i1p310 r5i1p310
        organisation='NASA-GISS'
        controlrun='r1i1p3'
        vardir='r87/dbi599'
        controldir='r87/dbi599'
        basindir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'Antp1' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p109 r2i1p109 r3i1p109 r4i1p109 r5i1p109 )  #r1i1p109 r2i1p109 r3i1p109 r4i1p109 r5i1p109
        organisation='NASA-GISS'
        controldir='r87/dbi599'
        basindir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'Antp3' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p309 r2i1p309 r3i1p309 r4i1p309 r5i1p309 )  #r1i1p309 r2i1p309 r3i1p309 r4i1p309 r5i1p309
        organisation='NASA-GISS'
        controldir='r87/dbi599'
        basindir='r87/dbi599'
        evspsbldir='r87/dbi599'
        sosdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalp3' ]] ; then
        experiment='historical'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )  #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'
        basindir='r87/dbi599'
        sosdir='r87/dbi599'
        tasdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalp1' ]] ; then
        experiment='historical'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        basindir='r87/dbi599'
        sosdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalNatp3' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3 )  #r1i1p3 r2i1p3 r3i1p3 r4i1p3 r5i1p3
        organisation='NASA-GISS'
        controlrun='r1i1p3'
        controldir='r87/dbi599'
        basindir='r87/dbi599'
        evspsbldir='r87/dbi599'
        sosdir='r87/dbi599'
        tasdir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalNatp1' ]] ; then
        experiment='historicalNat'
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controlrun='r1i1p1'
        controldir='r87/dbi599'
        basindir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'GISS-E2-R' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1
        organisation='NASA-GISS'
        controldir='r87/dbi599'
        basindir='r87/dbi599'
        evspsbldir='r87/dbi599'

    # IPSL-CM5A-LR

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p3 )  #r1i1p3
        organisation='IPSL'
        #vardir='r87/dbi599'  # ua6 for thetao but not so
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'Ant' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p2 )  #r1i1p2; missing r2i1p2 r3i1p2  
        organisation='IPSL'
        #vardir='r87/dbi599'  # ua6 for thetao but not so
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 (and probably more)  
        organisation='IPSL'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        tasdir='r87/dbi599'
        sosdir='r87/dbi599'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 r2i1p1 r3i1p1 r4i1p1 r5i1p1 r6i1p1
        organisation='IPSL'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 r2i1p1 r3i1p1
        organisation='IPSL'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        evspsbldir='r87/dbi599'

    elif [[ ${model} == 'IPSL-CM5A-LR' && ${experiment} == 'noAA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p4 )  #r1i1p4 r2i1p4 r3i1p4 r4i1p4
        organisation='IPSL'
        controlrun='r2i1p1'
        vardir='r87/dbi599' # ua6 for thetao but not so
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'

    # NorEMS1-M

    elif [[ ${model} == 'NorESM1-M' && ${experiment} == 'historical' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 r2i1p1 r3i1p1 ( no basin )
        organisation='NCC'
        controldir='r87/dbi599'

    elif [[ ${model} == 'NorESM1-M' && ${experiment} == 'historicalNat' ]] ; then
        runs=( r1i1p1 )  #r1i1p1 ( no fx )
        organisation='NCC'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'

    elif [[ ${model} == 'NorESM1-M' && ${experiment} == 'AA' ]] ; then
        experiment='historicalMisc'
        runs=( r1i1p1 )  #r1i1p1
        organisation='NCC'
        vardir='r87/dbi599'
        controldir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'

    elif [[ ${model} == 'NorESM1-M' && ${experiment} == 'historicalGHG' ]] ; then
        runs=( r1i1p1 )  #r1i1p1
        organisation='NCC'
        vardir='r87/dbi599'
        voldir='r87/dbi599'
        basindir='r87/dbi599'
        areaadir='r87/dbi599'
        areaodir='r87/dbi599'
        sosdir='r87/dbi599'
        controldir='r87/dbi599'

    else
        echo "Unrecognised model (${model}) / experiment (${experiment}) combination"
        usage
    fi

    for run in "${runs[@]}"; do

        origvardir="/g/data/${vardir}/drstree/CMIP5/GCM"
        origcontroldir="/g/data/${controldir}/drstree/CMIP5/GCM"
        origvoldir="/g/data/${voldir}/drstree/CMIP5/GCM"
        origbasindir="/g/data/${basindir}/drstree/CMIP5/GCM"
        origdepthdir="/g/data/${depthdir}/drstree/CMIP5/GCM"
        origareaadir="/g/data/${areaadir}/drstree/CMIP5/GCM"
        origareaodir="/g/data/${areaodir}/drstree/CMIP5/GCM"
        origtasdir="/g/data/${tasdir}/drstree/CMIP5/GCM"
        origsosdir="/g/data/${sosdir}/drstree/CMIP5/GCM"
        origprdir="/g/data/${prdir}/drstree/CMIP5/GCM"
        origevspsbldir="/g/data/${evspsbldir}/drstree/CMIP5/GCM"

        make ${options} -f ocean_summary_base.mk ORGANISATION="${organisation}" MODEL="${model}" EXPERIMENT="${experiment}" RUN="${run}" FX_RUN="${fxrun}" CONTROL_RUN="${controlrun}" ORIG_VARIABLE_DIR="${origvardir}" ORIG_CONTROL_DIR="${origcontroldir}" ORIG_VOL_DIR="${origvoldir}" ORIG_BASIN_DIR="${origbasindir}" ORIG_DEPTH_DIR="${origdepthdir}" ORIG_AREAA_DIR="${origareaadir}" ORIG_AREAO_DIR="${origareaodir}" ORIG_TAS_DIR="${origtasdir}" ORIG_SOS_DIR="${origsosdir}" ORIG_PR_DIR="${origprdir}" ORIG_EVSPSBL_DIR="${origevspsbldir}" VAR="${variable}" LONG_NAME="${long_name}" ZM_TICK_MAX="${zm_tick_max}" ZM_TICK_STEP="${zm_tick_step}" VM_TICK_MAX="${vm_tick_max}" VM_TICK_STEP="${vm_tick_step}" SCALE_FACTOR="${scale_factor}" PALETTE="${palette}"

        echo "DONE: make ${options} -f ocean_summary_base.mk ORGANISATION=${organisation} MODEL=${model} EXPERIMENT=${experiment} RUN=${run} FX_RUN=${fxrun} CONTROL_RUN=${controlrun} ORIG_VARIABLE_DIR=${origvardir} ORIG_CONTROL_DIR=${origcontroldir} ORIG_VOL_DIR=${origvoldir} ORIG_BASIN_DIR=${origbasindir} ORIG_DEPTH_DIR=${origdepthdir} ORIG_AREAA_DIR=${origareaadir} ORIG_AREAO_DIR=${origareaodir} ORIG_TAS_DIR=${origtasdir} ORIG_SOS_DIR=${origsosdir} ORIG_PR_DIR=${origprdir} ORIG_EVSPSBL_DIR=${origevspsbldir} VAR=${variable} LONG_NAME=${long_name} ZM_TICK_MAX=${zm_tick_max} ZM_TICK_STEP=${zm_tick_step} VM_TICK_MAX=${vm_tick_max} VM_TICK_STEP=${vm_tick_step} SCALE_FACTOR=${scale_factor} PALETTE=${palette}"
    done
done


