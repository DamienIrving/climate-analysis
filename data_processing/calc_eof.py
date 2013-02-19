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

import sys
import os
from optparse import OptionParser

import eof2

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io



class EofAnalysis:
    """Perform an EOF analysis. 
    
    Reference: 
    https://github.com/ajdawson/eof2

    """
    
    def __init__(self, data, neofs):
        """Perform the EOF analysis and calculate variance explained.

        It is assumed that the input is a netcdf_io.InputData instance.

        """
        
        assert isinstance(data, netcdf_io.InputData), \
        'input must be a netcdf_io.InputData instance'        

        self.neofs = neofs
        self.data = data
        self.solver = eof2.Eof(data.data, weights='area')
	self.var_exp = self.solver.varianceFraction(neigs=neofs)


    def eof(self, eof_scaling):
        """Calculate the EOFs."""
	
        if eof_scaling == 3:
            eofs = self.solver.eofsAsCorrelation(neofs=self.neofs)
            eof_scaling_text = 'EOF scaled as the correlation of the PCs with the original field - used eofsAsCorrelation() function'
            eof_units = ''
        else: 
            eofs = self.solver.eofs(neofs=self.neofs, eofscaling=eof_scaling)
            eof_units = ''
            if eof_scaling == 0:
                eof_scaling_text = 'No scaling applied'
            elif eof_scaling == 1:
                eof_scaling_text = 'EOF is divided by the square-root of its eigenvalue'  
            elif eof_scaling == 2:
                eof_scaling_text = 'EOF is multiplied by the square-root of its eigenvalue'        
            else:
                print 'EOF scaling method not recongnised'
                sys.exit(1)

        attributes = ['']*self.neofs
        for i in range(0, self.neofs):
            attributes[i] = {'id': 'eof'+str(i + 1),
                             'long_name': 'Empirical Orthogonal Function '+str(i + 1),
                             'units': eof_units,
                             'var_exp': self.var_exp[i],
                             'reference': 'https://github.com/ajdawson/eof2',
                             'history': eof_scaling_text}
  
        return eofs, attributes
     

    def pcs(self, pc_scaling):
        """Calculate the prinicple components."""

        pcs = self.solver.pcs(npcs=self.neofs, pcscaling=pc_scaling)
        pc_units = ''
        if pc_scaling == 0:
            pc_scaling_text = 'No scaling applied'
        elif pc_scaling == 1:
            pc_scaling_text = 'PC scaled to unit variance (divided by the square-root of its eigenvalue)'
        elif pc_scaling == 2:
            pc_scaling_text = 'PC multiplied by the square-root of its eigenvalue'    
        else:
            print 'PC scaling method not recongnised'   
            sys.exit(1)    
        
        attributes = ['']*self.neofs
        for i in range(0, self.neofs):
            attributes[i] = {'id': 'pc'+str(i + 1),
                             'long_name': 'Principle component '+str(i + 1),
                             'units': pc_units,
                             'var_exp': self.var_exp[i],
                             'reference': 'https://github.com/ajdawson/eof2',
                             'history': pc_scaling_text}

	return pcs, attributes 
 

def main(infile_name, var_id, outfile_name, **kwargs):
    """Run the program."""
    
    # Prepate input data #

    selectors = ['time', 'agg', 'region']
    data_opts = {}
    for item in selectors:
        if kwargs[item]:
            data_opts[item] = kwargs[item]

    indata = netcdf_io.InputData(infile_name, var_id, **data_opts)
    
    # Perform EOF analysis

    eof_anal = EofAnalysis(indata, kwargs['neofs'])
    
    eof_data, eof_atts = eof_anal.eof(kwargs['eof_scaling'])
    pc_data, pc_atts = eof_anal.pcs(kwargs['eof_scaling'])

    # Write output file #

    outdata_list = []
    outvar_atts_list = []
    outvar_axes_list = []   
    eof_axes = (indata.data.getLatitude(),
                indata.data.getLongitude(),)  
    pc_axes = (indata.data.getTime(),)
    for index in range(0, kwargs['neofs']*2):
        if index < kwargs['neofs']:
            outdata_list.append(eof_data[index, ::])
            outvar_atts_list.append(eof_atts[index])
            outvar_axes_list.append(eof_axes)   
        else:
            adj_index = index - kwargs['neofs']
            outdata_list.append(pc_data[:, adj_index])
            outvar_atts_list.append(pc_atts[adj_index])
            outvar_axes_list.append(pc_axes) 
        
    indata_list = [indata,]*kwargs['neofs']
    
    netcdf_io.write_netcdf(outfile_name, 'EOF', 
                           indata_list, 
                           outdata_list,
			   outvar_atts_list, 
			   outvar_axes_list)


if __name__ == '__main__':

    usage = "usage: %prog [options] {input_file} {input_variable} {output_file}"
    parser = OptionParser(usage=usage)

    parser.add_option("-M", "--manual", dest="manual", action="store_true", default=False,
                       help="output a detailed description of the program")
    parser.add_option("-n", "--neofs", dest="neofs", type='int', default=5,
                       help="Number of EOFs for output [default=5]")
    parser.add_option("-r", "--region", dest="region", type='string', default=None,
                      help="Region over which to calculate EOF [default=entire]")
    parser.add_option("-t", "--time", dest="time", type='str', nargs=2, default=None, 
                      help="Period over which to calculate time mean [default = entire time period]")
    parser.add_option("-a", "--agg", dest='agg', default=None,
                      help="temporal aggregation selector")
    parser.add_option("-e", "--eof_scaling", dest="eof_scaling", type='int', default=0,
                      help="Scaling method applied to EOF post calculation [default = None]")
    parser.add_option("-p", "--pc_scaling", dest="pc_scaling", type='int', default=0,
                      help="Scaling method applied to EOF post calculation [default = None]")
    
    (options, args) = parser.parse_args()            

    if options.manual == True or len(sys.argv) == 1:
        print """
        Usage:
            eof_anal.py [-M] [-h] [-n] [-r] [-t] [-p] [-e] [-a] {input_file} {variable} {output_file}

        Options
            -M -> Display this on-line manual page and exit
            -h -> Display a help/usage message and exit
	    -n -> Number of EOFs that are output [default = 5]
	    -e -> Scaling method applied to EOF post calculation [default = None] 
            -p -> Scaling method applied to PC post calculation [default = None] 
            -r -> Spatial region selector [default = entire]
	    -t -> Time period selector [default = entire]. Tuple: (start_date, end_date)
            -a -> Temporal aggregation selector [default = None]. Tuple: (season, climatology)
		   
	Note
	    The output PC files will take the user supplied file name and replace the string PC with PC1, PC2 etc 
        
	Options
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
	    /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_eof.py -r eqpacific -t 1981-01-01 2010-12-31 
	    /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc ts 
	    /work/dbirving/processed/indices/data/ts_Merra_surface_EOF_monthly-1981-2010_native-ocean-eqpacific.nc
	
        Improvements
            This program should take raw data, not anomaly data, as it's input.
            (i.e. it would calculate the anomaly itself, or perhaps the EOF package can do that?)
             
        Author
            Damien Irving, 10 Dec 2012.

        Bugs
            Please report any problems to: d.irving@student.unimelb.edu.au
        """
        sys.exit(0)

    else:

        # Repeat the command line arguments #

        print 'Input file: ', args[0]
        print 'Output file: ', args[2]  

        main(args[0], args[1], args[2], neofs=options.neofs, 
                                        region=options.region,
                                        agg=options.agg,
                                        time=options.time,
                                        pc_scaling=options.pc_scaling,
                                        eof_scaling=options.eof_scaling)
