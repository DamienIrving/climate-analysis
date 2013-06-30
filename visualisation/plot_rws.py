import plot_map


## Rossby wave source ##

infile_name = '/work/dbirving/datasets/Merra/data/processed/rws1_Merra_250hPa_daily_y73x144.nc'
outfile_name = '/work/dbirving/processed/spatial_maps/rws1_Merra_250hPa_daily-clim-1979-1983_y73x144.png'

infile_DJF = [infile_name, 'rws1', '1979-01-01', '2012-12-31', 'DJF']
infile_MAM = [infile_name, 'rws1', '1979-01-01', '2012-12-31', 'MAM']
infile_JJA = [infile_name, 'rws1', '1979-01-01', '2012-12-31', 'JJA']
infile_SON = [infile_name, 'rws1', '1979-01-01', '2012-12-31', 'SON']


infiles = [infile_DJF, infile_MAM, infile_JJA, infile_SON]

infile_data = plot_map.extract_data(infiles, region='nonpolar')

plot_map.multiplot(infile_data,
                   dimensions=[2,2],
                   ofile=outfile_name, 
                   title='Rossby_wave_source_(vortex_stretching_term)_climatology,_1979-1983', 
                   region='nonpolar', 
                   colourbar_colour='RdBu_r', 
                   ticks=[-30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30], 
                   units='$1 \\times 10^{-11} s^{-2}$',
                   extend="both",
                   img_headings=['DJF', 'MAM', 'JJA', 'SON'],
                   draw_axis=True, delat=17.5, delon=30, equator=True,
	           contour=True,
                   image_size=6)

#title='Rossby_wave_source_(advection_of_avrt_term)_climatology,_1979-1983',

print outfile_name


### Absolute vorticity ##
#
#infile_name = '/work/dbirving/datasets/Merra/data/processed/avrt_Merra_250hPa_daily_y73x144.nc'
#outfile_name = '/work/dbirving/processed/spatial_maps/avrt_Merra_250hPa_daily-clim-1979-1983_y73x144.png'
#
#infile_DJF = [infile_name, 'avrt', '1979-01-01', '2012-12-31', 'DJF']
#infile_MAM = [infile_name, 'avrt', '1979-01-01', '2012-12-31', 'MAM']
#infile_JJA = [infile_name, 'avrt', '1979-01-01', '2012-12-31', 'JJA']
#infile_SON = [infile_name, 'avrt', '1979-01-01', '2012-12-31', 'SON']
#
#
#infiles = [infile_DJF, infile_MAM, infile_JJA, infile_SON]
#
#infile_data = plot_map.extract_data(infiles, region='nonpolar')
#
#plot_map.multiplot(infile_data,
#                   dimensions=[2,2],
#                   ofile=outfile_name, 
#                   title='Absolute_vorticity_climatology,_1979-1983', 
#                   region='nonpolar', 
#                   colourbar_colour='RdBu_r', 
#                   ticks=[-30, -25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30], 
#                   units='$1 \\times 10^{-5} s^{-1}$',
#                   extend="both",
#                   img_headings=['DJF', 'MAM', 'JJA', 'SON'],
#                   draw_axis=True, delat=17.5, delon=30, equator=True,
#	           contour=True,
#                   image_size=6)
#
#print outfile_name
