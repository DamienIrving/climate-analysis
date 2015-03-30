import sys, pdb
import cdms2

infile = sys.argv[1]
var = sys.argv[2]

fin = cdms2.open(infile)
try:
    data = fin(var, latitude=(-50,-48), longitude=(10,12))
except cdms2.error.CDMSError:
    data = fin(var)

times = data.getTime().asComponentTime()

pdb.set_trace()

print times[-1]
