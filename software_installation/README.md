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
* `/usr/local/uvcdat/1.5.1/bin/pip install cdo`

#### Where everything gets installed

Here's what you'll typically enter at the command line to get access to python, ipython and the
UV-CDAT GUI:

* `/usr/local/uvcdat/1.5.1/bin/python` 
* `/usr/local/uvcdat/1.5.1/Library/Frameworks/Python.framework/Versions/2.7/bin/ipython notebook &`
* `/usr/local/uvcdat/1.5.1/bin/uvcdat`


## Iris

### Anaconda (i.e. any operating system)

The easiest way to install iris is alongside Anaconda:  
`conda install -c https://conda.binstar.org/rsignell iris`

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

## netCDF Operators (NCO)

### Mac OS X (10.9 Mavricks)

#### Homebrew

Using Homebrew (the MacOS X package manager) type:

    brew tap homebrew/science  
    brew install nco

#### Binaries

I didn't have any luck installing the most up-to-date binaries (provided as a tarball 
`.tar.gz` at the [NCO website](http://nco.sourceforge.net/)) but at that site they provided
some old DMG files that worked.


## Climate Data Operators (CDO)

### Mac OS X (10.9 Mavricks)

#### Homebrew

On the [website](https://code.zmaw.de/projects/cdo) it says that CDO can be installed via 
homebrew (`brew install cdo`) or macports (`port install cdo`). Macports says that it doesn't
know what cdo is, and so does homebrew unless you type `brew tap homebrew/science` first. 
Annoyingly you can't have both macports and homebrew installed on your machine at the same time,
so I've removed macports and am just using homebrew.

When I ran `brew install cdo` for the first time, it told me:

    Error: Could not create /usr/local/Cellar
    Check you have permission to write to /usr/local

It doesn't let you run `sudo brew install cdo` either, so a number of online forums
(e.g. [here](http://superuser.com/questions/751149/get-around-permission-errors) and
[here](https://github.com/Homebrew/homebrew/issues/3930) suggest that you do the following:

    sudo chmod g+w /usr/local
    sudo chgrp staff /usr/local

That seemed to work, however a number of simlinks failed because there were other directories
that it didn't have write permissions to. Every time that happened the process stopped, I used
`sudo chgrp staff` (and `sudo cdmod q+w` if need be) to fix the relevant permissions, and then
started the process again with `brew install cdo` until finally the whole thing installed properly.

#### Binaries

I then tried to install from binaries (following [these](https://code.zmaw.de/projects/cdo/embedded/1.6.3/cdo.html#x1-50001.1.1)
very useful instructions for dealing with binaries), however when I tried to run a cdo command 
it said that the netCDF file format wasn't supported. I'd need to install the 
[netCDF libraries](http://www.unidata.ucar.edu/downloads/netcdf/index.jsp) (which are also
binaries) to remedy this problem, however when I tried to do that it told me:

```configure: error: Can't find or link to the hdf5 library. Use --disable-netcdf-4, or see config.log for errors.```

So I'd need to install hdf5 first (via binaries), then netCDF and hopefully CDO will work, but I 
haven't tried this.
