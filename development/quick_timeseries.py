import xray
import matplotlib.pyplot as plt
import numpy

dset_cdat = xray.open_dataset('sam_ERAInterim_surface_030day-runmean_native.nc')
dset_xray = xray.open_dataset('sam_ERAInterim_surface_030day-runmean_native_xray.nc')


data_cdat = dset_cdat['sam'].values[0:200]
data_xray = dset_xray['sam'].values[0:200]
xaxis = numpy.arange(0, len(data_cdat))

plt.plot(xaxis, data_cdat)
plt.plot(xaxis, data_xray)

plt.savefig('test.png')
