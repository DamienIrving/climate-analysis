;*************************************************
; calc_streamfunction.ncl
;*************************************************

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

begin

;*************************************************
; open file and read in data: data are on a fixed grid
;*************************************************
  f    = addfile ("wind_Merra_250hPa_monthly_native_lon-shift.nc", "r")
  u    = f->ua
  v    = f->va

;*************************************************
; calculate streamfunction:
;*************************************************
  sf    = new ( dimsizes(u), typeof(u), u@_FillValue )  ; stream function
  vp    = new ( dimsizes(u), typeof(u), u@_FillValue )  ; velocity potential
  
  uv2sfvpg (u,v, sf,vp)            ; u,v ==> stream function + velocity pot

  copy_VarCoords(u, sf )  
  sf@long_name  = "Streamfunction"
  sf@units      = "m2 s-1"

;*************************************************
; write to netCDF file
;*************************************************   

  system("/bin/rm -f sf_Merra_250hPa_monthly_native_lon-shift.nc")   ; remove any pre-existing file
  ncdf  = addfile("sf_Merra_250hPa_monthly_native_lon-shift.nc" ,"c")  ; open output netCDF file
  
  ncdf->sf  = sf
  
end
