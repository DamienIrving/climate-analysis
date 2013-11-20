# Common commands

| Task   | Command    |
| ------ | ------:    |
|  Git   | ```
           git clone
           git add
           ``` |
|        | git add |
|        | git commit -m "comment |
|        | git push -u origin master | 
|        | git pull |
| Checking jobs | top |
|               | -u STUDENT\\dbirving (shows just my jobs) |
|               | -r (renice the job) |
|               | -k (kill the job) |
| Run job in background (can log out) | nohup nice myscript.py  |
| | |
| | |
| | |
| | |
| | |
| | |
| | |       



### CMIP tos data

Some of this data are on a triangulated grid. To get them onto a regular lat/lon grid, you need to use the following cdo command (at least that's what they've done at CSIRO)

cdo remapbil,sftlf.nc tos.nc out.nc

Note that sftlf.nc is the file that it copies the new grid from.
