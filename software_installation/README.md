## UV-CDAT

The simplest option for installing [UV-CDAT](http://uvcdat.llnl.gov/) is to 
[download](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/) the binary file 
that best matches your operating system and follow the 
[binary installation instructions](https://github.com/UV-CDAT/uvcdat/wiki/Install-Binaries). The 
other option is to install from the 
[source code on github](https://github.com/UV-CDAT/uvcdat), following the relevant 
[build instructions](https://github.com/UV-CDAT/uvcdat/wiki/Building-UVCDAT).

### System requirements

Regardless of whether you install from binaries or source code, there are a number of 
[packages](https://github.com/UV-CDAT/uvcdat/wiki/System-Requirements) that must be 
installed on your system before UV-CDAT will work. I've had no trouble installing these 
on Ubuntu 13.04 (they either come with the operating system or can be easily installed 
using the Ubuntu Software Centre), however for Mac OS X 10.6 (Snow Leopard) I've had 
problems. This is what I've currently installed on my Mac:

* **cmake 2.8.12.1** downloaded from [here](http://www.cmake.org/cmake/resources/software.html#latest)
* **Qt 4.8.5** downloaded from [here](http://qt-project.org/downloads)
* **gfortran** downloaded from the [UV-CDAT sourceforge page](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.4/gfortran-Mac-intel.tar.bz2/download): 
    
        cd / 
        sudo tar xjvf ~/Downloads/gfortran-Mac-intel.tar.bz2


### Binary installation issues - Mac OS X 10.6

When I download and install 
[UV-CDAT-1.4.0-Darwin-10.6.dmg](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.4/UV-CDAT-1.4.0-Darwin-10.6.dmg/download) 
the main UV-CDAT GUI seems to work fine (the installation location is 
`/Applications/UVCDAT.app`, however when I try to run an IPython command line session I 
get the following error:

    $ ./Library/Frameworks/Python.framework/Versions/2.7/bin/ipython
    -bash: ./Library/Frameworks/Python.framework/Versions/2.7/bin/ipython: /lgm/uvcdat/2013-10-21/Library/Frameworks/Python.framework/Versions/2.7/Resour: bad interpreter: No such file or directory


### Source code installation issues - Mac OS X 10.6

Following the [build instructions](https://github.com/UV-CDAT/uvcdat/wiki/Building-UVCDAT), 
this is the process I followed to try and install via source code:

1. Clone the UV-CDAT repo: 

        git clone git://github.com/UV-CDAT/uvcdat.git

2. Create a build directory: 

        mkdir build-uvcdat 
        cd build-uvcdat

3. Run the CMake GUI: 

        cmake-gui ../uvcdat 

    Once the GUI opened, I clicked the *configure* icon and selected the *Unix Makefiles* 
    generator and *default native compilers*. A number of red lines appeared, so I changed 
    the QT-QMAKE-EXECUTABLE from `/usr/bin/anaconda/bin/qmake` to `/usr/bin/qmake` and 
    clicked *configure* again. All the red lines were now gone, however an error was raised 
    (the details of the error are contained in **CMake-GUI-output.log**, **CMakeError.log** and 
    **CMakeOutput.log** in this directory).
   
4. Go back to the terminal and run `make` (however nothing happened, presumably because of the errors encountered in step 3).


## Iris

### Ubuntu 13.04

1. Install the required dependencies. Following the [installation recipes](https://github.com/SciTools/installation-recipes) I installed 
   the following using either `sudo apt-get install` or the Ubuntu Software Centre: 
        
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

