from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d


# Target rendering (Possibly unused)
# -- Ryan T --
def create_target(range_type):
    # Dimensions are obtained from:
    # https://en.wikipedia.org/wiki/Shooting_target#International_Confederation_of_Fullbore_Rifle_Associations
    # Details are as follows: "Range": (Distance, V Ring, 5 Ring, 4 Ring, 3 Ring, 2 Ring)
    # Distance is in metres. Rings are diameters in mm
    target_details = {"300m": (300, 70, 140, 280, 420, 600),
                      "400m": (400, 95, 185, 375, 560, 800),
                      "500m": (500, 145, 290, 660, 1000, 1320),
                      "600m": (600, 160, 320, 660, 1000, 1320),
                      "700m": (700, 255, 510, 815, 1120, 1830),
                      "800m": (800, 255, 510, 815, 1120, 1830),
                      "300yds": (274.32, 65, 130, 260, 390, 560),
                      "400yds": (365.76, 85, 175, 350, 520, 745),
                      "500yds": (457.20, 130, 260, 600, 915, 1320),
                      "600yds": (548.64, 145, 290, 600, 915, 1320)}
    plot_size = 1700

    p = figure(plot_width=plot_size, plot_height=plot_size, tools="", sizing_mode="scale_width", toolbar_location=None)
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
