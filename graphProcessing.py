from bokeh.plotting import figure
from bokeh.embed import components
from datetime import datetime as dt
from bokeh.models import DatetimeTickFormatter, Legend
from bokeh.palettes import Colorblind3 as palette
from math import pi
from itertools import cycle


# listx is a list containing a list of scores eg. [ [50,46,48,49,50,50] , [50,44,50,49,48,49] ]
# Each of the list of shots are one line and should all be the same lengthdoes
# listy is a list of dates (dd/mm/yyyy) eg. ['10/08/2020', '11/08/2020', '12/08/2020', '13/08/2020', '14/08/2020', '15/08/2020']
# listName is a list of names eg. ['Andrew', 'Ryan']
def compareLine(listx, listy, listName):
    # vars used to set the x-axis range
    startRange = listy[0].split('/')
    endRange = listy[-1].split('/')
    cLine = figure(plot_height=1000, plot_width=1000, sizing_mode='scale_width', title='Compare Graph',
                   x_axis_label='Date', y_axis_label='Score', x_axis_type='datetime',
                   x_range=(dt(int(startRange[2]), int(startRange[1]), int(startRange[0])), dt(int(endRange[2]), int(endRange[1]), int(endRange[0]))))
    # convert dates into a format we can use
    dates = []
    colours = cycle(palette)
    for day in listy:
        dateList = day.split('/')
        dates.append(dt(int(dateList[2]), int(dateList[1]), int(dateList[0])))

    legend_temp = []
    # Add lines
    for line, name, colour in zip(listx, listName, colours):
        c = cLine.line(dates, line, color=colour)
        legend_temp.append((name, [c]))
    legend = Legend(items=legend_temp)
    cLine.add_layout(legend, 'right')

    # Format x-axis into datetime
    cLine.xaxis.formatter = DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    # Rotate labels on the x-axis
    cLine.xaxis.major_label_orientation = pi / 4
    script, div = components(cLine)
    return script, div
