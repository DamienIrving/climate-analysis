### University of Melbourne computing notes###

## Help ##

How to get in touch with IT support (i.e. Doug Morrison):

1. The *preferred way* is through the Science IT service desk: http://ithelp.science.unimelb.edu.au/servicedesk/

2. You can also email (support@earthsci.unimelb.edu.au is best), call us (x47222 for Doug), or drop by (room 301). These are less preferable because they don't provide an audit trail, and ultimately might lead to less IT support being provided to Earth Sciences. But it's certainly fine if you just want to ask us something, as opposed to have a problem which needs to be resolved.


## abyss.earthsci.unimelb.edu.au ##

Login:		
ssh -Y STUDENT\\dbirving@abyss

Work areas:	
/home/dbirving/	(small memory, for code only)
/work/dbirving/	(default 20GB of storage, which I've had increased to 60GB)
	
cdat install (includes Python 2.5):
/opt/cdat/bin/cdat			(to execute)
/opt/cdat/lib/python2.5/site-packages/	(to see packages available to cdat)

General python install (Python 2.6.6):
/usr/bin/python				(to execute)
/usr/local/lib/python2.6/dist-packages/	(see available packages to python)

UV-CDAT install (includes Python 2.7.3)
/usr/local/uvcdat/1.2.0rc1/bin/uvcdat
/usr/local/uvcdat/1.2.0rc1/bin/cdat
/usr/local/uvcdat/1.2.0rc1/bin/ipython
/usr/local/uvcdat/1.2.0rc1/bin/python2.7/site-packages/ 

Fortran compiler: 
gfortran (open source compiler that will do f77, f90 and f95)
	

## vortex.earthsci.unimelb.edu.au ##

Login:
ssh -Y STUDENT\\dbirving@vortex
Note that you can't ssh into vortex from an external machine (need to go via abyss or irvingnix)

Work areas:
/home/STUDENT/dbirving/               (small memory, for code only)
/mnt/meteo0/data/simmonds/dbirving    (large memory, for data)

UV-CDAT install:
/usr/local/uvcdat/1.2.0/bin/cdat      (same as on abyss)
/usr/local/uvcdat/1.3.0/bin/cdat      (is actually version 1.3.1)

			
## dcc.nci.org.au ##
 
Login:
ssh -X dbi599@dcc.nci.org.au


## irvingnix.earthsci.unimelb.edu.au ##

Operating system: Ubuntu 13.04, 64-bit (it's Debian based)
Memory (RAM): 2GB 
I have sudo admin access, so I need to type 'sudo' at the command line before any admin commands. e.g. sudo apt-get install git-core


## Git ##

git clone

git add
git commit -m "comment"
git push -u origin master

git pull

For using latest version of Git: unixlab01.earthsci.unimelb.edu.au, vislab01.earthsci.unimelb.edu.au


## CMIP tos data ##

Some of this data are on a triangulated grid. To get them onto a regular lat/lon grid, you need to use the following cdo command (at least that's what they've done at CSIRO)

cdo remapbil,sftlf.nc tos.nc out.nc

Note that sftlf.nc is the file that it copies the new grid from.


## Running ACCESS ##

Initially apply for an NCI start up account
500 free hours to play around
Permanent access could be obtained via the UniMelb allocation or the CoECSS allocation (that would require getting aligned with the CoECSS somehow)
Mike Rezny says that his team at the CoE would help me with running the ACCESS model, even if I wasn't CoECSS aligned
Running the atmosphere part of the model is really easy. The coupled model is a bit of a nightmare


## Checking jobs ##

To check what jobs are running and how much CPU they are using, use the top command.

-u STUDENT\\dbirving  Shows just my jobs
-r                    Reince the job
-k                    Kill the job



