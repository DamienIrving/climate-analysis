#!/bin/bash


ts_file=/work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc

#vp_file=/work/dbirving/datasets/Merra/data/processed/vp_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc
#vp_file=/work/dbirving/datasets/Merra/data/processed/vp_Merra_250hPa_monthly-clim-1981-2010_native.nc
vp_file=/work/dbirving/datasets/Merra/data/processed/vp_Merra_250hPa_monthly_native.nc

uad_file=/work/dbirving/datasets/Merra/data/processed/uad_Merra_250hPa_monthly_native.nc
vad_file=/work/dbirving/datasets/Merra/data/processed/vad_Merra_250hPa_monthly_native.nc

proj=cyl

pticks='-5,-4.5,-4,-3.5,-3,-2.5,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5'
#cbar=blue8,blue7,blue6,blue5,blue4,blue3,blue2,red2,red3,red4,red5,red6,red7,red8
sticks='-9,-7.5,-6,-4.5,-3,-1.5,0,1.5,3,4.5,6,7.5,9'

## Select times to plot ##

# All times #
#years='1979 1980 1981 1982 1983 1984 1985 1986 1987 1988 1989 1990 1991 1992 1993 1994 1995 1996 1997 1998 1999 2000 2001 2002 2003 2004 2005 2006 2007 2008 2009 2010 2011'
#months='Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'
#count=1

# Eastern Pacific El Nino, 1982/83 #
years='1983'
months='Jan'
count=49

#years='1983'
#months='Jun'
#count=54
#
## Central Pacific El Nino, 1990/91 #
#years='1991'
#months='Jan'
#count=145
#
## Central Pacific El Nino, 1994/95 #
#years='1995'
#months='Feb'
#count=194
#
## Eastern Pacific El Nino, 1997/98 #
#years='1997'
#months='Dec'
#count=228
#
## Central Pacific El Nino, 2002/03 #
#years='2002'
#months='Nov'
#count=287
#
#years='2003'
#months='Mar'
#count=291
#
## The Modoki, 2004 #
#years='2004'
#months='Aug'
#count=308
#
## Central Pacific El Nino, 2009/10 #
#years='2009'
#months='Dec'
#count=372
#
#

for y in ${years[*]}
do
    for m in ${months[*]}
    do
        cdo seltimestep,${count} ${ts_file} temp_ts.nc
	cdo seltimestep,${count} ${vp_file} temp_vp.nc
	cdo seltimestep,${count} ${uad_file} temp_uad.nc
	cdo seltimestep,${count} ${vad_file} temp_vad.nc
	outfile=/work/dbirving/processed/spatial_maps/ts-vp_Merra_surface-250hPa_monthly_native_${proj}_${count}.png
        #outfile=test.png
	/opt/cdat/bin/cdat plot_map.py temp_ts.nc ts --title '250hPa_velocity_potential_&_SST_anomaly' --contour --ticks ${pticks} --draw_contours --contour_files temp_vp.nc --contour_variables vp --contour_ticks ${sticks} --image_size 13 --draw_axis --ofile ${outfile} --img_headings ${m}${y} --units Celsius --extend both --colourbar_colour RdBu_r --enso --projection ${proj} --contour_scale 1.e-6 --draw_vectors --uwnd_files temp_uad.nc --uwnd_variables uad --vwnd_files temp_vad.nc --vwnd_variables vad --thin 10
	echo ${outfile}
        rm temp_ts.nc
	rm temp_vp.nc
	rm temp_uad.nc
	rm temp_vad.nc
	count=`expr $count + 1`
    done
done
