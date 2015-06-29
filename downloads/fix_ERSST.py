# Read the input file, read the data and flatten the spatial dimension #
   
climate_index = 'NINO4'   

if climate_index == 'NINO34':
    minlat,maxlat,minlon,maxlon = [-5,5,190,240]
elif climate_index == 'NINO3':
    minlat,maxlat,minlon,maxlon = [-5,5,210,270]
elif climate_index == 'NINO4':
    minlat,maxlat,minlon,maxlon = [-5,5,160,210]
elif climate_index == 'NINO12':
    minlat,maxlat,minlon,maxlon = [-10,0,270,280]


# Read the data #
ifile = '/work/dbirving/processed/indices/data/tos_ERSSTv3b-download_NINO_monthly_native.txt'

years = []
months = []
data = []
raw = []

fin = open(ifile,'r')
line = fin.readline()
switch = False
while line:

    if line.split()[0] == 'YR':
	loc = line.split().index(climate_index)
	switch = True

    elif switch: 
	year = line.split()[0]
	month = line.split()[1]
	temp_data = line.split()[loc+1]
	temp_raw = line.split()[loc]
	
	years.append(int(year))
	months.append(int(month))
	data.append(float(temp_data))
	raw.append(float(temp_raw))

    line = fin.readline()


# Write the output file #

fout = open('/work/dbirving/processed/indices/data/tos_ERSSTv3b-download_'+climate_index+'_monthly_native.txt','w')
coords = ' (lat: %s to %s, lon: %s to %s)' %(str(minlat),str(maxlat),str(minlon),str(maxlon))
title = climate_index+coords+'\n'
fout.write(title)
base = 'Base period = 1981  to 2010 \n'
fout.write(base)  
version_info = 'Created 17 August 2012 using fix_ERSST.py, data from http://www.cpc.ncep.noaa.gov/data/indices/ \n'
fout.write(version_info)
fout.write('Input file = '+ifile+'\n')

print year

headers = ' YR   MON  %s   raw \n' %(climate_index)
fout.write(headers) 
for ii in range(0,len(years)):
    print >> fout, '%4i %3i %7.2f %7.2f' %(years[ii],months[ii],data[ii],raw[ii])

fout.close()

print '/work/dbirving/processed/indices/data/tos_ERSSTv3b-download_'+climate_index+'_monthly_native.txt'
