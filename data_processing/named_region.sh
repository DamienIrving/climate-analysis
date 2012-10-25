#!/bin/bash
# $ Id: $
#
# Author: ( @csiro.au)
# Date:   16/02/2011
#
# Description: 
#
# Copyright 2011, CSIRO
#

nargs=3
function usage {
    echo "USAGE: $0 {region} {input} {output}"
    echo "    region:     Region to extract"
    echo "    input:      Input file"
    echo "    output:     Output file"
    exit 1
}

if [ $nargs -ne $# ] ; then
  usage
fi

region=$1
infile=$2
outfile=$3

if [ ! -f $infile ] ; then
    echo "Input file doesn't exist: " $infile
    usage
fi

if [ -f $outfile ] ; then
   echo "Outfile exists. Skipping: " $outfile
   exit 2
fi

inbase=`basename $infile`
extn=`expr match "${inbase}" '.*\.\(.*\)'`
if [ $extn = 'xml' ] ; then
  tmp_in=$TMPDIR/xml_concat.$$.nc   # If I want to use this, I should override the default $TMPDIR
  python $CCT/processing/cdml_cat/xml_to_nc.py None $infile $tmp_in   # xml_to_nc.py is in my git_repo
  infile=$tmp_in
fi

if [ ! -f $infile ] ; then
    echo "Conversion of file from XML catalogue failed."
    exit 1
fi

case ${region} in
    trop_ind_pac )
      box="39,280,-25,25"
      cdo sellonlatbox,${box} $infile $outfile ;;
    eqpacific )
      box="120,280,-30,30"
      cdo sellonlatbox,${box} $infile $outfile ;;
    indian )
      box="39,120,-25,25"
      cdo sellonlatbox,${box} $infile $outfile ;;
    indo-pac )
      box="45,260,-55,-5"
      cdo sellonlatbox,${box} $infile $outfile ;;
    southern )
      box="0,360,-70,-20"
      cdo sellonlatbox,${box} $infile $outfile ;;
    sh )
      box="0,360,-90,0"
      cdo sellonlatbox,${box} $infile $outfile ;;
    nh )
      box="0,360,0,90"
      cdo sellonlatbox,${box} $infile $outfile ;;
    australia )
      box="110,156,-50,-5"
      cdo sellonlatbox,${box} $infile $outfile ;;
    * )
      regionfile=/home/dbirving/data_processing/regions/${region}.txt   
      if [ -f $regionfile ] ; then
          cdo maskregion,$regionfile $infile $outfile
      else
        echo "Unknown region: $region"
        exit 1
      fi
      ;;
esac

#rm $infile

exit 0
