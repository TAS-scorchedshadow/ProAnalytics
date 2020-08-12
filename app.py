from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort
from flask_bootstrap import Bootstrap
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d
from shotProcessing import validateShots, getScore
from uploadForms import uploadForm
from werkzeug.utils import secure_filename
import os
import graphProcessing

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
        print(str(score))
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
    p = figure(plot_width=1500, plot_height=1500, tools="", sizing_mode="scale_width")
    p.toolbar.logo = None

    # draw the circles of the target from the largest to the smallest
    p.circle([0], [0], radius=600, color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=420, color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=280, color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=140, color="black", line_color="white", line_width=4)
    p.circle([0], [0], radius=70, color="black", line_color="white", line_width=4)

    # Resize viewpoint so origin is at the middle and the entire graph is onscreen
    axisLimit = 600  # Height of Graph
    p.y_range = Range1d(start=-1 * axisLimit, end=axisLimit)

    axisLimit = 600  # Length of Graph
    p.x_range = Range1d(start=-1 * axisLimit, end=axisLimit)

    # make the rest of the grid invisible so only the target is seen
    p.axis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False

    # add a shot (test)
    jsonID = 1592616479803  # ID of json file
    filePath = "testJson/string-" + str(jsonID) + ".txt"
    s = validateShots(filePath)['validShots']
    for i in range(len(s)):
        plotShot(p, s[i]['x'], s[i]['y'], i + 1)
    script, div = components(p)

    # testing compare line graph
    scriptLine, divLine = graphProcessing.compareLine([[50, 46, 48, 49, 50, 50], [50, 44, 50, 49, 48, 49]],
                                              ['10/08/2020', '11/08/2020', '12/08/2020', '13/08/2020', '14/08/2020',
                                               '15/08/2020'], ['Andrew', 'Ryan'])

    return render_template('target.html', script=script, div=div, scriptLine=scriptLine, divLine=divLine)


# Add a circle with the number of the shot in the middle
# x and y are the coordinates
# p is the figure object
# num is the number of the shot
def plotShot(p, x, y, num):
    p.circle([x], [y], size=30, color="black", line_color="white", line_width=2)
    p.text([x], [y], text=[str(num)], text_baseline="middle", text_align="center", color="white")


if __name__ == '__main__':
    app.run(debug=True)
