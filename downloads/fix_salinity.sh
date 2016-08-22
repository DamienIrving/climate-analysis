#
# Description: Script fixing salinity units in a bunch of files
#

function usage {
    echo "USAGE: bash $0 outdir input_files"
    echo "   e.g. bash $0 /out/dir/ file1.nc file2.nc ... fileN.nc"
    exit 1
}

outdir=$1
shift
infiles=( $@ )

mkdir -p ${outdir}

for infile in "${infiles[@]}"; do

    filename=`echo ${infile} | rev | cut -d / -f 1 | rev`
    /g/data/r87/dbi599/miniconda2/envs/default/bin/python fix_salinity.py ${infile} ${outdir}${filename}  

done
