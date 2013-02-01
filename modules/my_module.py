"""
Collection of commonly used classes, functions and global variables

To import:

module_dir = os.path.join(os.environ['HOME'],'dbirving','modules')
sys.path.insert(0,module_dir)


"""

__author__ = 'Damien Irving'


import sys

import numpy

import cdutil
import genutil
import cdms2



## Regions ##
# The 3rd argument here works as follows:
# - First two letters: 'c' or 'o' for closed or open upper/loweer bounds
# - Third letter represents the search method: 
#   'b' bounds, 'n' node, 'e' extranode, 's' select
   

aus = cdms2.selectors.Selector(latitude=(-45,-10,'cc'), 
                               longitude=(110,160,'cc'))
ausnz = cdms2.selectors.Selector(latitude=(-50,0,'cc'),
                                 longitude=(100,185,'cc'))
worldgreenwhich = cdms2.selectors.Selector(latitude=(-90,90,'cc'),
                                           longitude=(-180,180,'cc'))
worlddateline = cdms2.selectors.Selector(latitude=(-90,90,'cc'),
                                         longitude=(0,360,'cc'))


## Colours ##

blue = ['#EAF4FF','#DFEFFF','#BFDFFF','#95CAFF','#55AAFF',
        '#0B85FF','#006AD5','#004080','#002B55','#001B35']

brown = ['#FFFAEA','#FFF8DF','#FFEFBF','#FFE495','#FFD555',
         '#FFC20B','#D59F00','#806000','#554000','#352800']

hot = ['#FFFFEA','#FFFFDF','#FFFF95','#FFFF0B','#FFAA0B',
       '#FF660B','#FF0B0B','#800000','#550000','#350000']

red = ['#FFEAEA','#FFDFDF','#FFBFBF','#FF9595','#FF5555',
       '#FF0B0B','#D50000','#800000','#550000','#350000']

green = ['#F4FFEA','#EFFFDF','#DFFFBF','#CAFF95','#AAFF55',
         '#85FF0B','#6AD500','#408000','#2B5500','#1B3500']

purple = ['#F4EAFF','#EFDFFF','#DFBFFF','#CA95FF','#AA55FF',
          '#850BFF','#6A00D5','#400080','#2B0055','#1B0035']

grey = ['#FFFFFF','#EBEBEB','#E6E6E6','#DCDCDC','#D2D2D2','#CCCCCC',
        '#787878','#666666','#4B4B4B','#333333','#1E1E1E','#000000']

jet= ['#001B35','#000080','#0000D5','#006AD5','#55AAFF','#55FFFF','#55FFAA',
      '#D5FF55','#FFD555','#FF850B','#D51B00','#800000','#350000']

IPCCrain = ['#FFF295','#FFD555','#FF850B','#D55000','#D50000','#550040',
            '#600080','#000080','#0000D5','#0B85FF','#55AAFF','#95CAFF']

grey = '#CCCCCC'
white = '#FFFFFF'


## Classes/functions ##

def convert_units(data):
    """Converts the units of the data.
        
    kg m-2 s-1 or K will be converted to 
    mm/day or Celsius

    """
    #There would be scope to use the genutil udunits module
    #here, however I couldn't figure out how to get it to
    #do the rainfall conversion, plus then all file variables
    #would need to have unidata udunits consistent units
    
    # Switch units #
    
    if data.units[0:10] == 'kg m-2 s-1':
        return numpy.ma.multiply(data,86400.0)
    
    elif units[0] = 'K':
        return numpy.ma.subtract(data,273.16)
    
    else:
        print 'original units not recognised'
        sys.exit(1)
    

def scale_offset(data, scale=1.0, offset=1.0):
    """Applies scaling and offset factors to data.
    
    new_data = (old_data*scale) + offset

    """
    
    return numpy.ma.add(numpy.ma.multiply(new_data, float(scale_offset[0])),
                        float(scale_offset[1]))
    

def _extract_region(region):
    """Obtains lat and lon info from a cdms2.selector region"""
    
    if isinstance(region, cdms2.selectors.Selector):
	for selector_component in region.components():
            if selector_component.id == 'lat':
                minlat, maxlat = selector_component.spec[0:2]
            elif selector_component.id == 'lon':
                minlon, maxlon = selector_component.spec[0:2] 
	latitude = (minlat, maxlat)
	longitude = (minlon, maxlon)
    else: 
	print 'region must be a cdms2 selector'
	sys.exit()
	    
    return latitude, longitude


class InputData:
    """
    Simple data extraction and subsetting/manipulation.
    
    """

    def __init__(self, fname, var_id, **kwargs):
	"""Takes an input file and extracts the desired data.

	**Arguments:**

	*fname*, *var_id*
	    File name and id of the variable to extract

	**Optional arguments**

	    Valid key word arguments include (with examples)
            * grid
            * latitude='(-30, 30)'
            * level=(1000.)
            * longitude='(120, 165)'
            * region='aus'
            * time=('1979-01-01', '2000-12-31') or slice(index1,index2,step)
	
	    Note that self.data has all the attributes and methods
	    of a typical cdms2 variable. For instance:
	    * self.data.getLatitude()
	    * self.data.getLatitude()
	    * self.data.getTime()
	    * self.data.attributes (dictionary incl. _FillValue, units etc)
	
	"""
        
        ## Read the input data, just to set the order and check for missing value ##

        infile = cdms2.open(fname)
        temp_data = infile(var_id)

        input_order = temp_data.getOrder()
        
        assert hasattr(temp_data, 'missing_value')

        del temp_data
       

        ## Prepare kwargs ## 

        # Sort out the order #

        order = 'tyxz'
        for item in 'tyxz':
            if item in input_order:
                order = order.replace(item,'')
        
        kwargs['order'] = order

        # Convert region to lat/lon #

        if kwargs.has_key('region'):   
            try:
                region = globals()[kwargs['region']]
                kwargs['latitude'], kwargs['longitude'] = _extract_region(region)
	    except KeyError:
                print 'region not defined - using all spatial data...'
	    
	    del kwargs['region']

        # Remove empty kwargs #

        for key in kwargs:
            if not kwargs[key]:
	        del kwargs[key]
        

	## Set object attributes ##
	
        data = infile(var_id, **kwargs)

	self.data = data
        self.fname = fname
	self.id = var_id
	

    def temporal_subset(self, input_timescale, output_timescale, climatology=False):
        """Takes a temporal subset of the data.
        
        **Arguments**
        
        *input_timescale*
            Can be daily, monthly or yearly
        
        *output_timescale*
            Can be 
            * SEASONALCYCLE (i.e. DJF/MAM/JJA/SON)
            * ANNUALCYCLE (i.e. JAN/FEB/MAR/.../DEC)
            * YEAR
	    * DJF,MAM,JJA,SON
	    * JAN,FEB,MAR,...,DEC
            * Any custom season (e.g. MJJASO, DJFM)

        **Reference**
            http://www2-pcmdi.llnl.gov/cdat/source/api-reference/cdutil.times.html

        """

        ## Set time bounds ##

        daily_freq = {'hourly': 24; '6hourly': 4; '12hourly': 2; 'daily': 1}

        if input_timescale in daily_freq.keys():
            cdutil.setTimeBoundsDaily(self.data, frequency=daily_freq[input_timescale])
        elif input_timescale == 'monthly':
            cdutil.setTimeBoundsMonthly(self.data)
        elif input_timescale == 'yearly':
            cdutil.setTimeBoundsYearly(self.data)
        else:
            print 'Unrecognised input timescale.'
            print 'Must be daily, monthly or yearly.'
            sys.exit(1)
        
        ## Extract subset of interest ##
        
	accepted_timescales = ['SEASONALCYCLE','ANNUALCYCLE','YEAR',
	                       'DJF','MAM','JJA','SON',
			       'JAN','FEB','MAR','APR','MAY','JUN',
                               'JUL','AUG','SEP','OCT','NOV','DEC']
        
        end = '.climatology(self.data)' if climatology else '(self.data)'
        if output_timescale in accepted_timescales:
	    FunctionToCall = 'cdutil.' + output_timescale + end
            outdata = eval(FunctionToCall)

	elif output_timescale in 'JFMAMJJASONDJFMAMJJASOND':
            custom = cdutil.Seasons(output_timescale)
            outdata = custom(self.data)

        else:
            print 'Unrecognised temporal subset.'
            sys.exit(1)
    

        return outdata

    
    def picker(self, **kwargs):
	"""Takes input data and extracts non-contigious values of an axis.

	**Arguments:**

	**Optional arguments**

	    Valid key word arguments include (with examples)
            * latitude='(-30, 30)'
            * level=(100, 850, 200)
            * longitude='(120, 135, 65)'
            * time=('1979-01-01', '2000-12-31') or slice(index1,index2,step)

        
        """
        
        pick = genutil.picker(**kwargs)
        
        return self.data(pick)


#    def time_mean(self,season):
        

#    def smooth
#    def eddy



#def write_outfile()
