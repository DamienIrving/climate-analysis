

nargs=1
function usage {
    echo "USAGE: bash $0 var"
    echo "   var:       Variable to plot as colorbar [env, sic, tas]"
    echo "   e.g. bash $0 env"
    exit 1
}

if [ $nargs -ne $# ] ; then
  usage
fi

var=$1

if [ "${var}" == "env" ] ; then
    longvar=env
    units=ms-1
    ticks="0 1 2 3 4 5 6 7 8 9 10 11 12"
    palette=Oranges
    extension=max
elif [ "${var}" == "tas" ] ; then
    longvar=tas-anom
    units=Celcius
    ticks="-4 -3.5 -3 -2.5 -2 -1.5 -1 -0.5 0 0.5 1 1.5 2 2.5 3 3.5 4"
    palette=RdBu_r
    extension=both
elif [ "${var}" == "sic" ] ; then
    longvar=sic-anom
    units=fraction
    ticks="-0.4 -0.35 -0.3 -.25 -0.2 -0.15 -0.1 -0.05 0.05 0.1 0.15 0.2 0.25 0.3 0.35 0.4"
    palette=RdBu_r
    extension=both
else
    usage
fi


/usr/local/uvcdat/1.3.0/bin/cdat plot_composite.py ${var} /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_DEC.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JAN.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_FEB.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_MAR.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_APR.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_MAY.nc  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JUN.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JUL.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_AUG.nc  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_SEP.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_OCT.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_NOV.nc  --ticks ${ticks} --units ms-1 --contour_var sf --contour_files /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_DEC.nc  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JAN.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_FEB.nc  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_MAR.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_APR.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_MAY.nc  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JUN.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JUL.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_AUG.nc  /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_SEP.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_OCT.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_NOV.nc  --contour_ticks -30 -27.5 -25 -22.5 -20 -17.5 -15 -12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5 15 17.5 20 22.5 25 27.5 30 --headings DJF JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV --projection spstere --palette ${palette} --extend ${extension} --dimensions 4 3 --raphael_boxes --ofile test_${var}_monthly.png --image_size 12

/usr/local/uvcdat/1.3.0/bin/cdat plot_composite.py ${var} /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_DJF.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_MAM.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JJA.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/${longvar}-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_SON.nc  --ticks ${ticks} --units ms-1 --contour_var sf --contour_files /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_DJF.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_MAM.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_JJA.nc /mnt/meteo0/data/simmonds/dbirving/Merra/data/processed/rwid/zw3/sf-zonal-anom-zw3-composite-mean_Merra_250hPa_30day-runmean_r360x181-mermax-lat70S40S_env-w234-va-ampmin7-extentmin300-360_SON.nc  --contour_ticks -30 -27.5 -25 -22.5 -20 -17.5 -15 -12.5 -10 -7.5 -5 -2.5 0 2.5 5 7.5 10 12.5 15 17.5 20 22.5 25 27.5 30 --headings DJF MAM JJA SON --projection spstere --palette ${palette} --extend ${extension} --dimensions 2 2 --raphael_boxes --ofile test_${var}_seasonal.png --image_size 12
 
