The wave envelope extraction is a multi-step process:

1. Calculate the new meridional wind anomaly and output it on a rotated grid:

a. For monthly data

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_vwind_rotation.py 
/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc ua
/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc va 
/work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly-anom-wrt-all_y181x360_np30-270.nc
--north_pole 30 270
--anomaly all all
--grid -90.0 181 1.0 0.0 360 1.0

b. For daily data (because cdat doesn't have daily climatology functions)

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_vwind_rotation.py 
/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_daily_native.nc ua
/work/dbirving/datasets/Merra/data/va_Merra_250hPa_daily_native.nc va 
/work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_daily_y181x360_np30-270.nc
--north_pole 30 270
--grid -90.0 181 1.0 0.0 360 1.0

cdo ydaysub /work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_daily_y181x360_np30-270.nc
-ydayavg /work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_daily_y181x360_np30-270.nc
/work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270.nc


2. Extract the wave envelope (output is still on the grid you gave it - i.e. the rotated grid)

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_envelope.py 
/work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly-anom-wrt-all_y181x360_np30-270.nc vrot
/work/dbirving/datasets/Merra/data/processed/vrot-env-w567_Merra_250hPa_monthly-anom-wrt-all_y181x360_np30-270.nc
--longitude 195 340


3. Plot the wave envelope together with other relevant variables

/usr/local/uvcdat/1.2.0rc1/bin/cdat plot_envelope.py
/work/dbirving/test_data/vrot-env_Merra_250hPa_monthly-anom-wrt-all_y181x360-np30-270.nc
env 30 270 0 0 
/work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc ua
/work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc va
/work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc sf
/work/dbirving/test_data/env-wind-sf_Merra_250hPa_monthly-anom-wrt-all_y181x360-native-np30-270


4. Create the Hovmoller diagram

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_hovmoller.py
/work/dbirving/datasets/Merra/data/processed/vrot-env-w567_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270.nc 
env absolute 14
/work/dbirving/datasets/Merra/data/processed/hov-vrot-env-w567_Merra_250hPa_daily-anom-wrt-all_y181x360_np30-270_absolute14_lon180-340.nc
--latitude -15 15 --longitude 180 340


5. Implement the ROIM method

matlab &
then run test_roim.m


6. Calculate the climatological statistics

???? 



##. Unit testing

/home/dbirving/testing/unittest_coordinate_rotation.py
/home/dbirving/testing/unittest_vwind_rotation.py

##. Visualising the process

/home/dbirving/testing/plot_vwind_rotation.py
/home/dbirving/testing/plot_coordinate_rotation.py    
