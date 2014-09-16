# Software Installation

My preferred setup is as follows:

* Simple manipulation of netCDF files: [NCO](http://nco.sourceforge.net/)
* Simple data processing with netCDF files: [CDO](https://code.zmaw.de/projects/cdo)
* Programming with Python: [Anaconda](http://continuum.io/downloads) plus these additional Python libraries:

    * [cdat-lite](https://pypi.python.org/pypi/cdat-lite/6.0rc2)
    * gitpython
    * [cdo](https://code.zmaw.de/projects/cdo/wiki/Cdo%7Brbpy%7D#Python)
    * [windspharm](http://ajdawson.github.io/windspharm/)
    * [eofs](http://ajdawson.github.io/eofs/)
    * [iris & cartopy](http://scitools.org.uk/)

* Quick data visualisation: [UV-CDAT](http://uvcdat.llnl.gov/) (this is an optional extra - [Panoply](http://www.giss.nasa.gov/tools/panoply/) would be a simplier alternative)

This is easy to setup on a linux machine, but more difficult on a Mac (and near on impossible on a
windows machine I would imagine, although I haven't tried)

My approach for installing Python libraries is to first install Anaconda. It is a free scientific Python
distribution that comes with most of the libraries you'd ever need. For installing extra libraries alongside
Anaconda, I first search [Binstar](https://binstar.org/) to see if `conda` can be used (conda is the library 
installer that comes with Anaconda). If a binstar isn't available, then I use the generic python package
installer (pip). This approach avoids the need to install things myself from binaries or source code, which
is a nightmare and in most cases doesn't work.

## Ubuntu (i.e. Linux)

### NCO

The Ubuntu Software Centre has NCO, which is the equivalent to `apt-get install nco` at the command line.

### CDO

The Ubuntu Software Centre has CDO, which is the equivalent to `apt-get install cdo` at the command line.

### Anaconda

[Downloaded](http://continuum.io/downloads) and ran their Linux-64bit installer. This can be updated via:

    $ sudo /usr/local/anaconda/bin/conda update conda
    $ sudo /usr/local/anaconda/bin/conda update anaconda

##### Additional libraries

Installed:
* `$ sudo /usr/local/anaconda/bin/conda install -c https://conda.binstar.org/ajdawson cdat-lite`
* `$ sudo /usr/local/anaconda/bin/conda install -c https://conda.binstar.org/ajdawson windspharm`
* `$ sudo /usr/local/anaconda/bin/conda install -c https://conda.binstar.org/rsignell iris` (installs cartopy too)
* `$ sudo /usr/local/anaconda/bin/pip install gitpython`
* `$ sudo /usr/local/anaconda/bin/pip install cdo`

Outstanding (i.e. things I still need to install or can't):  
* eofs

(note that soon the latest iris and cartopy binstar files will be stored [here](https://binstar.org/scitools))

### UV-CDAT

Installed from binaries (which involves installing a whole heap of dependencies) following the 
instructions [here](https://github.com/UV-CDAT/uvcdat/wiki/Installation-on-Ubuntu)


## Mac OS X (10.9 Mavricks)

### NCO

##### Homebrew

Using Homebrew (the Mac OS X package manager) type:

    $ brew tap homebrew/science  
    $ brew install nco

##### Binaries

I didn't have any luck installing the most up-to-date binaries (provided as a tarball 
`.tar.gz` at the [NCO website](http://nco.sourceforge.net/)) but at that site they provided
some old DMG files that worked.


### CDO

##### Homebrew

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
[here](https://github.com/Homebrew/homebrew/issues/3930)) suggest that you do the following:

    $ sudo chmod g+w /usr/local
    $ sudo chgrp staff /usr/local

That seemed to work, however a number of simlinks failed because there were other directories
that it didn't have write permissions to. Every time that happened the process stopped, I used
`sudo chgrp staff` (and `sudo cdmod q+w` if need be) to fix the relevant permissions, and then
started the process again with `brew install cdo` until finally the whole thing installed properly.

##### Binaries

I then tried to install from binaries (following [these](https://code.zmaw.de/projects/cdo/embedded/1.6.3/cdo.html#x1-50001.1.1)
very useful instructions for dealing with binaries), however when I tried to run a cdo command 
it said that the netCDF file format wasn't supported. I'd need to install the 
[netCDF libraries](http://www.unidata.ucar.edu/downloads/netcdf/index.jsp) (which are also
binaries) to remedy this problem, however when I tried to do that it told me:

```configure: error: Can't find or link to the hdf5 library. Use --disable-netcdf-4, or see config.log for errors.```

So I'd need to install hdf5 first (via binaries), then netCDF and hopefully CDO will work, but I 
haven't tried this.

### Anaconda

[Downloaded](http://continuum.io/downloads) and ran their Mac installer. This can be updated via:

    $ sudo /users/damienirving/anaconda/bin/conda update conda
    $ sudo /users/damienirving/anaconda/bin/conda update anaconda

##### Additional libraries

Installed:  
* `$ /users/damienirving/anaconda/bin/conda install -c https://conda.binstar.org/jklymak iris` (installs cartopy too)
* `$ /usr/local/anaconda/bin/pip install gitpython`

Outstanding (i.e. things I still need to install or can't):  
* windspharm (no able to produce a binstar - see [this disucssion](https://github.com/ajdawson/windspharm/issues/39))
* cdat-lite (currently no binstar and pip doesn't work)
* eofs

(note that soon the latest iris and cartopy binstar files will be stored [here](https://binstar.org/scitools))

### UV-CDAT

The simplest option for installing [UV-CDAT](http://uvcdat.llnl.gov/) is to 
[download](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.5/) the binary file 
that best matches your operating system (for Mavricks the Darwin 10.8 installer works fine).
There are instructions [here](https://github.com/UV-CDAT/uvcdat/wiki/Installation-on-Mac) which 
basically say that at the command line you just enter the following:

    $ cd /
    $ sudo tar xjvf UV-CDAT-[version number]-[your OS here].tar.bz2

On Mac OS X Mavricks, the installation will only work if you have gfortran, qt and xcode installed. The 
[installation instuctions](http://uvcdat.llnl.gov/installing.html) are a little confusing 
on this topic (there are multiple pages on the website that talk about dependencies and all say something
slightly different), however you can get xcode from the app store, while there are `.dmg` installation files
for qt and gfortran at the same [place](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.5/) 
that you downloaded the UV-CDAT binary file.

##### Extra packages & uodates 

* `$ /usr/local/uvcdat/1.5.1/bin/pip install ipython --upgrade`  (because tefault is very old)
* `$ /usr/local/uvcdat/1.5.1/bin/pip install readline`  (if tab completion isn't working in IPython)

##### Where everything gets installed

Here's what you'll typically enter at the command line to get access to python, ipython and the
UV-CDAT GUI:

* `$ /usr/local/uvcdat/1.5.1/bin/python` 
* `$ /usr/local/uvcdat/1.5.1/Library/Frameworks/Python.framework/Versions/2.7/bin/ipython notebook &`
* `$ /usr/local/uvcdat/1.5.1/bin/uvcdat`
