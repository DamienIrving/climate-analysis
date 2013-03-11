## Simple netCDF I/O example ## 

import pdb
import cdms2
cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)

pdb.set_trace()

ufile = cdms2.open('/work/dbirving/datasets/Merra/data/ua_Merra_250hPa_monthly_native.nc')
vfile = cdms2.open('/work/dbirving/datasets/Merra/data/va_Merra_250hPa_monthly_native.nc')

u = ufile('ua')
v = vfile('va')

wsp = (u**2 + v**2)**0.5

outfile = cdms2.open('/work/dbirving/temp_data/wsp.nc', 'w')

wsp.id = 'wsp'
wsp.long_name = 'Wind speed at 250 hPa'

outfile.write(wsp)

outfile.close()
