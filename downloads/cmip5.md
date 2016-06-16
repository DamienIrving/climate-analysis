## Required CMIP5 data

Variable: `thetao` (and corresponding `volcello`)  
Timescale: `mon`   
Experiment: `historicalMisc` (and corresponding `piControl`)  

Models/runs (focusing on the anthropogenic aerosol only runs):  

| Model         | rip               | location        |
| ---           | ---               | ---             | 
| CanESM2       | `r[1-5]i1p4`      | `/g/data/ua6`   | 
| CCSM4         | `r[1,4,6]i1p10`   | Schmidt (2014)  |
| CESM1-CAM5    | `r[1,2,3]i1p10`   | Schmidt (2014)  |
| CSIRO-Mk3.6   | `r[1-10]i1p4`     | `/g/data/ua6`   |
| FGOALS-g2     | `r2i1p1`          | Paola says it's in the NCI "bulk transfer data" |
| GFDL-CM3      | `r[1,3,5]i1p1`    | `/g/data/ua6`   |  
| GFDL-ESM2M    | `r1i1p5`          | ESGF            |     
| GISS-E2-H     | `r[1-5]i1p107`    | Schmidt (2014)  |
|               | `r[1-5]i1p310`    | Schmidt (2014)  |
| GISS-E2-R     | `r[1-5]1p107`     | Schmidt (2014)  |
|               | `r[1-5]1p310`     | Schmidt (2014)  | 
| IPSL-CM5-LR   | `r1i1p3`          | EGGF            |
| NorESM1-M     | `r1i1p1`          | Schmidt (2014)  |

Data already on NCI are labelled as `/g/data/ua6`.  
Data that turn up on searches on other ESGF nodes (but are not on NCI) are labelled "ESGF".  
Data that are in [a document](http://cmip-pcmdi.llnl.gov/cmip5/docs/historical_Misc_forcing.pdf) listing all historicalMisc runs are labelled Schmidt (2014). These data aren't on NCI and don't turn up in searches of other ESGF nodes.
