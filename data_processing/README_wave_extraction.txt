The wave envelope extraction is a multi-step process:

1. Calculate the new meridional wind anomaly and output it on a rotated grid:

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_vwind_rotation.py 
/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc ua
/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc va 
/work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360_np30-270.nc
--north_pole 30 270
--anomaly all all
--grid -90.0 181 1.0 0.0 360 1.0

2. Extract the wave envelope (output is still on the grid you gave it - i.e. the rotated grid)

/usr/local/uvcdat/1.2.0rc1/bin/cdat calc_envelope.py 
/work/dbirving/datasets/Merra/data/processed/vrot_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360_np30-270.nc vrot
/work/dbirving/datasets/Merra/data/processed/vrot-env-w567_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360_np30-270.nc

3. Plot the wave envelope together with other relevant variables

/usr/local/uvcdat/1.2.0rc1/bin/cdat plot_envelope.py
/work/dbirving/test_data/vrot-env_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360-np30-270.nc
env 30 270 0 0 
/work/dbirving/datasets/Merra/data/processed/ua_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc ua
/work/dbirving/datasets/Merra/data/processed/va_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc va
/work/dbirving/datasets/Merra/data/processed/sf_Merra_250hPa_monthly-anom-wrt-1979-2011_native.nc sf
/work/dbirving/test_data/env-wind-sf_Merra_250hPa_monthly-anom-wrt-1979-2011_y181x360-native-np30-270



#. Unit testing

/home/dbirving/testing/unittest_coordinate_rotation.py
/home/dbirving/testing/unittest_vwind_rotation.py

#. Visualising the process

/home/dbirving/testing/plot_vwind_rotation.py
/home/dbirving/testing/plot_coordinate_rotation.py    
