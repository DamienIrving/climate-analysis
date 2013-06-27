import numpy as np
import matplotlib.pyplot as plt

#import os
#import sys
#module_dir = os.path.join(os.environ['HOME'], 'data_processing', 'windspharm', 'windspharm', 'lib', 'windspharm')
#sys.path.insert(0, module_dir)
#from standard import VectorWind

from windspharm.standard import VectorWind


# create a dummy VectorWind object, we'll only use planetaryvorticity() so values don't matter
u = v = np.random.rand(73, 144)
w = VectorWind(u, v, gridtype='regular')

# calculate planetary vorticity
pvrt = w.planetaryvorticity()

# plot planetary vorticity, remembering it is for a north-south input grid
lon = np.arange(0., 360., 2.5)
lat = np.linspace(90, -90, 73)
plt.pcolor(lon, lat, pvrt)
plt.axis([0, 360, -90, 90])
plt.xlabel('longitude / degrees east')
plt.ylabel('latitude / degrees north')
plt.show()
