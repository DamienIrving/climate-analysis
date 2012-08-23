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

  ;*****************************************************
  ; open file and read in data: data are on a fixed grid
  ;*****************************************************
  var   = "vp"  ; vp, sf, uad, vad
  
  f     = addfile ("/work/dbirving/datasets/Merra/data/processed/wind_Merra_250hPa_monthly-clim-1981-2010_native.nc", "r")
 
  months = (/"jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"/) 
  uwinds = (/"ua_jan","ua_feb","ua_mar","ua_apr","ua_may","ua_jun","ua_jul","ua_aug","ua_sep","ua_oct","ua_nov","ua_dec"/)
  vwinds = (/"va_jan","va_feb","va_mar","va_apr","va_may","va_jun","va_jul","va_aug","va_sep","va_oct","va_nov","va_dec"/)
  
  do i = 0,dimsizes(months)-1
 
    u = f->$uwinds(i)$
    v = f->$vwinds(i)$

    if (var .eq. "vp" .or. var .eq. "sf") then

      ;*************************************************
      ; calculate streamfunction and velocity potential:
      ;*************************************************
    
      sf  = new ( dimsizes(u), typeof(u), u@_FillValue )  ; stream function
      vp  = new ( dimsizes(u), typeof(u), u@_FillValue )  ; velocity potential

      uv2sfvpg (u,v, sf,vp)            ; u,v ==> stream function + velocity pot

      copy_VarCoords(u, sf )  
      sf@long_name  = "Streamfunction"
      sf@units      = "m2 s-1"

      copy_VarCoords(u, vp )  
      vp@long_name  = "Velocity potential"
      vp@units      = "m2 s-1"

    else
      
      ;*************************************************
      ; calculate divergent wind components:
      ;************************************************* 
    
      div   = uv2dvG_Wrap(u,v)             ; u,v ==> divergence

      uad    = new ( dimsizes(u), typeof(u), u@_FillValue )
      vad    = new ( dimsizes(v), typeof(v), v@_FillValue )

      dv2uvg(div,uad,vad) ; div  ==> divergent  wind components

      copy_VarCoords(u, uad ) 
      uad@long_name  = "Zonal Divergent Wind"
      uad@units      = u@units

      copy_VarCoords(v, vad ) 
      vad@long_name  = "Meridional Divergent Wind"
      vad@units      = v@units

    end if
    
    ;*************************************************
    ; write to netCDF file
    ;*************************************************   
    
    strs = (/"/work/dbirving/datasets/Merra/data/processed/",var,"_Merra_250hPa_monthly-clim-1981-2010_native",months(i),".nc"/)
    outfile = str_concat(strs)
    
    system("rm -f " + outfile)   ; remove any pre-existing file
    ncdf  = addfile(outfile,"c")
    
    if (var .eq. "vp") then
      ncdf->vp = vp
    else if (var .eq. "sf") then
      ncdf->sf = sf
    else if (var .eq. "uad") then
      ncdf->uad = uad
    else 
      ncdf->vad = vad
    end if
    end if
    end if

  end do
  
end

