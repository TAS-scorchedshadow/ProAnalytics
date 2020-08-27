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

def compareBar():
    allStudentsTotal= {"SMITH_John": [7, 12], "JACK_Bob": [8, 6], "LI_Reginald": [9, 33], "VETTEL_Seb": [10,13],"CHILTON_Max": [11,20], "SENNA_Bruno": [12,27] }
    names = []
    scores = []
    year = []
    colour_list = []
    for i in allStudentsTotal:
        names.append(i)
        scores.append(int(allStudentsTotal[i][1]))
        year.append(int(allStudentsTotal[i][0]))

    for years in year:
        if years == 7:
            colour_list.append("blue")
        if years == 8:
            colour_list.append("red")
        if years == 9:
            colour_list.append("yellow")
        if years == 10:
            colour_list.append("green")
        if years == 11:
            colour_list.append("black")
        if years == 12:
            colour_list.append("orange")

    p_vbar = figure(x_range=names, plot_height=600, plot_width=(1000), title="Standings",
                    toolbar_location=None, tools="hover")
    p_vbar.hover.tooltips = [("Name", "@names"),("Score", "@scores")]
    p_vbar.vbar(names, top=(scores), color=colour_list, width=0.2)  # names are the x points, top of the bar graph creates the column from 0 on the y-axis, width specifies gap between the columns
    p_vbar.xgrid.grid_line_color = None
    p_vbar.vbar(names, scores, legend_label="Year 7", color="blue")
    p_vbar.vbar(names, scores, legend_label="Year 8", color = "red")
    p_vbar.vbar(names, scores, legend_label="Year 9", color="yellow")
    p_vbar.vbar(names, scores, legend_label="Year 10", color="green")
    p_vbar.vbar(names, scores, legend_label="Year 11", color="black")
    p_vbar.vbar(names, scores, legend_label="Year 12", color="orange")
    p_vbar.legend.title = 'Year Groups'
    p_vbar.y_range.start = 0  # ensures that the y-axis begins at 0
    script, div = components(p_vbar)
    return script, div