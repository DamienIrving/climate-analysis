## UV-CDAT

### Mac OS X (10.9 Mavricks)

The simplest option for installing [UV-CDAT](http://uvcdat.llnl.gov/) is to 
[download](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.5/) the binary file 
that best matches your operating system (for Mavricks the Darwin 10.8 installer works fine). 
At the command line you then just enter the following:

    cd /
    sudo tar xjvf UV-CDAT-[version number]-[your OS here].tar.bz2

On Mac OS X Mavricks, the installation will only work if you have gfortran, qt and xcode installed. The 
[installation instuctions](http://uvcdat.llnl.gov/installing.html) are a little confusing 
on this topic (there are multiple pages on the website that talk about dependencies and all say something
slightly different), however you can get xcode from the app store, while there are `.dmg` installation files
for qt and gfortran at the same [place](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.5/) 
that you downloaded the UV-CDAT binary file.

#### Extra packages

Here are the extra libraries that I install alongside UV-CDAT:  

* `/usr/local/uvcdat/1.5.1/bin/pip install gitpython`
* `/usr/local/uvcdat/1.5.1/bin/pip install ipython --upgrade`  (because tefault is very old)
* `/usr/local/uvcdat/1.5.1/bin/pip install readline`  (if tab completion isn't working in IPython)
* `/usr/local/uvcdat/1.5.1/bin/pip install pandas`

#### Where everything gets installed

Here's what you'll typically enter at the command line to get access to python, ipython and the
UV-CDAT GUI:

* `/usr/local/uvcdat/1.5.1/bin/python` 
* `/usr/local/uvcdat/1.5.1/Library/Frameworks/Python.framework/Versions/2.7/bin/ipython notebook &`
* `/usr/local/uvcdat/1.5.1/bin/uvcdat`


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

