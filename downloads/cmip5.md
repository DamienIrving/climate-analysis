## Required CMIP5 data

Variable: `thetao` (and corresponding `volcello`)  
Timescale: `mon`   
Experiment: `historicalMisc` (and corresponding `piControl`)  

Models/runs (focusing on the anthropogenic aerosol only runs):  

| Model         | rip               | status                                                | location               |
| ---           | ---               | ---                                                   | ---                    |
| CanESM2       | `r[1-5]i1p4`      | Got all data.                                         | `/g/data/ua6`          | 
| CCSM4         | `r[1,4,6]i1p10`   | No idea where data is. Need to contact.               | Schmidt (2014) says ?? |
| CESM1-CAM5    | `r[1,2,3]i1p10`   | No idea where data is. Need to contact.               | Schmidt (2014) says ?? |
| CSIRO-Mk3.6   | `r[1-10]i1p4`     | Got all data.                                         | `/g/data/ua6`          |
| FGOALS-g2     | `r2i1p1`          | Edit symlinks and check it's all there.               | `/g/data1/ua6/NCI_replica_tmp/ua6_cet900_sort/` |
| GFDL-CM3      | `r[1,3,5]i1p1`    | Got all data.                                         | `/g/data/ua6`          |  
| GFDL-ESM2M    | `r1i1p5`          | AA only for thetao. Need to contact re other exp.     | ESGF-LLNL              |    
| GISS-E2-H     | `r[1-5]i1p107`    | No idea where data is. Need to contact.               | Schmidt (2014)         |
|               | `r[1-5]i1p310`    | No idea where data is. Need to contact.               | Schmidt (2014)         |
| GISS-E2-R     | `r[1-5]1p107`     | No idea where data is. Need to contact.               | Schmidt (2014)         |
|               | `r[1-5]1p310`     | No idea where data is. Need to contact.               | Schmidt (2014)         | 
| IPSL-CM5-LR   | `r1i1p3`          | No piControl for thetao.                              | ESGF-DKRZ              |
| NorESM1-M     | `r1i1p1`          | No idea where data is. Need to contact.               | Schmidt (2014)         |

Data already on NCI are labelled as `/g/data/ua6`.  
Data that turn up on searches on other ESGF nodes (but are not on NCI) are labelled "ESGF".  
Data that are in [a document](http://cmip-pcmdi.llnl.gov/cmip5/docs/historical_Misc_forcing.pdf) listing all historicalMisc runs are labelled Schmidt (2014). These data aren't on NCI and don't turn up in searches of other ESGF nodes.
