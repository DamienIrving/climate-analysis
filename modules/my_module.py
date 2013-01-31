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

aus = cdms2.selectors.Selector(latitude=(-45,-10,'cc'),longitude=(110,160,'cc'))
ausnz = cdms2.selectors.Selector(latitude=(-50,0,'cc'),longitude=(100,185,'cc'))
worldgreenwhich = cdms2.selectors.Selector(latitude=(-90,90,'cc'),longitude=(-180,180,'cc'))
worlddateline = cdms2.selectors.Selector(latitude=(-90,90,'cc'),longitude=(0,360,'cc'))


## Colours ##

blue1,blue2,blue3,blue4,blue5, = ['#EAF4FF','#DFEFFF','#BFDFFF','#95CAFF','#55AAFF']
blue6,blue7,blue8,blue9,blue10 = ['#0B85FF','#006AD5','#004080','#002B55','#001B35']

brown1,brown2,brown3,brown4,brown5, = ['#FFFAEA','#FFF8DF','#FFEFBF','#FFE495','#FFD555']
brown6,brown7,brown8,brown9,brown10 = ['#FFC20B','#D59F00','#806000','#554000','#352800']

hot1,hot2,hot3,hot4,hot5, = ['#FFFFEA','#FFFFDF','#FFFF95','#FFFF0B','#FFAA0B']
hot6,hot7,hot8,hot9,hot10 = ['#FF660B','#FF0B0B','#800000','#550000','#350000']

red1,red2,red3,red4,red5, = ['#FFEAEA','#FFDFDF','#FFBFBF','#FF9595','#FF5555']
red6,red7,red8,red9,red10 = ['#FF0B0B','#D50000','#800000','#550000','#350000']

green1,green2,green3,green4,green5, = ['#F4FFEA','#EFFFDF','#DFFFBF','#CAFF95','#AAFF55']
green6,green7,green8,green9,green10 = ['#85FF0B','#6AD500','#408000','#2B5500','#1B3500']

purple1,purple2,purple3,purple4,purple5, = ['#F4EAFF','#EFDFFF','#DFBFFF','#CA95FF','#AA55FF']
purple6,purple7,purple8,purple9,purple10 = ['#850BFF','#6A00D5','#400080','#2B0055','#1B0035']

grey1,grey2,grey3,grey4,grey5,grey6 = ['#FFFFFF','#EBEBEB','#E6E6E6','#DCDCDC','#D2D2D2','#CCCCCC']
grey7,grey8,grey9,grey10,grey11,grey12 = ['#787878','#666666','#4B4B4B','#333333','#1E1E1E','#000000']

jet0,jet1,jet2,jet3,jet4,jet5,jet6 = ['#001B35','#000080','#0000D5','#006AD5','#55AAFF','#55FFFF','#55FFAA']
jet7,jet8,jet9,jet10,jet11,jet12 = ['#D5FF55','#FFD555','#FF850B','#D51B00','#800000','#350000']

IPCCrain1,IPCCrain2,IPCCrain3,IPCCrain4,IPCCrain5,IPCCrain6 = ['#FFF295','#FFD555','#FF850B','#D55000','#D50000','#550040']
IPCCrain7,IPCCrain8,IPCCrain9,IPCCrain10,IPCCrain11,IPCCrain12 = ['#600080','#000080','#0000D5','#0B85FF','#55AAFF','#95CAFF']

grey = '#CCCCCC'
white = '#FFFFFF'


## Classes ##

def convert_units(data, orig_units=None, scale_offset=None):
    """Converts the units of the data.
        
    **Arguments**
        
    *orig_units*
        Either kg m-2 s-1 or K
        Will be converted to mm/day or Celsius

    *scale_offset*
        List: (scale,offset)
        new_data = (old_data*scale) + offset
        Performed after any unit conversion 
        (i.e. if orig_units are supplied)

    """
    #There would be scope to use the genutil udunits module
    #here, however I couldn't figure out how to get it to
    #do the rainfall conversion, plus then all file variables
    #would need to have unidata udunits consistent units
    
    # Switch units #
    
    if orig_units:
        if data.units[0:10] == 'kg m-2 s-1':
            new_data = numpy.ma.multiply(data,86400.0)
        elif units[0] = 'K':
            new_data = numpy.ma.subtract(data,273.16)
        else:
            print 'original units not recognised'
            sys.exit(1)
    else:
        new_data = data

    if scale_offset:
        new_data = numpy.ma.add(numpy.ma.multiply(new_data,float(scale_offset[0])),float(scale_offset[1]))
    
    return new_data


def _extract_region(region):
    """Obtains lat and lon info from a cdms2.selector region"""
    
    if isinstance(region, cdms2.selectors.Selector):
	for selector_component in region.components():
            if selector_component.id == 'lat':
                minlat = selector_component.spec[0]
                maxlat = selector_component.spec[1]
            elif selector_component.id == 'lon':
                minlon = selector_component.spec[0]
                maxlon = selector_component.spec[1] 
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
            * time=('1979-01-01', '2000-12-31')
            * units='Celcius', 'K','mm d-1', 'kg m-2 s-1'
	
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

        # Convert units #  ## Need to figure this out still

        if kwargs['units']:
            convert_units

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
	

#        def __getattr__(self, key):
#            try:
#        	return super(InputFile, self).__getattr__(key)
#            except AttributeError:
#        	if key in self.atts:
#                    return self.atts[key]
#        	else:
#                    raise
#
#        def __getattr__(self, attrName):
#            if not self.__dict__.has_key(attrName):
#                value = self.fetchAttr(attrName)    # computes the value
#                self.__dict__[attrName] = value
#            
#	    return self.__dict__[attrName]



    def temporal_subset(self, input_timescale, output_timescale, ):
        """Takes a temporal subset of the data.
        
        **Arguments**
        
        *input_timescale*
            Can be daily, monthly or yearly
        
        *output_timescale*
            Can be 
            * SEASONALCYCLE (i.e. DJF/MAM/JJA/SON)
            * ANNUALCYCLE (i.e. JAN/FEB/MAR/.../DEC)
            * YEAR
            * Any custom season (e.g. MJJASO, DJF)

        """
        #There would also be scope here to use the climatology and
        #departures methods, because the data will then retain a meaningful 
        #time axis
        #e.g. cdutil.ANNUALCYCLE.climatology       


        ## Set time bounds ##

        if input_timescale == 'daily':
            cdutil.setTimeBoundsDaily(self.data,frequency= )
        elif input_timescale == 'monthly':
            cdutil.setTimeBoundsMonthly(self.data)    # Need to check whether the time values are at the start or middle of month
        elif input_timescale == 'yearly':
            cdutil.setTimeBoundsYearly(self.data)
        else:
            print 'Unrecognised input timescale.'
            print 'Must be daily, monthly or yearly.'
            sys.exit(1)
        
        ## Extract subset of interest ##
        #I could add the option of months (e.g. JAN, FEB) here
        
        if output_timescale == 'SEASONALCYCLE':
            outdata = cdutil.SEASONALCYCLE(self.data)
        elif output_timescale == 'ANNUALCYCLE':
            outdata = cdutil.ANNUALCYCLE(self.data)
        elif output_timescale == 'YEAR':
            outdata = cdutil.YEAR(self.data)
        else:
            custom = cdutil.Seasons(output_timescale)
            outdata = custom(self.data)
    
        return outdata
    
#    def time_mean(self,season):
        

#    def smooth



#def write_outfile()
