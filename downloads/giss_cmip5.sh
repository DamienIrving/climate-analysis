#
# Description: Download GISS model data from the following ftp site:
#   ftp://giss_cmip5@ftp.nccs.nasa.gov/
#   (no password, just hit return)
#

#
# What's available?
#
# wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/
#
# E2-H
#
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_185001-186912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_187001-188912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_189001-190912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_191001-192912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_193001-194912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_195001-196912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_197001-198912.nc
#
#E2-H_historicalMisc_r1i1p107/   r[1-5]i1p1, r[1-5]i1p106, r[1-5]i1p107
#E2-H_historical_r1i1p1/   r[1-6]i1p[1-3]
#
#thetao_Omon_GISS-E2-H_historicalMisc_r1i1p107_199001-200512.nc
#
#E2-H_historicalGHG_r1i1p1/   r[1-5]i1p1
#E2-H_historicalNat_r1i1p1/   r[1-5]i1p1
#E2-H_historicalExt_r1i1p1/   r[1,3]i1p[1-6]  (p6 has r2 as well)
#
#thetao_Omon_GISS-E2-H_historicalGHG_r1i1p1_200601-201212.nc
#
#E2-H_historicalMisc_r3i1p310/ r[1-5]i1p310
#E2-H_historicalNat_r1i1p3/   r[1-5]i1p3
#
#thetao_Omon_GISS-E2-H_historicalMisc_r3i1p310_199001-200912.nc
#thetao_Omon_GISS-E2-H_historicalMisc_r3i1p310_201001-201212.nc
#
# E2-R
#
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_185001-187512.nc
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_187601-190012.nc
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_190101-192512.nc
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_192601-195012.nc
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_195101-197512.nc
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_197601-200012.nc
#
#E2-R_historicalMisc_r5i1p1/    r[1-5]i1p1, r[1-5]i1p106, r[1-5]i1p107
#E2-R_historical_r1i1p1/   r[1-6]i1p[1-3]
#
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p1_200101-200512.nc
#
#E2-R_historicalGHG_r1i1p1/  r[1-5]i1p1
#E2-R_historicalNat_r1i1p1/  r[1-5]i1p1
#
#thetao_Omon_GISS-E2-R_historicalNat_r1i1p1_200101-200512.nc
#thetao_Omon_GISS-E2-R_historicalNat_r1i1p1_200601-201212.nc
#
#E2-R_historicalExt_r5i1p1/ r[1,3]i1p[1-6]
#
#thetao_Omon_GISS-E2-R_historicalExt_r5i1p1_200601-201212.nc
#
#E2-R_historicalMisc_r5i1p310/ r[1-5]i1p310
#E2-R_historicalNat_r31ip3/ r[1-5]i1p3
#
#thetao_Omon_GISS-E2-R_historicalMisc_r5i1p310_200101-201212.nc
#

e2h_base_years=(185001-186912 187001-188912 189001-190912 191001-192912 193001-194912 195001-196912 197001-198912)
e2r_base_years=(185001-187512 187601-190012 190101-192512 192601-195012 195101-197512 197601-200012)

# Download E2-H data

for run in 1 2 3 4 5
do
    for physics in 1 106 107 310
    do 
        for years in "${e2h_base_years[@]}"
        do
	    wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-H_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-H_historicalMisc_r${run}i1p${physics}_${years}.nc
        done

        if [ ${physics} == 310 ] ; then
            wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-H_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-H_historicalMisc_r${run}i1p${physics}_199001-200912.nc
            wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-H_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-H_historicalMisc_r${run}i1p${physics}_201001-201212.nc
        else
            wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-H_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-H_historicalMisc_r${run}i1p${physics}_199001-200512.nc
        fi
    done
done

# Download E2-R data

for run in 1 2 3 4 5
do
    for physics in 1 106 107 310
    do 
        for years in "${e2r_base_years[@]}"
        do
	    wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-R_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-R_historicalMisc_r${run}i1p${physics}_${years}.nc
        done

        if [ ${physics} == 310 ] ; then
            wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-R_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-R_historicalMisc_r${run}i1p${physics}_200101-201212.nc
        else
            wget ftp://giss_cmip5:@ftp.nccs.nasa.gov/historical/E2-R_historicalMisc_r${run}i1p${physics}/thetao_Omon_GISS-E2-R_historicalMisc_r${run}i1p${physics}_200101-200512.nc
        fi
    done
done





