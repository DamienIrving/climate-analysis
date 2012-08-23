#!/bin/bash

Proj=`basename $0 .sh`

ScriptDir=`dirname $0`

file=""

nargs=4
function manual {
    echo "Usage: ${Proj} [-h] type year month projection"
    echo "Where: -h          = Display this help/usage message and exit"
    echo "       type        = Type of plot [raw,anomaly]"
    echo "       year        = Year to plot [e.g. 1983 OR all]"
    echo "       month       = Month to plot [e.g. Jan OR all]"
    echo "       projection  = Map projection [cyl]"
    echo ""
    echo "List of interesting month/years (peak listed)"
    echo "       Eastern Pacific El Nino, 1982/83: Jan,1983 or Jun,1983"
    echo "       Central Pacific El Nino, 1990/91: Jan,1991"
    echo "       Central Pacific El Nino, 1994/95: Feb,1995"
    echo "       Eastern Pacific El Nino, 1997/98: Dec,1997"
    echo "       Central Pacific El Nino, 2002/03: Nov,2002 or Mar,2003"
    echo "       The Modoki             , 2004   : Aug,2004"
    echo "       Central Pacific El Nino, 2009/10: Dec,2009"; }

# Parse the command line options

set -- `getopt "h:" "$@"`

for key in "$@"
do
    case $key in
        --)
            shift
            break
            ;;
        -h)
            fnUsage
            exit 0
            ;;
    esac
done

if [ $nargs -ne $# ] ; then
    manual
    exit 1
fi


### Read the input variables ###

contour_type=$1 
years=$2
months=$3
proj=$4
#variables=(`echo $1 | tr ',' ' '`)


## Define input files and relevant plot characteristics ##

inpath=/work/dbirving/datasets/Merra/data
outpath=/work/dbirving/processed/spatial_maps

if [ ${contour_type} = 'raw' ] ; then
    ts_file=${inpath}/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc
    sf_file=${inpath}/processed/sf_Merra_250hPa_monthly_native.nc
    cbar=RdBu_r
    pticks='-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5'
    sticks='-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30'
    title='250hPa_streamfunction_&_SST_anomaly'
    outfile_start=${outpath}/ts-sf_Merra_surface-250hPa_monthly_native
elif [ ${contour_type} = 'anomaly' ] ; then
    ts_file=${inpath}/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc
    sf_file=${inpath}/processed/sf_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc
    cbar=RdBu_r
    pticks='-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5'
    sticks='-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30'
    title='250hPa_streamfunction_anomaly_&_SST_anomaly'
    outfile_start=${outpath}/ts-sf_Merra_surface-250hPa_monthly-anom-wrt-1981-2010_native
else
    echo 'Type of plot does not exist'
fi


## Define the months to plot ##

if [ ${months} = 'Jan' ] ; then
    month_num=1
elif [ ${months} = 'Feb' ] ; then
    month_num=2
elif [ ${months} = 'Mar' ] ; then
    month_num=3
elif [ ${months} = 'Apr' ] ; then
    month_num=4
elif [ ${months} = 'May' ] ; then
    month_num=5
elif [ ${months} = 'Jun' ] ; then
    month_num=6
elif [ ${months} = 'Jul' ] ; then
    month_num=7
elif [ ${months} = 'Aug' ] ; then
    month_num=8
elif [ ${months} = 'Sep' ] ; then
    month_num=9
elif [ ${months} = 'Oct' ] ; then
    month_num=10
elif [ ${months} = 'Nov' ] ; then
    month_num=11
elif [ ${months} = 'Dec' ] ; then
    month_num=12
elif [ ${months} = 'all' ] ; then
    months='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'
else
    echo 'Invalid month'
fi

## Define the years to plot ##

if [ ${years} = 'all' ] ; then
    count=1
    years='1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011'
else
    diff=`expr ${years} - 1979`
    year_num=`expr 12 \\* ${diff}`
    count=`expr ${year_num} + ${month_num}`
fi


## Create the plot ##

for y in ${years[*]}
do
    for m in ${months[*]}
    do
        cdo seltimestep,${count} ${ts_file} temp_ts.nc
	cdo seltimestep,${count} ${sf_file} temp_sf.nc
	outfile=${outfile_start}_${proj}_${count}.png
	/opt/cdat/bin/cdat plot_map.py temp_ts.nc ts --title ${title} --contour --ticks ${pticks} --draw_contours --contour_files temp_sf.nc --contour_variables sf --contour_ticks ${sticks} --image_size 13 --draw_axis --ofile ${outfile} --img_headings ${m}${y} --units Celsius --extend both --colourbar_colour ${cbar} --enso --projection ${proj} --contour_scale 1.e-6 
	echo ${outfile}
        rm temp_ts.nc
	rm temp_sf.nc
	count=`expr $count + 1`
    done
done
