## Location ##

http://www.metoffice.gov.uk/hadobs/hadisst/data/download.html
(downloaded 13 August 2012)
This is HadISST1.
There is no uncertainty data.

## Variables ##

Sea surface temperature (was sst, now tos)


## Post processing ##

cdo sellonlatbox,0,359.9,-90,90       # For having longitude values 0 to 360, instead of -180 to 180
cdo invertlat (the original files go from N to S instead of S to N)
cdo chname,sst,tos
