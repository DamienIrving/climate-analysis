path=/mnt/meteo0/data/simmonds/dbirving/Merra/data/processed
cdat=/usr/local/uvcdat/1.2.0/bin/cdat

for region in shextropics20 shextropics30 sh
do
    for season in DJF MAM JJA SON
    do
        infile=${path}/eof-sf_Merra_250hPa_monthly-${season}_native-${region}.nc
	outfile=${path}/figures/eof-sf_Merra_250hPa_monthly-${season}_native-${region}.png
        ${cdat} plot_EOF.py ${infile} ${region} --ofile ${outfile} --ticks -1 -0.8 -0.6 -0.4 -0.2 0.0 0.2 0.4 0.6 0.8 1.0
    done
done




