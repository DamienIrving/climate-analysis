;*************************************************
; calc_streamfunction.ncl
;*************************************************
;to execute, run a command line ncl session (>> ncl)
;then >>load "calc_streamfunction.ncl"

;NCARG_ROOT = /usr/local
;load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

load "/usr/local/lib/ncarg/nclscripts/csm/gsn_code.ncl"   
load "/usr/local/lib/ncarg/nclscripts/csm/gsn_csm.ncl"  
load "/usr/local/lib/ncarg/nclscripts/csm/contributed.ncl"
begin

;*************************************************
; open file and read in data: data are on a fixed grid
;*************************************************
  f    = addfile ("/work/dbirving/datasets/Merra/data/processed/wind_Merra_250hPa_monthly-clim-1981-2010_native.nc", "r")
  u    = f->ua
  v    = f->va

;*************************************************
; calculate streamfunction and velocity potential:
;*************************************************
;  sf    = new ( dimsizes(u), typeof(u), u@_FillValue )  ; stream function
;  vp    = new ( dimsizes(u), typeof(u), u@_FillValue )  ; velocity potential
  
;  uv2sfvpg (u,v, sf,vp)            ; u,v ==> stream function + velocity pot

;  copy_VarCoords(u, sf )  
;  sf@long_name  = "Streamfunction"
;  sf@units      = "m2 s-1"

;  copy_VarCoords(u, vp )  
;  vp@long_name  = "Velocity potential"
;  vp@units      = "m2 s-1"

;*************************************************
; calculate divergent wind components:
;*************************************************
  div   = uv2dvG_Wrap(u,v)             ; u,v ==> divergence
  
  uad    = new ( dimsizes(u), typeof(u), u@_FillValue )
  vad    = new ( dimsizes(v), typeof(v), v@_FillValue )

  dv2uvg(div,uad,vad) ; div  ==> divergent  wind components

;  copy_VarCoords(u, uad ) 
;  uad@long_name  = "Zonal Divergent Wind"
;  uad@units      = u@units

   copy_VarCoords(v, vad ) 
   vad@long_name  = "Meridional Divergent Wind"
   vad@units      = v@units
  

;*************************************************
; write to netCDF file
;*************************************************   

;  system("/bin/rm -f /work/dbirving/datasets/Merra/data/sf_Merra_250hPa_monthly-anom-wrt-1981-2010_native.nc")   ; remove any pre-existing file
  ncdf  = addfile("/work/dbirving/datasets/Merra/data/processed/vad_Merra_250hPa_monthly-clim-1981-2010_native.nc" ,"c")  ; open output netCDF file
  
  ncdf->vad  = vad
  
end
