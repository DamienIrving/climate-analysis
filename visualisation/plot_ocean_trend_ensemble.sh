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
            ccsm_ticks="--ticks 2.0 0.4"
            fgoals_ticks="--ticks 2.5 0.5"
            gfdl_cm_ticks="--ticks 2.5 0.5"
            gfdl_esm_ticks="--ticks 3.75 0.75"
            ipsl_ticks="--ticks 3.75 0.75"
            noresm_ticks="--ticks 5 1"
            palette='BrBG_r'
        elif [[ ${variable} == 'thetao' ]] ; then
            long_name=sea_water_potential_temperature
            ccsm_ticks="--ticks 15 3"
            fgoals_ticks="--ticks 15 3"
            gfdl_cm_ticks="--ticks 15 3"
            gfdl_esm_ticks="--ticks 25 5"
            ipsl_ticks="--ticks 15 3"
            noresm_ticks="--ticks 20 4"
            palette='RdBu_r'
        fi

        ticks="${ccsm_ticks} ${fgoals_ticks} ${gfdl_cm_ticks} ${gfdl_esm_ticks} ${ipsl_ticks} ${noresm_ticks}"

        ccsm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCAR/CCSM4/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-time-trend_Oyr_CCSM4_${experiment}_ensmean-i1p1_1950-01-01_2000-12-31.nc"
        fgoals_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/LASG-CESS/FGOALS-g2/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_FGOALS-g2_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        gfdl_cm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-CM3/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-time-trend_Oyr_GFDL-CM3_${experiment}_ensmean-i1p1_1950-01-01_2000-12-31.nc"
        gfdl_esm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-ESM2M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_GFDL-ESM2M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        ipsl_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        noresm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_NorESM1-M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        
        data_files="${ccsm_file} ${fgoals_file} ${gfdl_cm_file} ${gfdl_esm_file} ${ipsl_file} ${noresm_file}"

        outfile=/g/data/r87/dbi599/figures/ocean_trend_ensembles/${experiment}/${variable}-maps-time-trend-zonal-mean-${region}_Oyr_ensemble_${experiment}_i1p1_1950-01-01_2000-12-31.png

        ccsm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCAR/CCSM4/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-clim_Oyr_CCSM4_${experiment}_ensmean-i1p1_all.nc"
        fgoals_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/LASG-CESS/FGOALS-g2/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_FGOALS-g2_${experiment}_r1i1p1_all.nc"
        gfdl_cm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-CM3/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-clim_Oyr_GFDL-CM3_${experiment}_ensmean-i1p1_all.nc"
        gfdl_esm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-ESM2M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_GFDL-ESM2M_${experiment}_r1i1p1_all.nc"
        ipsl_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_all.nc"
        noresm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_NorESM1-M_${experiment}_r1i1p1_all.nc"
        
        climatology_files="${ccsm_clim} ${fgoals_clim} ${gfdl_cm_clim} ${gfdl_esm_clim} ${ipsl_clim} ${noresm_clim}"

    if [[ ${dry_run} == 'yes' ]] ; then
        echo  ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 2 3 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
    else
         ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 2 3 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
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
            ccsm_ticks="--ticks 3.0 0.6"
            fgoals_ticks="--ticks 3.0 0.6"
            gfdl_cm_ticks="--ticks 3.75 0.75"
            gfdl_esm_ticks="--ticks 5 1"
            ipsl_ticks="--ticks 3.75 0.75"
            noresm_ticks="--ticks 5 1"
            palette='BrBG_r'
        elif [[ ${variable} == 'thetao' ]] ; then
            long_name=sea_water_potential_temperature
            ccsm_ticks="--ticks 15 3"
            fgoals_ticks="--ticks 15 3"
            gfdl_cm_ticks="--ticks 20 4"
            gfdl_esm_ticks="--ticks 15 3"
            ipsl_ticks="--ticks 15 3"
            noresm_ticks="--ticks 25 5"
            palette='RdBu_r'
        fi

        ticks="${ccsm_ticks} ${fgoals_ticks} ${gfdl_cm_ticks} ${gfdl_esm_ticks} ${ipsl_ticks} ${noresm_ticks}"

        ccsm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCAR/CCSM4/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-time-trend_Oyr_CCSM4_${experiment}_ensmean-i1p1_1950-01-01_2000-12-31.nc"
        fgoals_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/LASG-CESS/FGOALS-g2/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_FGOALS-g2_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        gfdl_cm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-CM3/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-time-trend_Oyr_GFDL-CM3_${experiment}_ensmean-i1p1_1950-01-01_2000-12-31.nc"
        gfdl_esm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-ESM2M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_GFDL-ESM2M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        ipsl_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"
        noresm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_NorESM1-M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"

        data_files="${ccsm_file} ${fgoals_file} ${gfdl_cm_file} ${gfdl_esm_file} ${ipsl_file} ${noresm_file}"

        outfile=/g/data/r87/dbi599/figures/ocean_trend_ensembles/${experiment}/${variable}-maps-time-trend-zonal-mean-${region}_Oyr_ensemble_${experiment}_i1p1_1950-01-01_2000-12-31.png

        ccsm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCAR/CCSM4/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-clim_Oyr_CCSM4_${experiment}_ensmean-i1p1_all.nc"
        fgoals_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/LASG-CESS/FGOALS-g2/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_FGOALS-g2_${experiment}_r1i1p1_all.nc"
        gfdl_cm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-CM3/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-clim_Oyr_GFDL-CM3_${experiment}_ensmean-i1p1_all.nc"
        gfdl_esm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-ESM2M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_GFDL-ESM2M_${experiment}_r1i1p1_all.nc"
        ipsl_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p1_all.nc"
        noresm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_NorESM1-M_${experiment}_r1i1p1_all.nc"

        climatology_files="${ccsm_clim} ${fgoals_clim} ${gfdl_cm_clim} ${gfdl_esm_clim} ${ipsl_clim} ${noresm_clim}"

    if [[ ${dry_run} == 'yes' ]] ; then
        echo  ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 2 3 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
    else
         ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 2 3 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
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
            ccsm_ticks="--ticks 2.0 0.4"
            fgoals_ticks="--ticks 2.0 0.4"
            gfdl_cm_ticks="--ticks 3.75 0.75"
            gfdl_esm_ticks="--ticks 5 1"
            ipsl_ticks="--ticks 3.75 0.75"
            noresm_ticks="--ticks 5 1"
            palette='BrBG_r'
        elif [[ ${variable} == 'thetao' ]] ; then
            long_name=sea_water_potential_temperature
            ccsm_ticks="--ticks 7.5 1.5"
            fgoals_ticks="--ticks 7.5 1.5"
            gfdl_cm_ticks="--ticks 20 4"
            gfdl_esm_ticks="--ticks 15 3"
            ipsl_ticks="--ticks 15 3"
            noresm_ticks="--ticks 25 5"
            palette='RdBu_r'
        fi

        ticks="${ccsm_ticks} ${fgoals_ticks} ${gfdl_cm_ticks} ${gfdl_esm_ticks} ${ipsl_ticks} ${noresm_ticks}"

        ccsm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCAR/CCSM4/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p10/${variable}-maps-time-trend_Oyr_CCSM4_${experiment}_ensmean-i1p10_1950-01-01_2000-12-31.nc"
        fgoals_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/LASG-CESS/FGOALS-g2/${experiment}/yr/ocean/${variable}-maps/r2i1p1/${variable}-maps-time-trend_Oyr_FGOALS-g2_${experiment}_r2i1p1_1950-01-01_2000-12-31.nc"
        gfdl_cm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-CM3/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-time-trend_Oyr_GFDL-CM3_${experiment}_ensmean-i1p1_1950-01-01_2000-12-31.nc"
        gfdl_esm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-ESM2M/${experiment}/yr/ocean/${variable}-maps/r1i1p5/${variable}-maps-time-trend_Oyr_GFDL-ESM2M_${experiment}_r1i1p5_1950-01-01_2000-12-31.nc"
        ipsl_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p3/${variable}-maps-time-trend_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p3_1950-01-01_2000-12-31.nc"
        noresm_file="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-time-trend_Oyr_NorESM1-M_${experiment}_r1i1p1_1950-01-01_2000-12-31.nc"

        data_files="${ccsm_file} ${fgoals_file} ${gfdl_cm_file} ${gfdl_esm_file} ${ipsl_file} ${noresm_file}"

        outfile=/g/data/r87/dbi599/figures/ocean_trend_ensembles/historicalAA/${variable}-maps-time-trend-zonal-mean-${region}_Oyr_ensemble_historicalAA_i1_1950-01-01_2000-12-31.png

        ccsm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCAR/CCSM4/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p10/${variable}-maps-clim_Oyr_CCSM4_${experiment}_ensmean-i1p10_all.nc"
        fgoals_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/LASG-CESS/FGOALS-g2/${experiment}/yr/ocean/${variable}-maps/r2i1p1/${variable}-maps-clim_Oyr_FGOALS-g2_${experiment}_r2i1p1_all.nc"
        gfdl_cm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-CM3/${experiment}/yr/ocean/${variable}-maps/ensmean-i1p1/${variable}-maps-clim_Oyr_GFDL-CM3_${experiment}_ensmean-i1p1_all.nc"
        gfdl_esm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NOAA-GFDL/GFDL-ESM2M/${experiment}/yr/ocean/${variable}-maps/r1i1p5/${variable}-maps-clim_Oyr_GFDL-ESM2M_${experiment}_r1i1p5_all.nc"
        ipsl_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/IPSL/IPSL-CM5A-LR/${experiment}/yr/ocean/${variable}-maps/r1i1p3/${variable}-maps-clim_Oyr_IPSL-CM5A-LR_${experiment}_r1i1p3_all.nc"
        noresm_clim="/g/data/r87/dbi599/drstree/CMIP5/GCM/NCC/NorESM1-M/${experiment}/yr/ocean/${variable}-maps/r1i1p1/${variable}-maps-clim_Oyr_NorESM1-M_${experiment}_r1i1p1_all.nc"

        climatology_files="${ccsm_clim} ${fgoals_clim} ${gfdl_cm_clim} ${gfdl_esm_clim} ${ipsl_clim} ${noresm_clim}"

    if [[ ${dry_run} == 'yes' ]] ; then
        echo  ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 2 3 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
    else
         ${python} ~/climate-analysis/visualisation/plot_ocean_trend_ensemble.py ${data_files[@]} ${long_name} ${region} 2 3 ${outfile} --palette ${palette} --climatology_files ${climatology_files[@]} ${ticks[@]} --scale_factor 3
        echo ${outfile}
    fi

    done
done
