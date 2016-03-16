# Software Installation

My preferred setup is as follows:

* Simple manipulation of netCDF files: [NCO](http://nco.sourceforge.net/)
* Simple data processing with netCDF files: [CDO](https://code.zmaw.de/projects/cdo)
* Programming with Python:
  * General purpose libraries I use extensively:
    * [gitpython](http://gitpython.readthedocs.org/en/stable/)
    * [iris & cartopy](http://scitools.org.uk/)
    * [xarray](http://xarray.pydata.org/en/stable/)
    * [seaborn](http://stanford.edu/~mwaskom/software/seaborn/)
  * Libraries I've used for discrete tasks:
    * [windspharm](http://ajdawson.github.io/windspharm/)
    * [eofs](http://ajdawson.github.io/eofs/)
    * [pyqt-fit](http://pythonhosted.org/PyQt-Fit/index.html)
    * [statsmodels](http://statsmodels.sourceforge.net/stable/)
  * Libraries that I might use in future:
    * [cmocean](http://matplotlib.org/cmocean/) 
    * [python-gsw](https://github.com/TEOS-10/python-gsw)

* Quick data visualisation: [UV-CDAT](http://uvcdat.llnl.gov/) 

    * (This is an optional extra - [Panoply](http://www.giss.nasa.gov/tools/panoply/) would be a simplier alternative)
    * This is easy to setup on a linux machine, but more difficult on a Mac
      (and near on impossible on a windows machine I would imagine, although I haven't tried)

My approach for installing Python libraries is to install [Miniconda](http://conda.pydata.org/miniconda.html)
so that I can use the `conda` package installer. 
For packages that aren't automatically available using `conda install`, you can search anaconda.org. 
Almost all packages I use are available from [anaconda.org/IOOS](http://anaconda.org/ioos).
Failing this, I use the generic python package installer (`pip` or `easy_install`). 
This approach avoids the need to install things myself from binaries or source code, 
which is a nightmare and in most cases doesn't work.

## Linux

I have installed software on machines that run Ubuntu 12.04 and CentOS 7.

#### NCO

* The Ubuntu Software Centre has NCO,
  which is the equivalent to `apt-get install nco` at the command line.
* For CentOS run `yum install nco` 

#### CDO

* The Ubuntu Software Centre has CDO,
  which is the equivalent to `apt-get install cdo` at the command line.
* `yum` doesn't have cdo on CentOS

#### Python

The easiest thing to do is create an `environment.yml` file (like the yml files in this directory)
and then create a [conda environment](http://conda.pydata.org/docs/using/envs.html) using the following commands:

```
conda env create environment.yml
source activate environment_name 
```
The `environment.yml` file is just a text file with the environment name, any channels you want to add,
and the list of the software that will be installed.
Once you're finished:   

```
source deactivate
```

###### Bugs/possible improvements

* You may have to specify the path for `activate`; e.g. `/Users/irv033/miniconda2/bin/activate`
* Sometimes the file has to be explicitly called `environment.yml` in order to work
* `$ sudo /usr/local/anaconda/bin/pip install -i https://pypi.anaconda.org/pypi/simple pyqt-fit`
* On CentOS the miniconda install required some tweaking:
  * To make it work successfully, I first had to run `yum install bzip2`
  * On resbaz.cloud.edu.au I then had to do the following to make the IPython launcher call the conda IPython:
    * `conda install ipython`
    * `conda install ipython-notebook`
    * edit ``/etc/supervisor.d/ipynb.conf` so that it points to the correct ipython


#### UV-CDAT

Installed from binaries (which involves installing a whole heap of dependencies) following the 
instructions [here](https://github.com/UV-CDAT/uvcdat/wiki/Installation-on-Ubuntu)


## Mac OS X

#### NCO

###### Homebrew

Using Homebrew (the Mac OS X package manager) type:

    $ brew tap homebrew/science  
    $ brew install nco

###### Binaries

I didn't have any luck installing the most up-to-date binaries 
(provided as a tarball `.tar.gz` at the [NCO website](http://nco.sourceforge.net/)) 
but at that site they provided some old DMG files that worked.


#### CDO

###### Homebrew

On the [website](https://code.zmaw.de/projects/cdo) it says that CDO can be installed via 
homebrew (`brew install cdo`) or macports (`port install cdo`). 
Macports says that it doesn't know what cdo is,
and so does homebrew unless you type `brew tap homebrew/science` first. 
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

That seemed to work, 
however a number of simlinks failed because there were other directories that it didn't have write permissions to. 
Every time that happened the process stopped, 
I used `sudo chgrp staff` (and `sudo cdmod q+w` if need be) to fix the relevant permissions, 
and then started the process again with `brew install cdo` until finally the whole thing installed properly.
Afterwards, @MacHomebrew suggested `sudo chown -R $USER /usr/local` would fix all of the permissions issues.

###### Binaries

I then tried to install from binaries 
(following [these](https://code.zmaw.de/projects/cdo/embedded/1.6.3/cdo.html#x1-50001.1.1)
very useful instructions for dealing with binaries), 
however when I tried to run a cdo command it said that the netCDF file format wasn't supported. 
I'd need to install the [netCDF libraries](http://www.unidata.ucar.edu/downloads/netcdf/index.jsp) 
(which are also binaries) to remedy this problem, 
however when I tried to do that it told me:

```configure: error: Can't find or link to the hdf5 library. Use --disable-netcdf-4, or see config.log for errors.```

So I'd need to install hdf5 first (via binaries), 
then netCDF and hopefully CDO will work, 
but I haven't tried this.

#### Python

As per the Linux instructions, with the addition of the following commands (or `nco` and `cdo` could be added to the `environment.yml` file):  
`conda install -c https://conda.anaconda.org/ioos nco`  
`conda install -c https://conda.anaconda.org/ioos cdo`  
`conda install -c https://conda.anaconda.org/statsmodels statsmodels`    

Note that any issues with eofs or windspharm on Mac should be noted [here](https://github.com/ajdawson/windspharm/issues/39).


#### UV-CDAT

The simplest option for installing [UV-CDAT](http://uvcdat.llnl.gov/) is to 
[download](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.5/) 
the binary file that best matches your operating system 
(for Mavricks the Darwin 10.8 installer works fine).
There are instructions [here](https://github.com/UV-CDAT/uvcdat/wiki/Installation-on-Mac),
which basically say that at the command line you just enter the following:

    $ cd /
    $ sudo tar xjvf UV-CDAT-[version number]-[your OS here].tar.bz2

On Mac OS X Mavricks, 
the installation will only work if you have gfortran, qt and xcode installed. 
The [installation instuctions](http://uvcdat.llnl.gov/installing.html) are a little confusing 
(there are multiple pages on the website that talk about dependencies and all say something slightly different),
however you can get xcode from the app store, 
while there are `.dmg` installation files for qt and gfortran at the same 
[place](http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/1.5/) 
that you downloaded the UV-CDAT binary file.

###### Extra packages & uodates 

* `$ /usr/local/uvcdat/1.5.1/bin/pip install ipython --upgrade`  (because tefault is very old)
* `$ /usr/local/uvcdat/1.5.1/bin/pip install readline`  (if tab completion isn't working in IPython)

###### Where everything gets installed

Here's what you'll typically enter at the command line to get access to python,
ipython and the UV-CDAT GUI:

* `$ /usr/local/uvcdat/1.5.1/bin/python` 
* `$ /usr/local/uvcdat/1.5.1/Library/Frameworks/Python.framework/Versions/2.7/bin/ipython notebook &`
* `$ /usr/local/uvcdat/1.5.1/bin/uvcdat`

## CWS Virtual Lab

* `module avail` to find cdo and nco
* Install miniconda at `/g/data/r87/dbi599/` 
  * This gets added to the `.bashrc` file: `export PATH="/g/data/r87/dbi599/miniconda2/bin:$PATH"`
 
