"""
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

import argparse
import numpy

import eof2

module_dir = os.path.join(os.environ['HOME'], 'modules')
sys.path.insert(0, module_dir)
import netcdf_io as nio



class EofAnalysis:
    """Perform an EOF analysis. 
    
    Reference: 
    https://github.com/ajdawson/eof2

    """
    
    def __init__(self, data, neofs=5):
        """Perform the EOF analysis and calculate variance explained.

        It is assumed that the input is a nio.InputData instance.

        """
        
        assert isinstance(data, nio.InputData), \
        'input must be a nio.InputData instance'        

        self.neofs = neofs
        self.data = data
        self.solver = eof2.Eof(data.data, weights='area')
	self.var_exp = self.solver.varianceFraction(neigs=neofs)


    def eof(self, eof_scaling=0):
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
     

    def pcs(self, pc_scaling=0):
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
 

def main(inargs):
    """Run the program."""
    
    # Prepate input data #

    indata = nio.InputData(inargs.infile, inargs.variable, 
                           **nio.dict_filter(vars(inargs), ['time', 'agg', 'region']))
    
    # Perform EOF analysis

    eof_anal = EofAnalysis(indata, **nio.dict_filter(vars(inargs), nio.list_kwargs(EofAnalysis.__init__)))
    
    eof_data, eof_atts = eof_anal.eof(**nio.dict_filter(vars(inargs), nio.list_kwargs(eof_anal.eof)))
    pc_data, pc_atts = eof_anal.pcs(**nio.dict_filter(vars(inargs), nio.list_kwargs(eof_anal.pcs)))

    # Write output file #

    neofs = numpy.shape(eof_data)[0]
    outdata_list = []
    outvar_atts_list = []
    outvar_axes_list = []   
    eof_axes = (indata.data.getLatitude(),
                indata.data.getLongitude(),)  
    pc_axes = (indata.data.getTime(),)
    for index in xrange(neofs * 2):
        if index < neofs:
            outdata_list.append(eof_data[index, ::])
            outvar_atts_list.append(eof_atts[index])
            outvar_axes_list.append(eof_axes)   
        else:
            adj_index = index - neofs
            outdata_list.append(pc_data[:, adj_index])
            outvar_atts_list.append(pc_atts[adj_index])
            outvar_axes_list.append(pc_axes) 
        
    indata_list = [indata,]
    
    nio.write_netcdf(inargs.outfile, 'EOF', 
                     indata_list, 
                     outdata_list,
                     outvar_atts_list, 
                     outvar_axes_list)


if __name__ == '__main__':

    extra_info =""" 
  eof_scaling:      
      0 : Un-scaled EOFs (default)
      1 : EOFs are divided by the square-root of their eigenvalues (gives larger eventual value)
      2 : EOFs are multiplied by the square-root of their eigenvalues
      3 : EOFs scaled as the correlation of the PCs with the original field

  pc_scaling:
      0 : Un-scaled principal components (default)
      1 : Principal components are scaled to unit variance (divided by the square-root of their eigenvalue)
      2 : Principal components are multiplied by the square-root of their eigenvalue

reference:
  uses eof2 package: https://github.com/ajdawson/eof2

example (abyss.earthsci.unimelb.edu.au):
  /usr/local/uvcdat/1.2.0rc1/bin/cdat calc_eof.py --region eqpacific --time 1981-01-01 2010-12-31 
  /work/dbirving/datasets/Merra/data/processed/ts_Merra_surface_monthly-anom-wrt-1981-2010_native-ocean.nc ts 
  /work/dbirving/processed/indices/data/ts_Merra_surface_EOF_monthly-1981-2010_native-ocean-eqpacific.nc

note:
  using monthly anomaly data gives a different result to letting the program automatically 
  remove the time mean at each grid point (because you haven't taken seasonality into account
  if you simply remove the mean of the entire monthly timeseries)

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Perform EOF analysis'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("variable", type=str, help="Input file variable")
    parser.add_argument("outfile", type=str, help="Output file name")
			
    parser.add_argument("--neofs", type=int,
                        help="Number of EOFs for output [default=5]")
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate EOF [default = entire]")
    parser.add_argument("--time", type=str, nargs=2, metavar=('START_DATE', 'END_DATE'),
                        help="Time period over which to calculate the EOF [default = entire]")
    parser.add_argument("--agg", type=str,
                        help="temporal aggregation selector")
    parser.add_argument("--eof_scaling", type=int, choices=[0, 1, 2, 3],
                        help="Scaling method applied to EOF post calculation [default = None]")
    parser.add_argument("--pc_scaling", type=int, choices=[0, 1, 2],
                        help="Scaling method applied to EOF post calculation [default = None]")
    
    args = parser.parse_args()            


    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
