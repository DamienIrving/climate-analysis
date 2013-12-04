
for script in wget*
do
    wget --content-disposition -i $script
done


for year in {1979..2013}
do
    cdo mergetime *.${year}????.* MERRA.prod.assim.tavg1_2d_slv_Nx.${year}.SUB.nc
    rm *.${year}[01]???.*
done
