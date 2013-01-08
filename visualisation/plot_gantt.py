"""
Creates a simple Gantt chart

"""

import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates
from matplotlib.dates import MONTHLY, DateFormatter, rrulewrapper, RRuleLocator

from pylab import *


def create_date(month,year):
    """Creates the date"""
    
    date = dt.datetime(int(year), int(month), 1)
    mdate = matplotlib.dates.date2num(date)
    
    return mdate


# Data    

pos = arange(0.5,2.5,0.5)
ylabels = ['Thesis','Impacts','Structure','Climatology']

task_dates = {}
task_dates['Climatology'] = [create_date(5,2013),create_date(8,2013),create_date(10,2013)]
task_dates['Structure'] = [create_date(10,2013),create_date(3,2014),create_date(5,2014)]
task_dates['Impacts'] = [create_date(5,2014),create_date(12,2014),create_date(2,2015)]
task_dates['Thesis'] = [create_date(2,2015),create_date(5,2015)]

# Initialise plot

fig = plt.figure()
ax = fig.add_axes([0.15,0.2,0.75,0.3])  #[left,bottom,width,height]

# Plot the data

start_date,end_date = task_dates['Thesis']
ax.barh(0.5, end_date - start_date, left=start_date, height=0.3, align='center', color='yellow')
for i in range(0,3):
    labels = ['analysis','write up'] if i == 1 else [None,None]
    start_date,mid_date,end_date = task_dates[ylabels[i+1]]
    ax.barh((i*0.5)+1.0, mid_date - start_date, left=start_date, height=0.3, align='center',label=labels[0], color='blue')
    ax.barh((i*0.5)+1.0, end_date - mid_date, left=mid_date, height=0.3, align='center',label=labels[1], color='yellow')

# Format the y-axis

locsy, labelsy = yticks(pos,ylabels)
plt.setp(labelsy,size='medium')


# Format the x-axis

ax.axis('tight')

ax.xaxis_date() #Tell matplotlib that these are dates...

rule = rrulewrapper(MONTHLY, interval=3)
loc = RRuleLocator(rule)
formatter = DateFormatter("%b '%y")

ax.xaxis.set_major_locator(loc)
ax.xaxis.set_major_formatter(formatter)
labelsx = ax.get_xticklabels()
plt.setp(labelsx, rotation=30, fontsize=10)

# Format the legend

font = font_manager.FontProperties(size='small')
ax.legend(loc=1,prop=font)

# Finish up

fig.autofmt_xdate()
plt.savefig('gantt.svg')
#plt.show()









