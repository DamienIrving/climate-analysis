#
# Description: Script for plotting ensemble results for each basin
#

function usage {
    echo "USAGE: bash $0 "
    echo "  -n option for dry run"
    exit 1
}


dry_run='no'
while getopts ":n" opt; do
  case $opt in
    n)
      dry_run='yes'
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done


python='/g/data/r87/dbi599/miniconda2/envs/default/bin/python'


# historical zonal plots

experiment='historical'
for region in atlantic pacific indian globe; do

    for variable in thetao so; do

        if [[ ${variable} == 'so' ]] ; then
            long_name=sea_water_salinity
            ticks="--ticks 3.5 0.5 --ticks 5 1"
            palette='BrBG_r'
        elif [[ ${variable} == 'thetao' ]] ; then
            long_name=sea_water_potential_temperature
            ticks="--ticks 15 3 --ticks 20 4"
            palette='RdBu_r'
        fi

        data_files="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_NorESM1-M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"

        outfile=/g/data/r87/dbi599/figures/ocean_trend_ensembles/${experiment}/${variable}-maps-time-trend-zonal-mean-${region}_Oyr_ensemble_${experiment}_r1i1p1_1950-01-01_2000-12-31.png

        climatology_files="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_NorESM1-M_${experiment}_r1i1p1_all.nc"

    if [[ ${dry_run} == 'yes' ]] ; then
        echo  ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 1 2 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
    else
         ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 1 2 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
        echo ${outfile}
    fi

    done
done



# historicalGHG zonal plots

experiment='historicalGHG'
for region in atlantic pacific indian globe; do

    for variable in thetao so; do

        if [[ ${variable} == 'so' ]] ; then
            long_name=sea_water_salinity
            ticks="--ticks 3.5 0.5 --ticks 5 1"
            palette='BrBG_r'
        elif [[ ${variable} == 'thetao' ]] ; then
            long_name=sea_water_potential_temperature
            ticks="--ticks 15 3 --ticks 25 5"
            palette='RdBu_r'
        fi

        data_files="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_NorESM1-M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"

        outfile=/g/data/r87/dbi599/figures/ocean_trend_ensembles/${experiment}/${variable}-maps-time-trend-zonal-mean-${region}_Oyr_ensemble_${experiment}_r1i1p1_1950-01-01_2000-12-31.png

        climatology_files="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_NorESM1-M_${experiment}_r1i1p1_all.nc"

    if [[ ${dry_run} == 'yes' ]] ; then
        echo  ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 1 2 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
    else
         ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 1 2 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
        echo ${outfile}
    fi

    done
done



# historicalAA zonal plots

experiment='historicalMisc'
for region in atlantic pacific indian globe; do

    for variable in thetao so; do

        if [[ ${variable} == 'so' ]] ; then
            long_name=sea_water_salinity
            ticks="--ticks 3.5 0.5 --ticks 5 1"
            palette='BrBG_r'
        elif [[ ${variable} == 'thetao' ]] ; then
            long_name=sea_water_potential_temperature
            ticks="--ticks 15 3 --ticks 25 5"
            palette='RdBu_r'
        fi

        data_files="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p3/${variable}-maps-time-trend_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p3_1950-01-01_2000-12-31.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_NorESM1-M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"

        outfile=/g/data/r87/dbi599/figures/ocean_trend_ensembles/historicalAA/${variable}-maps-time-trend-zonal-mean-${region}_Oyr_ensemble_historicalAA_r1i1p1_1950-01-01_2000-12-31.png

        climatology_files="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p3/${variable}-maps-clim_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p3_all.nc /g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_NorESM1-M_${experiment}_r1i1p1_all.nc"

    if [[ ${dry_run} == 'yes' ]] ; then
        echo  ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 1 2 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
    else
         ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 1 2 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
        echo ${outfile}
    fi

    done
done
