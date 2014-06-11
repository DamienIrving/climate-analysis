temp_dir=/mnt/meteo0/data/simmonds/dbirving/temp
data_dir=/mnt/meteo0/data/simmonds/dbirving/Merra/data
ufile=${data_dir}/ua_Merra_250hPa_daily_native.nc
vfile=${data_dir}/va_Merra_250hPa_daily_native.nc
outfile=${data_dir}/processed/rws_Merra_250hPa_daily_native.nc


years=(1979 1982 1985 1988 1991 1994 1997 2000 2003 2006 2009 2012)
temp_files=()
for year in "${years[@]}"; do
    end=`expr $year + 2`
    temp_file=${temp_dir}/temp-rws_${year}-${end}.nc
    /usr/local/uvcdat/1.3.0/bin/cdat ~/phd/data_processing/calc_wind_quantities.py rossbywavesource $ufile ua $vfile va ${temp_file} --time ${year}-01-01 ${end}-12-31 none 
    temp_files+=(${temp_file})
done

cdo mergetime ${temp_files[@]} $outfile
rm ${temp_files[@]}
ncatted -O -a axis,time,c,c,T $outfile


