### University of Melbourne computing notes ###


## Help ##

How to get in touch with IT support (i.e. Doug Morrison and Brett Holman):

1. The *preferred way* is through the Science IT service desk: http://ithelp.science.unimelb.edu.au/servicedesk/

2. You can also email us (support@earthsci.unimelb.edu.au is best, it reaches both of us), call us (x54367 for me, x47222 for Doug), or drop by (room 301). These are less preferable because they don't provide an audit trail, and ultimately might lead to less IT support being provided to Earth Sciences. But it's certainly fine if you just want to ask us something, as opposed to have a problem which needs to be resolved.

3. Don't call our mobiles. Really, don't. Unless the server room is on fire or something, and even then you should be calling x46666 instead. The University does not provide us with mobiles so calling us on our private numbers is inappropriate.


## abyss.earthsci.unimelb.edu.au ##

Login:		
ssh -Y STUDENT\\dbirving@abyss

Work areas:	
/home/dbirving/	(small memory, for code only)
/work/dbirving/	(20GB of storage, can be increased)
	
cdat install (includes Python 2.5):
/opt/cdat/bin/cdat				(to execute)
/opt/cdat/lib/python2.5/site-packages/	(to see packages available to cdat)

General python install (Python 2.6.6):
/usr/bin/python				(to execute)
/usr/local/lib/python2.6/dist-packages/	(see available packages to python)

UV-CDAT install (includes Python 2.7.3)
/usr/local/uvcdat/1.2.0rc1/bin/uvcdat
/usr/local/uvcdat/1.2.0rc1/bin/cdat
/usr/local/uvcdat/1.2.0rc1/bin/ipython

Fortran compiler: 
gfortran (open source compiler that will do f77, f90 and f95)
	
			
## dcc.nci.org.au ##
 
Login:
ssh -X dbi599@dcc.nci.org.au


## irvingnix.earthsci.unimelb.edu.au ##

Operating system = Ubuntu Lucid
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



