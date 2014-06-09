## UV-CDAT

The simplest option for installing [UV-CDAT](http://uvcdat.llnl.gov/) is to 
[download](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/) the binary file 
that best matches your operating system and follow the 
[binary installation instructions](https://github.com/UV-CDAT/uvcdat/wiki/Install-Binaries). The 
other option is to install from the 
[source code on github](https://github.com/UV-CDAT/uvcdat), following the relevant 
[build instructions](https://github.com/UV-CDAT/uvcdat/wiki/Building-UVCDAT).

### Extra packages

Here are the extra libraries that I install alongside UV-CDAT:  

* `/usr/local/uvcdat/1.5.1/bin/pip install gitpython`
* `/usr/local/uvcdat/1.5.1/bin/pip install ipython --update`  (because tefault is very old)
* `/usr/local/uvcdat/1.5.1/bin/pip install readline`  (if tab completion isn't working in IPython)
* `/usr/local/uvcdat/1.5.1/bin/pip install pandas`


## Iris

### Ubuntu 13.04

1. Install the required dependencies. Following the [installation recipes](https://github.com/SciTools/installation-recipes) I installed the following using either `sudo apt-get install` or the Ubuntu Software Centre: 
        
        git libhdf5-serial-dev libnetcdf-dev libudunits2-dev libgeos-dev libproj-dev
        libjasper-dev libfreetype6-dev tk-dev python-tk cython python-scipy matplotlib
        python-nose python-pyke python-mock python-sphinx python-shapely python-pip

    Some additional ones using `sudo pip`:
        
        netCDF4

2. Download latest release of the [cartopy](https://github.com/SciTools/cartopy/tags) and 
   [iris](https://github.com/SciTools/iris/tags) source code 

3. Uppack and install these releases at the desired installation location (e.g. `/usr/local/`):
    
        cd /usr/local/    
        sudo tar -xzf ~/Downloads/cartopy-0.9.0.tar.gz
        cd cartopy-0.9.0
        python setup.py install

        cd /usr/local/
        sudo tar -xzf ~/Downloads/iris-1.5.1.tar.gz
        cd iris-1.5.1
        python setup.py install

4. Ask questions at the [support forum](http://scitools.org.uk/iris/community.html) 

