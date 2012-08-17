#!/bin/bash


ts_file=/work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc
sf_file=/work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc

proj=cyl

pticks='-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5'
#cbar=blue8,blue7,blue6,blue5,blue4,blue3,blue2,red2,red3,red4,red5,red6,red7,red8
sticks='-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30'

#years='1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011'
#months='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'
#count=1

years='1983'
months='Jan'
count=49

for y in ${years[*]}
do
    for m in ${months[*]}
    do
        cdo seltimestep,${count} ${ts_file} temp_ts.nc
	cdo seltimestep,${count} ${sf_file} temp_sf.nc
	#outfile=/work/dbirving/processed/plots/ts-sf_Merra_surface-250hPa_monthly-anom-wrt-1981-2010_native_${proj}_${count}.png
        outfile=test.png
	/opt/cdat/bin/cdat plot_map.py temp_ts.nc ts --title '250hPa_streamfunction_anomaly_&_SST_anomaly' --contour --ticks ${pticks} --draw_contours --contour_files temp_sf.nc --contour_variables sf --contour_ticks ${sticks} --image_size 13 --draw_axis --ofile ${outfile} --img_headings ${m}${y} --units Celsius --extend both --colourbar_colour RdBu_r --enso --projection ${proj} --contour_scale 1.e-6
	echo ${outfile}
        rm temp_ts.nc
	rm temp_sf.nc
	
	count=`expr $count + 1`
    done
done
