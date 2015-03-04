import sys
import numpy as np
import matplotlib.pyplot as plt
import iris
import iris.plot as iplt
import re, pdb

infile = sys.argv[1]
var_name = sys.argv[2]
start_year = int(sys.argv[3])
end_year = int(sys.argv[4])

cube_all = iris.load_cube(infile, var_name)
time_constraint = iris.Constraint(time=lambda t: iris.time.PartialDateTime(year=start_year) <= t <= iris.time.PartialDateTime(year=end_year))

with iris.FUTURE.context(cell_datetime_objects=True):
    cube_extract = cube_all.extract(time_constraint) 

plt.figure()
iplt.plot(cube_extract)
plt.xlabel('Time')
plt.ylabel(var_name)
plt.show()
