#!/bin/bash
# $ Id: $
#
# Author: David Kent (David.Kent@csiro.au)
# Date:   16/07/2011
#
# Description: Calculates EOFs and compiles all the desired information into a
#              single NetCDF file. Uses CDO for the calculation. The spatial
#              distributions, the time-series and the explained variance are all
#              add to the output file.
#
# Copyright 2011, CSIRO
#

version="$Revision: 327 $"

nargs=4
function usage {
    echo "USAGE: $0 n var input output"
    echo "    n:          Number of EOFs to calculate"
    echo "    var:        Variable base name"
    echo "    input:      Input file"
    echo "    output:     Output file"
    echo ""
    echo "    This routine only handles missing values if they"
    echo "    are in the same spatial location at every time step"
    echo ""
    echo "    Input data are assumed to be an anomaly timeseries"
    exit 1
}

if [ $nargs -ne $# ] ; then
  usage
fi

np=$1
varbase=$2
infile=$3
outfile=$4

if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi

if [ -f $outfile ] ; then
   echo "Outfile exists. Skipping: " $outfile
   exit 2
fi

TMPDIR=/work/dbirving/temp_data
MYDIR=/home/dbirving/data_processing


# Select the desired region and time period

region_flag=false
start_flag=false
end_flag=false
tmpregfile=$TMPDIR/tmp_reg.nc
tmptimefile=$TMPDIR/tmp_time.nc
while getopts ":r:t:" opt; do
  case $opt in
    r)
      $MYDIR/named_region.sh $OPTARG ${infile} ${tmpregfile}  
      region_flag=true
      ;;
    s)
      start_date=$OPTARG
      start_flag=true
      ;;
    e)
      if start_flag ; then
        end_flag=true
      else
        echo "Must use both start (-s) and end (-e) date options" >&2
        exit 1
      fi
      end_date=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;  
  esac
done
shift $((OPTIND-1))

if (( region_flag )) && (( end_flag )) ; then
  cdo seldate,${start_date},${end_date} ${tempregfile} ${tmptimefile}
  infile=${tmptimefile}
elif region_flag ; then
  infile=${tmpregfile}
fi


### Get the lat/lon varaible names....
griddes=$TMPDIR/cdo_griddes.txt
cdo griddes ${infile} > ${griddes} 2> /dev/null
xname=`grep xname ${griddes} | sed -e"s/.*= \(.*\)$/\1/"`
yname=`grep yname ${griddes} | sed -e"s/.*= \(.*\)$/\1/"`

# Get the time variable name....
tvar=`ncdump -h ${infile} | grep calendar | sed -n "s/^		\([a-zA-Z]*\)\:calendar.*$/\1/p"`

# Set file names
export CDO_FILE_SUFFIX=.nc
tmpcdoeof1=$TMPDIR/cdo_eof1_$$.nc
tmpcdoeof2=$TMPDIR/cdo_eof2_$$.nc
tmpcdoeofcoeff=$TMPDIR/cdo_eof3_$$_
tmpperval=$TMPDIR/cdo_percval_$$.nc

cdo eof,${np} ${infile} ${tmpcdoeof1} ${tmpcdoeof2} 2> /dev/null
cdo -f nc eofcoeff ${tmpcdoeof2} ${infile} ${tmpcdoeofcoeff} 2> /dev/null

# Calculate the percent variance explained
tmppercvar=$TMPDIR/cdo_eof_perc_var_$$.nc
cdo mulc,100 -div ${tmpcdoeof1} -timsum ${tmpcdoeof1} ${tmppercvar} 2> /dev/null

# Work out the variable list
# Looks to see if the variable passed as an argument exists. If not, defaults to
# all variables in the file....
testf=$TMPDIR/test$$.nc
cdo selname,${varbase} ${infile} ${testf} 2> /dev/null
if [ 0 -eq $? ] ; then
    vars=${varbase}
else
    vars=`cdo showname ${infile} 2> /dev/null`
fi
rm -f ${testf}

# Process each EOF sequentially
for n in `seq ${np}`; do

  for var in ${vars} ; do
    # Get the time-series
    npz=`expr $n - 1`
    nf=`printf %05d ${npz}`
    ncrename -v ${var},${var}_ts_eof${n} ${tmpcdoeofcoeff}${nf}.nc ${tmpcdoeofcoeff}${nf}_rename.nc
    if [ 0 -ne $? ] ; then
      exit 1
    fi
    #ncwa -C -v ${tvar},${var}_ts_eof${n} -a ${yname},${xname} ${tmpcdoeofcoeff}${nf}_rename.nc ${tmpcdoeofcoeff}${nf}_nospace.nc
    ncwa -C -v ${tvar},${var}_ts_eof${n} -a lon,lat ${tmpcdoeofcoeff}${nf}_rename.nc ${tmpcdoeofcoeff}${nf}_nospace.nc
    if [ 0 -ne $? ] ; then
      exit 1
    fi
    ncatted -h -a long_name,${var}_ts_eof${n},o,c,"eof_time_series" ${tmpcdoeofcoeff}${nf}_nospace.nc
    ncatted -h -a standard_name,${var}_ts_eof${n},o,c,"eof_of_sea_surface_temperature" ${tmpcdoeofcoeff}${nf}_nospace.nc
    ncatted -h -a name,${var}_ts_eof${n},o,c,"eof_of_sea_surface_temperature" ${tmpcdoeofcoeff}${nf}_nospace.nc
    ncatted -h -a cell_methods,${var}_ts_eof${n},d,, ${tmpcdoeofcoeff}${nf}_nospace.nc
    ncks -A ${tmpcdoeofcoeff}${nf}_nospace.nc ${outfile}
    if [ 0 -ne $? ] ; then
      exit 1
    fi
  
    # Get the spatial pattern
    ncwa -a ${tvar} -d ${tvar},${npz} ${tmpcdoeof2} ${tmpcdoeof2}_${n}.nc
    if [ 0 -ne $? ] ; then
      exit 1
    fi
    ncrename -v ${var},${var}_spatial_eof${n} ${tmpcdoeof2}_${n}.nc
    if [ 0 -ne $? ] ; then
      exit 1
    fi
    ncatted -h -a long_name,${var}_spatial_eof${n},o,c,"eof_spatial_pattern" ${tmpcdoeof2}_${n}.nc
    ncatted -h -a standard_name,${var}_spatial_eof${n},o,c,"eof_of_sea_surface_temperature" ${tmpcdoeof2}_${n}.nc
    ncatted -h -a name,${var}_spatial_eof${n},o,c,"eof_of_sea_surface_temperature" ${tmpcdoeof2}_${n}.nc
    ncatted -h -a cell_methods,${var}_spatial_eof${n},d,, ${tmpcdoeof2}_${n}.nc
    ncks -C -v${var}_spatial_eof${n},${yname},${xname} -A ${tmpcdoeof2}_${n}.nc ${outfile}
    if [ 0 -ne $? ] ; then
      exit 1
    fi
  
    # Get the percent var explained
    ncwa -d ${tvar},${npz} ${tmppercvar} ${tmpperval}
    if [ 0 -ne $? ] ; then
      exit 1
    fi
    ncrename -v ${var},${var}_perc_eof${n} ${tmpperval}
    if [ 0 -ne $? ] ; then
      exit 1
    fi
    ncatted -h -a long_name,${var}_perc_eof${n},o,c,"eof_percent_explained" ${tmpperval}
    ncatted -h -a standard_name,${var}_perc_eof${n},o,c,"eof_of_sea_surface_temperature" ${tmpperval}
    ncatted -h -a name,${var}_perc_eof${n},o,c,"eof_of_sea_surface_temperature" ${tmpperval}
    ncatted -h -a units,${var}_perc_eof${n},o,c,"percent" ${tmpperval}
    ncks -C -v${var}_perc_eof${n} -A ${tmpperval} ${outfile}
    if [ 0 -ne $? ] ; then
      exit 1
    fi

    rm ${tmpperval} ${tmpcdoeof2}_*nc ${tmpcdoeofcoeff}?????_nospace.nc ${tmpcdoeofcoeff}${nf}_rename.nc
  done
done

rm ${tmpcdoeof1} ${tmpcdoeof2} ${tmppercvar}

if region_flag ; then
  rm ${tempregfile} 
fi

if end_flag ; then
  rm ${temptimefile} 
fi
 

# Set some metadata
ncks -h -A -x $infile $outfile
ncatted -h -a history,global,a,c,"\nEOFs calculated using $0 ($version) on `date`" $outfile

exit 0
