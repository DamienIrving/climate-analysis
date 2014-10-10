Weird things about these modules:  

* `coordinate_rotation.py` requires a library called `css`, that I can only get via downloading UV-CDAT. That means I have to run it with `/usr/local/uvcdat/1.3.0/bin/python` instead of `/usr/local/anaconda/bin/python` on vortex. Since `coordinate_rotation.py` depends on `netcdf_io.py` and UV-CDAT doesn't play nice with `pandas` and `netCDF4`, I can't use those libraries in `netcdf_io.py`  
