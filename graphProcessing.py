from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
from datetime import datetime
from bokeh.models import DatetimeTickFormatter, Legend, Range1d, LegendItem
from bokeh.palettes import Category10_10 as palette
from math import pi
from itertools import cycle

import time

from shotProcessing import validateShots

# values is a dictionary with each key being the name for the line.
# If comparing shooters, this can be the shooters name e.g Rishi Wig
# The values of each dictionary will be another dictionary that looks like the following:
# { 'yValue': [50, 46, 49] , 'xValue': ['10/08/2020', '11/08/2020', '12/08/2020']}
# where the list in xValue must be the same length as the list in yValue
# the dates can also include anything after the date if its separated by a space e.g '10/08/2020 15:30' or '10/08/2020 hello'
# everything after the space is ignored
# So an example of values would be
# {
# 'Andrew': { 'yValue': [50, 46, 49] , 'xValue': ['10/08/2020', '11/08/2020', '12/08/2020']} ,
# 'Rishi': { 'yValue': [50, 46, 49] , 'xValue': ['10/08/2020', '11/08/2020', '12/08/2020']}
# }
def compareLine(values, xLabel, yLabel, title):
    # break down values into three lists
    # listy is a list containing a list of scores eg. [ [50,46,48,49,50,50] , [50,44,50,49,48,49] ]
    # Each of the list of shots are one line and should all be the same length does
    # listx is a list of dates (dd/mm/yyyy) for each line eg. [['10/08/2020', '11/08/2020', '12/08/2020'],  ['13/08/2020', '14/08/2020', '15/08/2020']]
    # listName is a list of names eg. ['Andrew', 'Ryan']
    listx = []
    listy = []
    for shooter in values:
        for row in range(len(values[shooter]['xValue'])):
            values[shooter]['xValue'][row] = values[shooter]['xValue'][row].split(" ")[0]
    listName = []
    for key in values:
        listName.append(key)
        listx.append(values[key]['xValue'])
        listy.append(values[key]['yValue'])
    # vars used to set the x-axis range
    cLine = figure(plot_height=500, plot_width=1000, sizing_mode='scale_width', title=title,
                     x_axis_label=xLabel, y_axis_label=yLabel, x_axis_type='datetime',
                   )
    cLine.toolbar.logo = None
    # convert dates into a format we can use
    dates = []
    colours = cycle(palette)
    for shoot in listx:
        dates.append([])
        for day in shoot:
            dates[-1].append(time.mktime(datetime.strptime(day, "%d/%m/%Y").timetuple()) * 1000)
    legend_temp = []
    # Add lines
    for lineY, lineX, name, colour in zip(listy, dates, listName, colours):
        c = cLine.line(lineX, lineY, color=colour)
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
    cLine.xaxis.visible = True
    script, div = components(cLine)
    return script, div

#Designed to provide a comparison between shooters
#allStudentsTotal is a dictionary with the name as the key & the value as a list, where the first value is year & the second is the score
#mostly by Rishi Wig, some modifications by Henry Guo
def compareBar(username_one, username_two, score_one, score_two, xLabelBar, yLabelBar, titleBar):
    # init vars
    names = [username_one, username_two]
    scores = [score_one, score_two]
    colour_list = ["blue", "red"]
    label_year = [username_one, username_two]
    legendTemp = []

    # create ColumnDataSource
    source = ColumnDataSource(data=dict(
        name=names,
        score=scores,
        colour=colour_list,
    ))
    p_vbar = figure(x_range=names, plot_height=400, plot_width=800, sizing_mode='scale_width', x_axis_label = xLabelBar, y_axis_label=yLabelBar, title=titleBar,
                    toolbar_location=None, tools="hover")
    p_vbar.hover.tooltips = [
        ("Name", "@name"),
        ("Score", "@score")
    ]
    r = p_vbar.vbar('name', top='score', color='colour', width=0.2, source=source)  # names are the x points, top of the bar graph creates the column from 0 on the y-axis, width specifies gap between the columns
    p_vbar.xgrid.grid_line_color = None

    # add the labels (it was done this way so they are indexed correctly) https://discourse.bokeh.org/t/cant-order-legend-entries-in-hbar-plot/3816
    for label, num in zip(label_year, range(len(label_year))):
        legendTemp.append(LegendItem(label=label, renderers=[r], index=num))
    legend = Legend(items=legendTemp, title='Usernames', location='top_right')
    p_vbar.add_layout(legend)

    p_vbar.y_range.start = 0  # ensures that the y-axis begins at 0
    script, div = components(p_vbar)
    return script, div


def create_target(range_type):
    # Details are as follows: "Range": (Distance, V Ring, 5 Ring, 4 Ring, 3 Ring, 2 Ring)
    # Distance is in metres, rings are Diameters in mm
    target_details = {"300m": (300, 70, 140, 280, 420, 600),
                      "400m": (400, 95, 185, 375, 560, 800),
                      "500m": (500, 145, 290, 660, 1000, 1320),
                      "600m": (600, 160, 320, 660, 1000, 1320),
                      "700m": (700, 255, 510, 815, 1120, 1830),
                      "800m": (700, 255, 510, 815, 1120, 1830),
                      "300yds": (274.32, 65, 130, 260, 390, 560),
                      "400yds": (365.76, 85, 175, 350, 520, 745),
                      "500yds": (457.20, 130, 260, 600, 915, 1320),
                      "600yds": (548.64, 145, 290, 600, 915, 1320)}
    plot_size = 1700

    TOOLTIPS = [
        ("Shot", "@shotNum"),
        ("Score", "@score"),
        ("(x,y)", "(@x, @y)"),
    ]

    p = figure(plot_width=plot_size, plot_height=plot_size, tools=["hover"], sizing_mode="scale_width",toolbar_location=None, tooltips=TOOLTIPS)
    p.toolbar.logo = None
    # Draws the rings of the target from the largest to the smallest
    p.circle([0], [0], radius=int(target_details[range_type][5]/2), color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=int(target_details[range_type][4]/2), color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=int(target_details[range_type][3]/2), color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=int(target_details[range_type][2]/2), color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=int(target_details[range_type][1]/2), color="black", line_color="white", line_width=4)

    # Draws the gridlines of the target, from middle to left/top, then middle to right/bottom
    x = 0
    while x > -plot_size:
        p.line([x, x], [plot_size, -plot_size], line_color="gray", line_width=2)
        p.line([plot_size, -plot_size], [x, x], line_color="gray", line_width=2)
        x -= (291 * target_details[range_type][0]) / 1000
    x = (291 * target_details[range_type][0]) / 1000
    while x < 1400:
        p.line([x, x], [plot_size, -plot_size], line_color="gray", line_width=2)
        p.line([plot_size, -plot_size], [x, x], line_color="gray", line_width=2)
        x += (291 * target_details[range_type][0]) / 1000

    # Resize viewpoint so origin is at the middle and the entire graph is onscreen
    axis_limit = target_details[range_type][5]/2  # Height/Width of Graph
    p.y_range = Range1d(start=-axis_limit, end=axis_limit)
    p.x_range = Range1d(start=-axis_limit, end=axis_limit)

    # make the rest of the grid invisible so only the target is seen
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False

    # Make border
    p.border_fill_color = "slategray"
    return p


def drawTarget(shots, targetSize, groupRadius, groupCenter):
    # shots (dictionary of shots with their number and x,y positions {shotNum: [x, y, score], ...}
    # targetSize (str)
    # groupRadius (float)
    # groupCenter (tuple with 2 floats eg. (12.66, -32.5) )
    p = create_target(targetSize)   # Creates a target with the appropriate face
    # Required: x/y value of shot, shot number
    # Required: shot grouping radius, shot grouping center point
    # Required: target size

    # Tooltips code from https://docs.bokeh.org/en/latest/docs/user_guide/tools.html
    # ColumnDataSource is used instead to allow for tooltips
    shotX = []
    shotY = []
    score = []
    shotNum = []
    for i in shots:
        shotX.append(shots[i][0])
        shotY.append(shots[i][1])
        score.append(shots[i][2])
        shotNum.append(i)
    source = ColumnDataSource(data=dict(
        x=shotX,
        y=shotY,
        score=score,
        shotNum=shotNum
    ))
    p.select(type=HoverTool).names = ['shot']
    p.circle('x', 'y', radius=20, color="black", line_color="white", line_width=2, source=source, name='shot')
    p.text('x', 'y', text='shotNum', text_baseline="middle", text_align="center", color="white", source=source)
    # Uses stats_circle_center and stats_circle_radius in order to perform
    group_center = (12.66, -32.5)
    group_radius = 228.8
    p.circle([groupCenter[0]], [groupCenter[1]], radius=groupRadius, fill_alpha=0, line_color="yellow", line_width=4)
    script, div = components(p)
    return script, div


# Add a circle with the number of the shot in the middle
# x and y are the coordinates
# p is the figure object
# num is the number of the shot
def plotShot(p, x, y, num):
    p.circle([x], [y], size=30, color="black", line_color="white", line_width=2)
    p.text([x], [y], text=[str(num)], text_baseline="middle", text_align="center", color="white")
