"""
Filename:     calc_eof.py
Author:       Damien Irving, d.irving@student.unimelb.edu.au
Description:  Perform Empiricial Orthogonal Function (EOF) analysis
Reference:    Uses eofs package: http://ajdawson.github.io/eofs/

"""

# Import general Python modules

import sys, os
import argparse
import numpy, xray
import eofs

# Import my modules

cwd = os.getcwd()
repo_dir = '/'
for directory in cwd.split('/')[1:]:
    repo_dir = os.path.join(repo_dir, directory)
    if directory == 'climate-analysis':
        break

modules_dir = os.path.join(repo_dir, 'modules')
sys.path.append(modules_dir)
try:
    import netcdf_io as nio
except ImportError:
    raise ImportError('Must run this script from anywhere within the climate-analysis git repo')

# Define functions and classes

class EofAnalysis:
    """Perform an EOF analysis. 
    
    Reference: https://github.com/ajdawson/eof2

    """
    
    def __init__(self, data, neofs=5):
        """Perform EOF analysis and calculate variance explained."""
        
        assert isinstance(data, nio.InputData), \
        'input must be a nio.InputData instance'        

        self.neofs = neofs
        self.data = data
        self.solver = eofs.iris.Eof(data.data, weights='cos_lat')
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
                             'notes': eof_scaling_text}
  
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
                             'notes': pc_scaling_text}

    return pcs, attributes 
 

def main(inargs):
    """Run the program."""
    
    # Prepate input data
    try:
        time_constraint = gio.get_time_constraint(inargs.time)
    except AttributeError:
        time_constraint = iris.Constraint() 

    with iris.FUTURE.context(cell_datetime_objects=True):
        cube = iris.load_cube(inargs.infile, inargs.longname & time_constraint)

    coord_names = [coord.name() for coord in cube.coords()]
    assert coord_names == ['time', 'latitude', 'longitude']
    
    time_coord = cube.coord('time')
    lat_coord = cube.coord('latitude')
    lon_coord = cube.coord('longitude')
    
    # Perform EOF analysis
    eof_anal = EofAnalysis(cube, **nio.dict_filter(vars(inargs), nio.list_kwargs(EofAnalysis.__init__)))
    
    eof_data, eof_atts = eof_anal.eof(**nio.dict_filter(vars(inargs), nio.list_kwargs(eof_anal.eof)))
    pc_data, pc_atts = eof_anal.pcs(**nio.dict_filter(vars(inargs), nio.list_kwargs(eof_anal.pcs)))

    # Write output file
    d = {}
    d['time'] = ('time', time_coord.points)
    d['latitude'] = ('latitude', lat_coord.points)
    d['longitude'] = ('longitude', lon_coord.points)
    
    eof_dims = ['latitude', 'longitude']
    pc_dims = ['time']
    neofs = numpy.shape(eof_data)[0]
    for index in xrange(neofs * 2):
        if index < neofs:
            var = eof_atts[index].id
            d[var] = (eof_dims, eof_data[index, ::])
        else:
            adj_index = index - neofs
            var = pc_atts[adj_index].id
            d[var] = (pc_dims, pc_data[adj_index, ::])
            
    dset_out = xray.Dataset(d)

    for index in xrange(neofs * 2):
        if index < neofs:
            var = eof_atts[index].id
            dset_out[var].attrs = eof_atts[index]
        else:
            adj_index = index - neofs
            var = pc_atts[index].id
            dset_out[var].attrs = pc_atts[adj_index]

    gio.set_dim_atts(dset_out, time_coord, lat_coord, lon_coord)

    outfile_metadata = {inargs.infile: cube.attributes['history']}

    gio.set_global_atts(dset_out, cube.attributes, outfile_metadata)
    dset_out.to_netcdf(inargs.outfile,) #format='NETCDF3_CLASSIC')


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
  uses eofs package: http://ajdawson.github.io/eofs/

example:

note:
  The data are area weighted according the the sqrt of the cosine of the latitude, as 
  recommended by Wilks2011

author:
  Damien Irving, d.irving@student.unimelb.edu.au

"""

    description='Perform EOF analysis'
    parser = argparse.ArgumentParser(description=description,
                                     epilog=extra_info, 
                                     argument_default=argparse.SUPPRESS,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("infile", type=str, help="Input file name")
    parser.add_argument("longname", type=str, help="Long name for input variable")
    parser.add_argument("outfile", type=str, help="Output file name")
            
    parser.add_argument("--neofs", type=int,
                        help="Number of EOFs for output [default=5]")
    parser.add_argument("--region", type=str, choices=nio.regions.keys(),
                        help="Region over which to calculate EOF [default = entire]")
    parser.add_argument("--time", type=str, nargs=3, metavar=('START_DATE', 'END_DATE', 'MONTHS'),
                        help="Time period over which to calculate the EOF [default = entire]")
    parser.add_argument("--eof_scaling", type=int, choices=[0, 1, 2, 3],
                        help="Scaling method applied to EOF post calculation [default = None]")
    parser.add_argument("--pc_scaling", type=int, choices=[0, 1, 2],
                        help="Scaling method applied to EOF post calculation [default = None]")
    
    args = parser.parse_args()            

    print 'Input file: ', args.infile
    print 'Output file: ', args.outfile  

    main(args)
