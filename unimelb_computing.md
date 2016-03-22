# University of Melbourne computing notes

## Abyss (abyss.earthsci.unimelb.edu.au)

#### Login: on campus  
`ssh -Y STUDENT\\dbirving@abyss`

#### Login: off campus
`ssh -Y STUDENT\\dbirving@abyss.earthsci.unimelb.edu.au` (works sometimes)

Connect to the university VPN first by going to the CISCO AnyConnect Secure Mobility Client and enter the following URL: http://remote.unimelb.edu.au/student. Your computer then acts like you're on campus.
  
#### Work areas	 
`/home/dbirving/` (limited memory, for code only)  
`/work/dbirving/` (default 20GB of storage, which I've had increased to 60GB)
	
#### Software
cdat install (includes Python 2.5):  
`/opt/cdat/bin/cdat` (to execute)  
`/opt/cdat/lib/python2.5/site-packages/`  (to see available packages)  

General python install (Python 2.6.6):  
`/usr/bin/python`  
`/usr/local/lib/python2.6/dist-packages/`

UV-CDAT install (includes Python 2.7.3):  
`/usr/local/uvcdat/1.2.0rc1/bin/uvcdat`  
`/usr/local/uvcdat/1.2.0rc1/bin/cdat`  
`/usr/local/uvcdat/1.2.0rc1/bin/ipython`  
`/usr/local/uvcdat/1.2.0rc1/bin/python2.7/site-packages/`   

Fortran compiler:   
`gfortran` (open source compiler that will do f77, f90 and f95)
	

## Vortex (vortex.earthsci.unimelb.edu.au)

#### Login: on campus
`ssh -Y STUDENT\\dbirving@vortex`  

#### Login: off campus

You can't ssh into vortex from an external machine (i.e. if not using the VPN). Instead, you need to go via abyss.

Connect to the university VPN first by going to the CISCO AnyConnect Secure Mobility Client and enter the following URL: http://remote.unimelb.edu.au/student. Your computer then acts like you're on campus.

#### Work areas  
`/home/STUDENT/dbirving/` (limited memory, for code only)  
`/mnt/meteo0/data/simmonds/dbirving` (large memory, for data)  

#### Software

Anaconda install:  
`/usr/local/anaconda/bin/python`  
`/usr/local/anaconda/bin/ipython`

UV-CDAT install:  
`/usr/local/uvcdat/1.2.0/bin/cdat`  
`/usr/local/uvcdat/1.3.0/bin/cdat` (is actually version 1.3.1)

			
