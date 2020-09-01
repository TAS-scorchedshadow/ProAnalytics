from bokeh.plotting import figure, ColumnDataSource
from bokeh.embed import components
from bokeh.models import HoverTool
from datetime import datetime as dt
from bokeh.models import DatetimeTickFormatter, Legend, Range1d, LegendItem
from bokeh.palettes import Colorblind3 as palette
from math import pi
from itertools import cycle

from shotProcessing import validateShots


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
    # init vars
    names = []
    scores = []
    year = []
    colour_list = []
    label_year = ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11", "Year 12"]
    legendTemp = []
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

    # create ColumnDataSource
    source = ColumnDataSource(data=dict(
        name=names,
        score=scores,
        colour=colour_list,
    ))
    p_vbar = figure(x_range=names, plot_height=600, plot_width=1000, title="Standings",
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
    legend = Legend(items=legendTemp, title='Year Groups', location='top_right')
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
    # Draws the circles of the target from the largest to the smallest
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
    # shots (dictionary of shots with their number and x,y positions {shotNum: [x, y, score] ...}
    # targetSize (str)
    # groupRadius (float)
    # groupCenter (tuple with 2 floats eg. (12.66, -32.5) )
    p = create_target(targetSize)   # Creates a target with the appropriate face
    # todo: Change this to pull from database info instead of directly from json
    # Required: x/y value of shot, shot number
    # Required: shot grouping radius, shot grouping center point
    # Required: target size

    # Tooltips code from https://docs.bokeh.org/en/latest/docs/user_guide/tools.html
    # ColumnDataSource is used instead to allow for tooltips
    shotX = []
    shotY = []
    score = []
    print(shots)
    for i in range(1, len(shots)+1):
        shotX.append(shots[i][0])
        shotY.append(shots[i][1])
        score.append(shots[i][2])
    source = ColumnDataSource(data=dict(
        x=shotX,
        y=shotY,
        score=score,
        shotNum=range(1, len(shots)+1)
    ))
    p.select(type=HoverTool).names = ['shot']
    p.circle('x', 'y', size=30, color="black", line_color="white", line_width=2, source=source, name='shot')
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
