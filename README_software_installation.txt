Note that software can be installed from binaries (i.e. unpack and it will install itself) or from the 
source code (i.e. unpack the code and then run something like "python setup.py install")


## UV-CDAT (http://uvcdat.llnl.gov/) ##

1. Download latest binaries from: http://sourceforge.net/projects/cdat/files/Releases/UV-CDAT/

2. Follow installation instructions at: https://github.com/UV-CDAT/uvcdat/wiki/Install-Binaries
    cd /
    sudo tar xjvf UV-CDAT-[version number]-[your OS here].tar.bz2

    (so long as your operating system matches [your OS here], then I haven't 
    had any problems)

3. Ask questions at the support forum (http://askbot-uvcdat.llnl.gov/questions/) or on 
   the mailing list (uvcdat-support@llnl.gov)


# Iris #

1. Install the required dependencies, following the installation recipes (https://github.com/SciTools/installation-recipes):
    From "sudo apt-get install" or the Ubuntu Software Centre I got: 
        git libhdf5-serial-dev libnetcdf-dev libudunits2-dev libgeos-dev libproj-dev
        libjasper-dev libfreetype6-dev tk-dev python-tk cython python-scipy matplotlib
        python-nose python-pyke python-mock python-sphinx python-shapely python-pip

    Some additional ones using pip (via sudo):
        netCDF4

2. Download latest release of the cartopy (https://github.com/SciTools/cartopy/tags) and iris (https://github.com/SciTools/iris/tags) source code 

3. Uppack and install these releases at the desired installation location (/usr/local/):

cd /usr/local/    
sudo tar -xzf ~/Downloads/cartopy-0.9.0.tar.gz
cd cartopy-0.9.0
python setup.py install

cd /usr/local/
sudo tar -xzf ~/Downloads/iris-1.5.1.tar.gz
cd iris-1.5.1
python setup.py install

4. Ask questions at the Google support forum: http://scitools.org.uk/iris/community.html 

