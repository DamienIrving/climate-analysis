#!/usr/bin/env cdat
"""
SVN INFO: $Id$
Filename:     eof_anal.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Performs and Empiricial Orthogonal Function (EOF) analysis
Reference:    Uses eof2 package: https://github.com/ajdawson/eof2

Updates | By | Description
--------+----+------------
23 October 2012 | Damien Irving | Initial version.
10 December 2012 | Damien Irving | Switched over to eof2 package

"""

__version__ = '$Revision$'     ## Change this for git (this is an svn command)


### Import required modules ###

from optparse import OptionParser
import sys
from datetime import datetime
import numpy

import cdms2
cdms2.setNetcdfShuffleFlag(0)
cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)
import eof2


### Define globals ###

eqpacific = cdms2.selectors.Selector(latitude=(-30, 30, 'cc'),
                                     longitude=(120, 280, 'cc'))
sh = cdms2.selectors.Selector(latitude=(-90, 0, 'cc'),
                              longitude=(0, 360, 'cc'))	
shextrop = cdms2.selectors.Selector(latitude=(-90, -30, 'cc'),
                                    longitude=(0, 360, 'cc'))			      			     
tropics = cdms2.selectors.Selector(latitude=(-30, 30, 'cc'),
                                   longitude=(0, 360, 'cc'))

### Define functions ###


class InputFile:
    """Takes an input file name and unpacks the contents"""

    def __init__(self, fname):

        self.fname = fname
	fin = cdms2.open(fname)
        self.history = fin.attributes['history'] if ('history' in fin.attributes.keys()) else ''
	self.region = None
	self.infile = fin
	
    def extract_data(self, variable, region_name, time_bounds):
        """Extracts data according to the desired time period and region"""

        self.region = region_name
        infile = self.infile

        if region_name:
            try:
                region = globals()[region_name]
            except KeyError:
                print 'region not defined - using all spatial data...'
                region = None
        else:
            region = None 

        if time_bounds and region:
            indata = infile(variable, region, time=(time_bounds[0], time_bounds[1]), squeeze=1)
        elif time_bounds: 
            indata = infile(variable, time=(time_bounds[0], time_bounds[1]), squeeze=1)
        elif region:
            indata = infile(variable, region, squeeze=1)
        else:
            indata = infile(variable, squeeze=1)

        return indata


class EofAnalysis:
    """Performs an EOF analysis, using the eof2 package: https://github.com/ajdawson/eof2"""
    
    def __init__(self, data, neofs):
        self.neofs = neofs
        self.data = data
        self.solver = eof2.Eof(data, weights='area')
	
    def eof(self, eof_scaling):
        """Calculates the EOF"""
	
        if eof_scaling == 3:
            eofs = self.solver.eofsAsCorrelation(neofs=self.neofs)
            eof_scaling_text = 'EOF scaled as the correlation of the PCs with the original field - used eofsAsCorrelation() function'
            eof_units = ''
        else: 
            eofs = self.solver.eofs(neofs=self.neofs, eofscaling=eof_scaling)
            eof_units = ''
            if eof_scaling == 0:
                eof_scaling_text = 'None'
            elif eof_scaling == 1:
                eof_scaling_text = 'EOF is divided by the square-root of its eigenvalue'  
            elif eof_scaling == 2:
                eof_scaling_text = 'EOF is multiplied by the square-root of its eigenvalue'        
            else:
                print 'EOF scaling method not recongnised'
                sys.exit(1)

        return eofs, eof_scaling_text, eof_units

    def pcs(self, pc_scaling):
        """Calculates the prinicple components"""

        pcs = self.solver.pcs(npcs=self.neofs, pcscaling=pc_scaling)
        pc_units = ''
        if pc_scaling == 0:
            pc_scaling_text = 'None'
        elif pc_scaling == 1:
            pc_scaling_text = 'PC scaled to unit variance (divided by the square-root of its eigenvalue)'
        elif pc_scaling == 2:
            pc_scaling_text = 'PC multiplied by the square-root of its eigenvalue'    
        else:
            print 'PC scaling method not recongnised'   
            sys.exit(1)    
        
	return pcs, pc_scaling_text, pc_units 
	
    def var_exp(self):
        """Calculates the variance explained"""
    
        return self.solver.varianceFraction(neigs=self.neofs)


def write_eofs(infile, eof_anal, outfile_name_eof, outfile_name_pc, eof_scaling):
    """Writes output netCDF file with EOFs in it"""
    
    ## Perform EOF analysis ##
    
    eofs, eof_scaling_text, eof_units = eof_anal.eof(eof_scaling)
    varfracs = eof_anal.var_exp()
    
    ## Write output file ##
    
    outfile = cdms2.open(outfile_name_eof,'w')
    
    # Global attributes #

    global_atts = {'title': 'Empirical Orthogonal Function analysis over %s region'  %(infile.region),
                   'contact': 'Damien Irving (d.irving@student.unimelb.edu.au)',
                   'reference': 'https://github.com/ajdawson/eof2',
		   'companion_file': outfile_name_pc,
		   'history': '%s: Calculated EOF from %s using %s, format=NETCDF3_CLASSIC\n%s'  %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"),
                   infile.fname, sys.argv[0], infile.history)
                  }
                      
    for key, value in global_atts.iteritems():
        setattr(outfile, key, value)

    # Variables #

    outlat = outfile.copyAxis(eof_anal.data.getLatitude())  
    outlon = outfile.copyAxis(eof_anal.data.getLongitude())  
    
    for i in range(0, eof_anal.neofs):
	var = eofs[i, :, :]
	var = cdms2.MV2.array(var)
	var = var.astype(numpy.float32)
	var.setAxisList([outlat, outlon])
	var.id = 'eof'+str(i+1)

	var_atts = {'name': 'eof'+str(i+1),
                    'standard_name': 'eof'+str(i+1),
                    'units': eof_units, 
		    'scaling': eof_scaling_text, 
                    'variance_explained': '%7.4f'  %(varfracs[i])
        	   } 

	for key, value in var_atts.iteritems():
            setattr(var, key, value)

        outfile.write(var)  

    outfile.close()


def write_pcs(infile, eof_anal, outfile_name_eof, outfile_name_pc, pc_scaling):
    """Writes an output text file for each of the Principle Components (pcs)"""
    
    ## Perform EOF analysis ##
    
    pcs, pc_scaling_text, pc_units = eof_anal.pcs(pc_scaling)
    varfracs = eof_anal.var_exp()
    
    ## Get time axis info ##
    
    times = eof_anal.data.getTime().asComponentTime()
    years = []
    months = []
    
    for i in range(0, len(times)):
        years.append(int(str(times[i]).split('-')[0]))
        months.append(int(str(times[i]).split('-')[1]))
    
    
    ## Write outfiles ##
    
    for i in range(0, eof_anal.neofs):
        
	# File name #
    
        new_name = outfile_name_pc.replace('PC', 'PC'+str(i+1))
        outfile = open(new_name, 'w')   
	        
	# Global attributes #
	
	outfile.write('Title: Principle Component %s from EOF analysis over %s region \n'  %(i+1, infile.region))
        outfile.write('Contact: Damien Irving (d.irving@student.unimelb.edu.au) \n')
        outfile.write('History: EOF calculated using eof2 cdat module \n')
        outfile.write('Reference: https://github.com/ajdawson/eof2 \n')
        outfile.write('Sourcefile: %s \n'  %(infile.fname))
	outfile.write('Companion EOF file: %s \n'  %(outfile_name_eof))
        outfile.write('Created %s using %s \n'  %(datetime.now().strftime("%a %b %d %H:%M:%S %Y"), sys.argv[0]))
	outfile.write('Scaling: %s \n'  %(pc_scaling_text))
	outfile.write('Units: %s \n'  %(pc_units))
	outfile.write('Variance explained: %7.4f \n'  %(varfracs[i]))
	
	# Data #
	
	outfile.write(' YR   MON  PC%s \n' %(i+1)) 
        ntime = numpy.shape(pcs)[0]
	for t in range(0, ntime):
            print >> outfile, '%4i %3i %7.2f'  %(years[t], months[t], pcs[t,i])


def main(infile_name, var_id, outfile_name_eof, outfile_name_pc, neofs, region_name, time_bounds, eof_scaling, pc_scaling):
    """Run the program"""
    
    infile = InputFile(infile_name)
    
    eof_anal = EofAnalysis(infile.extract_data(var_id, region_name, time_bounds), neofs)
    
    write_eofs(infile, eof_anal, outfile_name_eof, outfile_name_pc, eof_scaling)
    write_pcs(infile, eof_anal, outfile_name_eof, outfile_name_pc, pc_scaling)


if __name__ == '__main__':

    ## Help and manual information ##

    usage = "usage: %prog [options] {input_file} {input_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual", dest="manual", action="store_true", default=False,
                       help="output a detailed description of the program")
    parser.add_option("-n", "--neofs", dest="neofs", type='int', default=5,
                       help="Number of EOFs for output [default=5]")
    parser.add_option("-r", "--region", dest="region", type='string', default=None,
                      help="Region over which to calculate EOF [default=entire]")
    parser.add_option("-t", "--time_bounds", dest="time_bounds", type='str', nargs=2, default=None, 
                      help="Period over which to calculate time mean [default = entire time period]")
    parser.add_option("-e", "--eof_scaling", dest="eof_scaling", type='int', default=0,
                      help="Scaling method applied to EOF post calculation [default = None]")
    parser.add_option("-p", "--pc_scaling", dest="pc_scaling", type='int', default=0,
                      help="Scaling method applied to EOF post calculation [default = None]")
    
    (options, args) = parser.parse_args()            

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            eof_anal.py [-M] [-h] [-n] [-r] [-t] [-p] [-e] {input_file} 
	    {input_variable} {output_eof_file} {output_pc_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -n -> Number of EOFs that are output [default = 5]
	    -r -> Region over which to calculate the EOF [default = entire; i.e whole input region]
            -t -> Time period over which to calculate the EOF (2 args: start_date end_date) [default = entire]
	    -e -> Scaling method applied to EOF post calculation [default = None] 
            -p -> Scaling method applied to PC post calculation [default = None] 
		   
	Note
	    The output PC files will take the user supplied file name and replace the string PC with PC1, PC2 etc 
        
	Options
	    region: eqpacific, sh, tropics
	    
	    eof_scaling:      
                0 : Un-scaled EOFs (default)
                1 : EOFs are divided by the square-root of their eigenvalues (gives larger eventual value)
                2 : EOFs are multiplied by the square-root of their eigenvalues
		3 : EOFs scaled as the correlation of the PCs with the original field

	    pc_scaling:
                0 : Un-scaled principal components (default)
                1 : Principal components are scaled to unit variance (divided by the square-root of their eigenvalue)
                2 : Principal components are multiplied by the square-root of their eigenvalue
       
        Reference
            Uses eof2 package: https://github.com/ajdawson/eof2

        Example (abyss.earthsci.unimelb.edu.au)
	    /usr/local/uvcdat/1.2.0rc1/bin/cdat eof_anal.py -r eqpacific -t 1979-01-01 2011-12-31 
	    /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc ts 
	    /work/dbirving/processed/indices/data/ts_Merra_surface_EOF_monthly-1979-2011_native-ocean-eqpacific.nc
	    /work/dbirving/processed/indices/data/ts_Merra_surface_PC_monthly_native-ocean-eqpacific.txt
	    
        Author
            Damien Irving, 10 Dec 2012.

        Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
        """
        sys.exit(0)

    else:

        # Repeat the command line arguments #

        print 'Input file: ', args[0]
        print 'Output EOF file: ', args[2]
	print 'Output PC file:', args[3]
	print 'Region:', options.region
        
        infile_name, var_id, outfile_name_eof, outfile_name_pc = args  
    
        main(infile_name, var_id, outfile_name_eof, outfile_name_pc, options.neofs, 
	options.region, options.time_bounds, options.eof_scaling, options.pc_scaling)
