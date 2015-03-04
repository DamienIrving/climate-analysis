from cdo import *
cdo = Cdo()
import numpy


operator_text = 'cdo ymonavg '
operator_func = eval(operator_text.replace(' ', '.', 1))
infile='/Users/damienirving/Downloads/Data/va_Merra_250hPa_monthly_native.nc'

operator_func(input=infile, returnArray=var_id)

print result