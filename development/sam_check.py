import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import re, pdb


infile = '/mnt/meteo0/data/simmonds/dbirving/temp/test_monthly_sam.nc'
cube_all = iris.load_cube(infile, 'Southern_Annular_Mode_Index')
time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=2011) <= t <= iris.time.PartialDateTime(year=2011))

with iris.FUTURE.context(cell_datetime_objects=True):
    cube_extract = cube_all.extract(time_constraint) 

plt.figure()
iplt.plot(cube_extract)
plt.title('Southern Annular Mode')
plt.xlabel('Time')
plt.ylabel('SAM')
plt.show()
