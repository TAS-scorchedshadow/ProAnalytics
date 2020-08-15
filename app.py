from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort
from flask_bootstrap import Bootstrap
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d
from shotProcessing import validateShots, getScore
from uploadForms import uploadForm
from werkzeug.utils import secure_filename
from drawtarget import create_target
import os

app = Flask(__name__)
app.secret_key = "super secret"
bootstrap = Bootstrap(app)
array_shots = [[150, 0], [300, 100], [499, 700]]


@app.route('/')
@app.route('/home')
def home():
    jsonID = 1551500850141  # ID of json file
    filePath = "testJson/string-" + str(jsonID) + ".txt"
    s = validateShots(filePath)
    for i in range(len(s['validShots'])):
        score = getScore(s['validShots'][i])
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # create form
    form = uploadForm()

    # on submission
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            filename = secure_filename(file.filename)
            file.save(os.path.join('F:\\Pycharm\\Pycharm Projects\\ProAnalytics\\testJson', filename))
    return render_template('upload.html', form=form)


@app.route('/target')
def drawTarget():
    p = create_target("300m")   # Creates a target with the 300m face
    # todo: Change this to pull from database info instead of directly from json
    # Required: x/y value of shot, shot number
    # Required: shot grouping radius, shot grouping center point
    # Required: target size

    # add a shot (test)
    jsonID = 1592616479803  # ID of json file
    filePath = "testJson/string-" + str(jsonID) + ".txt"
    s = validateShots(filePath)['validShots']
    for i in range(len(s)):
        plotShot(p, s[i]['x'], s[i]['y'], i + 1)
    # Uses stats_circle_center and stats_circle_radius in order to perform
    # Currently hardcoded to json 1592616479803
    group_center = (12.66, -32.5)
    group_radius = 228.8
    p.circle([group_center[0]], [group_center[1]], radius=group_radius, fill_alpha=0, line_color="yellow", line_width=4)
    script, div = components(p)
    return render_template('target.html', script=script, div=div)


# Add a circle with the number of the shot in the middle
# x and y are the coordinates
# p is the figure object
# num is the number of the shot
def plotShot(p, x, y, num):
    p.circle([x], [y], size=30, color="black", line_color="white", line_width=2)
    p.text([x], [y], text=[str(num)], text_baseline="middle", text_align="center", color="white")

# Using the

@app.route('/comparitiveBar')
def comparitiveBar():

    allStudentsTotal= {"SMITH_John": [7, 12], "JACK_Bob": [7, 6], "LI_Reginald": [9, 33]}
    year7name = []
    year7points = []
    year8name = []
    year8points = []
    year9name = []
    year9points = []
    year10name = []
    year10points = []
    year11name = []
    year11points = []
    year12name = []
    year12points = []

    for i in allStudentsTotal:
        if (allStudentsTotal[i])[0] == 7:
            year7name.append((i))
            year7points.append(((allStudentsTotal[i])[1]))
        if (allStudentsTotal[i])[0] == 8:
            year8name.append((i))
            year8points.append(((allStudentsTotal[i])[1]))
        if (allStudentsTotal[i])[0] == 9:
            year9name.append((i))
            year9points.append(((allStudentsTotal[i])[1]))
        if (allStudentsTotal[i])[0] == 10:
            year10name.append((i))
            year10points.append(((allStudentsTotal[i])[1]))
        if (allStudentsTotal[i])[0] == 11:
            year11name.append((i))
            year11points.append(((allStudentsTotal[i])[1]))
        if (allStudentsTotal[i])[0] == 12:
            year12name.append((i))
            year12points.append(((allStudentsTotal[i])[1]))

    for i in allStudentsTotal:
        p_vbar = figure(x_range=allStudentsTotal[i], plot_height=600, plot_width=(600), title="Standings",
                    toolbar_location=None, tools="hover")
                    #tooltips="@year7names: @year7points")  # specifies the formatting of the data
        #for j in range(len(allStudentsTotal)):
        p_vbar.vbar(allStudentsTotal[i], top=(allStudentsTotal[i][1]), color="red", width=0.2)  # names are the x points, top of the bar graph creates the column from 0 on the y-axis, width specifies gap between the columns
    p_vbar.xgrid.grid_line_color = None
    p_vbar.y_range.start = 0  # ensures that the y-axis begins at 0
    script, div = components(p_vbar)

    return render_template('comparitive_bar.html', script=script, div=div)

if __name__ == '__main__':
    app.run(debug=True)
