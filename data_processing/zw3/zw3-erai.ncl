
; Calculates the positive and negative phases of zw3 index. 
;
; Notes:
;  ** the /nclGSUN/ scripts loaded below are
;     required to use Mary Haley's simplified
;     plot interfaces.
;
;************************************************
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/shea_util.ncl"

;*********************************************************
begin

nyrst  = 1979
nyren  = 2011 
nyrs   = (nyren - nyrst) +1			
nyr1   = (nyrs*12)
nyrm   = nyr1 - 1	
nlat    = 121
mlon    = 240				; assigning values for plotting
nmos    = 12
ntime   = nyr1
yrs     = new ((/nyrs/), float)			; create year array
yrs     = fspan (nyrst, nyren, nyrs)		

plev = 850.

gphfile = new((/nyr1,nlat,mlon/), "float")                 	; create new arrays to graph
gphdata = new((/nyr1/), float)
;time    = new((/nyr1/), "float")
datedata = new((/nyr1/), string)

wvindex76W =new ((/nyr1/), "float")		; declaring index variables
wvindex50E =new ((/nyr1/), "float")
wvindex166 =new ((/nyr1/), "float")
zw3za   =new ((/nyr1/), "float")
Zdata      =new ((/nyr1, nlat, mlon/), "float")                        	; declaring variables
datatp     =new ((/nyr1, nlat, mlon/), "float")
Zsum       =new ((/12, nlat, mlon/), "float")
Zbar       =new ((/12, nlat, mlon/), "float")
sgma       =new ((/12, nlat, mlon/), "float")
Zstar      =new ((/nyr1, nlat, mlon/), "float")


;time!0          = "time"                                 	; assigning a name to the 0 index
gphfile!0       = "time"




yrmo= new((/nyr1/), float)   			; array containing year+fraction of year
m = -1
do k = 0, nyrm, 12
  m = m + 1
  do nmo = 0,nmos-1
yrmo(nmo+k) = yrs(m) + nmo/12.
 end do
end do
;
;print(yrmo)



  FILS = new (1,"string")
 
; FILS(0) = "eraiz.mon.mean.nc"
  FILS(0) = "z.mon.mean.nc"
;********************************************
; Read in data
;********************************************
  print ("===> Wall Clock Start: ZA: "+systemfunc("date"))
; DIRI  = "/u/raphael/"                                                	; read in any data
  DIRI  = "/chade/raphael/"                                                	; read in any data

  PATH  = DIRI+FILS
  g     = addfiles (PATH, "r")
  ListSetType (g, "cat")
 print("done ListSetType")
  dgph   = addfiles_GetVar (g, PATH, "z" )                           	; get data from the files
print("done addfiles")
  printVarSummary(dgph)
  lat = dgph&latitude
  lon = dgph&longitude
  data=dgph(0:395,{500},:,:)                   	; strip off data at desired level, time period, etc.
  printVarSummary(data)
print ("===> Wall Clock End  : ZA: "+systemfunc("date"))
 

t1 = data&time

time = ut_calendar(t1, -1)
;print(time)
time!0 = "time"

Zdata = dim_rmvmean(data(:,:,:)) 			; create zonal anomaly 
; Zdata = dim_rmvmean((data(:,:,:)/9.80665)) 			; create zonal anomaly 
printVarSummary(Zdata)

print("FINISHED WITH ZDATA, NOW ON TO WVINDEX")
wvindex76W!0 = "time"			; naming and assigning attributes
wvindex50E!0 = "time"			; to variables at each index node. 
wvindex166!0 = "time"
wvindex76W&time = time
wvindex50E&time = time
wvindex166&time = time						

zw3za!0="time"
zw3za&time = time

Zdata!0="time"						 
Zdata!1="lat"						
Zdata!2="lon"
Zdata&time = time
Zdata&lat = lat
Zdata&lon = lon

Zstar!0="time"
Zstar!1="lat"
Zstar!2="lon"
Zstar&time = time
Zstar&lat = lat
Zstar&lon = lon


;*************************************************************************************************
;       Calculating Average Index

;*************************************************************************************************

print ("Calculating average index")

do mo = 0,11                                    ; Calculating climatological
Zsum(mo,:,:) = 0.0				; monthly means and sigmas
        k=0                                             
do l=0,nyrm,12
        Zsum(mo,:,:) = Zsum(mo,:,:) + Zdata((l+mo),:,:)
        datatp(k,:,:)=Zdata((l+mo),:,:)                 ; A new array for sigma
        k=k+1
end do
Zbar(mo,:,:)=Zsum(mo,:,:)/nyrs
sgma(mo,:,:) = dim_stddev (datatp(lat|:,lon|:,time|:))
end do
 
do l=0,nyrm,12					; Calculating Index 
do mo = 0,11
   Zstar((l+mo),:,:)=(Zdata((l+mo),:,:)-Zbar(mo,:,:))/(sgma(mo,:,:) + 1.0)

  wvindex76W(l+mo) = Zstar((l+mo),{-49.0},{284.});   assign specific lat and lon to index arrays  
  wvindex50E(l+mo) = Zstar((l+mo),{-49.0},{50.0})
  wvindex166(l+mo) = Zstar((l+mo),{-49.0},{166.0})
  zw3za(l+mo)=(wvindex76W(l+mo)+wvindex50E(l+mo)+wvindex166(l+mo))/3.0 ; Spatial avg of indices 

end do
end do

;*******************************************
; write index to file
;*******************************************
 diro           = ""
 filo           = "zw3index-erai-"+nyrst+"-"+nyren+"_"+plev+".nc"

 system ("rm "+diro+filo)

 fo = addfile (diro+filo, "c")


 fo@title       = "ZW3 index at "+plev+"mb "+nyrst+"-"+nyren
 fo@history     = systemfunc ("date")
 fo@source      = "ERA Interim  REANALYSIS"
 fo@time        = time 
 fo->zw3era      = zw3za
 fo->time       = time



;************************************************************************
; Calculating Average and Standard Deviation

;************************************************************************

print ("Calculating average and standard deviation")
avrg=avg(zw3za(:))
stdv=stddev(zw3za(:))

stdplus=(avrg + 1*stdv)			; Setting up the thesholds for outlier data
stdminus=(avrg - 1*stdv)

;************************************************************************
; Finding month and year with much larger than average  data and setting up difference plots
;************************************************************************
print ("Searching for months with strongly positive index")

posZ    =new((/nlat, mlon/), "float")
negZ    =new((/nlat, mlon/), "float")
avgposZ =new((/nlat,mlon/), "float")
avgnegZ =new((/nlat,mlon/), "float")
diffavgZ=new((/nlat,mlon/), "float")

do kn = 0,nlat-1
     do knn = 0,mlon-1
        posZ(kn,knn) = 0.0
     end do
end do

  l=0
  do n = 0,nyrm
    if (zw3za(n).gt.stdplus) then  
	posZ(:,:)=Zdata(n,:,:)+posZ(:,:)
print("strongly positive index")
print(n)

	l=l+1
    end if
  end do
;print (l)
;print(posZ)
print ("Searching for months with strongly negative index data")
do kn = 0,nlat-1
     do knn = 0,mlon-1
        negZ(kn,knn) = 0.0
     end do
end do

  m=0
  do n = 0,nyrm
    if (zw3za(n).lt.stdminus) then  
	negZ(:,:)=Zdata(n,:,:)+negZ(:,:)
print("strongly negative index")
print(n)

	m=m+1
    end if
  end do
print (m)
  
;************************************************
; Average of geopotential heights based on n
;************************************************
print ("Calculating the spatial average of GPH for each used month")

posZ!0="lat"				
posZ!1="lon"
posZ&lat = lat
posZ&lon = lon

negZ!0="lat"				
negZ!1="lon"
negZ&lat = lat
negZ&lon = lon

avgposZ = posZ (:,:)/l			; creating the average GPH for pos anomalies
avgposZ!0="lat"		
avgposZ!1="lon"
avgposZ&lat = lat
avgposZ&lon = lon
				; creating the average GPH for neg anomalies
avgnegZ = negZ (:,:)/m	
avgnegZ!0="lat"
avgnegZ!1="lon"
avgnegZ&lat = lat
avgnegZ&lon = lon

printVarSummary(avgposZ)
printVarSummary(avgnegZ)


diffavgZ= avgposZ-avgnegZ		; creating a difference field between the two GPH fields
diffavgZ!0="lat"
diffavgZ!1="lon"
diffavgZ&lat = lat
diffavgZ&lon = lon

;****************************************
; Plotting anomaly maps and index
;*****************************************

print ("Plotting Positive  Anomaly Map")

wks = gsn_open_wks("ps", plev+"zw3-erai-19792012")	; Plotting a line graph of index vs time

res              = True				; plot mods desired
 res@gsnFrame        = False                        	    
res@gsnPolar     = "SH"                    			; specify the hemisphere
res@mpMaxLatF    = -20.
res@mpGridLatSpacingF = 30.
res@mpGridLonSpacingF = 90.
res@cnFillOn             = False                        ; turn on color fill
res@cnLinesOn            = True
res@cnLineLabelsOn       = True          	; turn on/off contour line labels
res@cnInfoLabelOn        = False
res@cnMonoLineThickness  = True     	     	; turn on/off choice of thickness
res@cnLineThicknessF     = 3.0               	; choose contour thickness
res@cnLevelSelectionMode = "AutomaticLevels"    	; set manual contour levels
; res@cnLevelSelectionMode = "ManualLevels"    	; set manual contour levels
res@cnMinLevelValF       = -100.          	; set min contour level
res@cnMaxLevelValF      =   100.            	; set max contour level
; res@cnLevelSpacingF       =     20.              	; set contour spacing
res@cnLabelMasking       = True         	; do not draw labels over contour


res@tiMainString  = "Asymmetry for Positive "+plev+"hPa ZW3 Anomalies ERAI "+nyrst+"-"+nyren 
res@gsnLeftString  = " ERAI-POS"  	
plot1= gsn_csm_contour_map_polar(wks,avgposZ,res) 	       
frame (wks)

print ("Negative Index Anomalies Map")

res@gsnLeftString  = "ERAI-NEG"  	
res@tiMainString  = "Asymmetry for Negative "+plev+"hPa ZW3 Anomalies ERAI"+nyrst+"-"+nyren
plot2= gsn_csm_contour_map_polar(wks,avgnegZ,res)
frame (wks)

print ("Difference Plot of Anomalies")

res@gsnLeftString  = "ERAI"  	
res@tiMainString  = "ZW3 Asymmetry Difference Pos - Neg"+nyrst+"-"+nyren
plot3= gsn_csm_contour_map_polar(wks,diffavgZ,res)
plot3= ShadeLtContour(plot3, 0.0, 3)
frame (wks)
;*************************************************************************************************
;               Spectral Analysis
;
;               set function arguments

;*************************************************************************************************
        d       =0      ; detrending opt:  0=>remove mean 1=>remove mean + detrend
        sm      =5      ; smooth: should be at least 3 and odd
        pct     =0.10   ; percent taper: (0.0 <=pct <=1.0) 0.10 common
;******************************************************
; Calculate spectrum and confidence interval
;******************************************************

print ("Performing and plotting the spectral analysis")

res                 = True       		     	 ; set resources

Iavespec=specx_anal(zw3za(:),d,sm,pct)                ; spectral analysis for anomalies
spltIave=specx_ci(Iavespec, 0.05, 0.95)              ; spectral confidence interval

res@tiMainString = "Spectral Analysis of "+plev+"hPa ZW3 Index  ERAI "+nyrst+"-"+nyren
res@tiXAxisString= "Frequency (cycles/month)"                  
res@tiYAxisString= "Variance"                                  
res@xyLineColors = (/"foreground","green","blue","red"/)
plot4 = gsn_csm_xy(wks, Iavespec@frq, spltIave, res)
frame(wks)

;*********************************************************
;Plotting a line graph of the average index
;*********************************************************

 print ("Plotting Index Timeseries")

 res                 = True      		        ; set resources

  res@cnLinesOn       = False
 res@tiMainString = plev+"hPa ZW3 Index ERAI "+nyrst+"-"+nyren
 res@tiYAxisString   = "Index value"
 res@tiXAxisString   = "Time in months"
 res@trXMinF       = nyrst                         	       ; Set minimum X axis value.
  
 res@vpHeightF= 0.2                                      ; change aspect ratio of plot
 res@vpWidthF = 0.7              

 res@gsnYRefLine           = 0.0                ; create a reference line  
 res@gsnXYBarChart         = True              ; create bar chart 
 res@gsnAboveYRefLineColor = "red"             ; above ref line fill red
 res@gsnBelowYRefLineColor = "blue"            ; below ref line fill blue
 res@xyLineColors = (/"red","blue","",""/)

plot5 = gsn_csm_xy(wks,yrmo(:),zw3za(:),res)
frame(wks)

end
