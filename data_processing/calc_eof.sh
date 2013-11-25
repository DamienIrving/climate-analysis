path=/mnt/meteo0/data/simmonds/dbirving/Merra/data/processed
infile=sf_Merra_250hPa_monthly_native.nc
cdat=/usr/local/uvcdat/1.2.0/bin/cdat

for region in shextropics20 shextropics30 sh
do
    for season in DJF MAM JJA SON
    do
        ${cdat} calc_eof.py --region ${region} --time 1979-01-01 2013-01-01 ${season} --eof_scaling 3 --pc_scaling 1 ${path}/${infile} sf ${path}/eof-sf_Merra_250hPa_monthly-${season}_native-${region}.nc
    done
done
