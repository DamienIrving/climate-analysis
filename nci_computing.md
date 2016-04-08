# Climate and Weather Science Laboratory (CWSLab) project

* New website: http://cwslab.nci.org.au/
* Overview of CWSLab: http://www.cawcr.gov.au/projects/CWSLab/MAS.php  
* GitHub repo (plus wiki): https://github.com/CWSL  
* Vistrails user guide: http://www.vistrails.org/usersguide/v2.1/html/index.html  
* NCI environment modules: http://nci.org.au/services-support/getting-help/environment-modules/  
* NCI `/g/data/`: http://nci.org.au/services-support/getting-help/gdata-faqs-2/  
* ARCCSS CMIP wiki: http://climate-cms.unsw.wikispaces.net/CMIP5+data
* NCI CMIP community page: https://opus.nci.org.au/display/CMIP/CMIP+Community+Home
* ARCCSS support on slack: https://arccss.slack.com

Contacts:  

* General: cwslab@bom.gov.au
* NCI: help@nci.org.au


## CWS Virtual Desktop

### Access requirements

1. An NCI login with access to compute and storage resources
   
  * username: dbi599
  * compute/storage: I'm on r87 project, which means I should write to `/local/r87/dbi599/tmp`
    * Can also write to `/g/data/r87/dbi599`

2. A client application that enables connection using the secure shell protocol and a VNC client application
 
  * VNC client = TurboVNC  
  * Desktop launcher = Strudel  
  * Instructions: https://docs.google.com/document/d/1qx_BSd-WRSGW05_ZqSWt7bxxe3beCBrDIv9Nv6kB0QE/edit  
  
### Software solution

Install miniconda at `/g/data/r87/dbi599` and use conda environments.

### Long running jobs

If you go to the "TurboVNC Viewer" menu in the top left when quitting, it will give you the option of having the VM continue to run while you're logged out.

  
  
