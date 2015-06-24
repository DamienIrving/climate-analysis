## Input: file_cdat file_xray var

import sys
import xray
import matplotlib.pyplot as plt
import numpy

ifile_cdat = sys.argv[1]
ifile_xray = sys.argv[2]
var = sys.argv[3]

dset_cdat = xray.open_dataset(ifile_cdat)
dset_xray = xray.open_dataset(ifile_xray)


data_cdat = dset_cdat[var].values[0:200]
data_xray = dset_xray[var].values[0:200]
xaxis = numpy.arange(0, len(data_cdat))

plt.plot(xaxis, data_cdat, label='cdat')
plt.plot(xaxis, data_xray, label='xray')
plt.legend()

plt.savefig('test.png')
