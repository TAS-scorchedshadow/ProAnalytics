from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort, url_for
from flask_bootstrap import Bootstrap
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d
from shotProcessing import validateShots, getScore
from uploadForms import uploadForm
from werkzeug.utils import secure_filename
from drawtarget import create_target
from models import User
import os

app = Flask(__name__)
app.secret_key = "super secret"
bootstrap = Bootstrap(app)
array_shots = [[150, 0], [300, 100], [499, 700]]
# code from https://stackoverflow.com/questions/10637352/flask-ioerror-when-saving-uploaded-files/20257725#20257725
# that creates absolute path with relative path
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/upload')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
@app.route('/home')
def home():
    jsonID = 1551500850141  # ID of json file
    filePath = os.path.join(APP_ROOT, "testJson/string-" + str(jsonID) + ".txt")
    s = validateShots(filePath)
    for i in range(len(s['validShots'])):
        score = getScore(s['validShots'][i])
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/report')
def report():
    return render_template('signUpForm.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # create form
    form = uploadForm()

    # on submission
    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            filename = secure_filename(file.filename)
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filePath) #Add file to upload folder
            print(filename,"was uploaded")

            #TODO save data to database
            #Test to see if upload works
            s = validateShots(filePath)['validShots'] # Get all valid Shots
            for i in range(len(s)):
                score = getScore(s[i])
                print(score)

            #Delete file
            os.remove(filePath)
            print(filename, "was removed")
    return render_template('upload.html', form=form)


@app.route('/user/signup',methods=['POST'])
def signup():
    return User().signup()


@app.route('/target')
def testDrawTarget():
    script, div = drawTarget()
    return render_template('target.html', script=script, div=div)

def drawTarget(filePath="testJson/string-1592616479803.txt"):
    p = create_target("300m")   # Creates a target with the 300m face
    # todo: Change this to pull from database info instead of directly from json
    # Required: x/y value of shot, shot number
    # Required: shot grouping radius, shot grouping center point
    # Required: target size


    # add a shot (test)
    s = validateShots(filePath)['validShots']
    for i in range(len(s)):
        plotShot(p, s[i]['x'], s[i]['y'], i + 1)
    # Uses stats_circle_center and stats_circle_radius in order to perform
    # Currently hardcoded to json 1592616479803
    group_center = (12.66, -32.5)
    group_radius = 228.8
    p.circle([group_center[0]], [group_center[1]], radius=group_radius, fill_alpha=0, line_color="yellow", line_width=4)
    script, div = components(p)
    return script, div


# Add a circle with the number of the shot in the middle
# x and y are the coordinates
# p is the figure object
# num is the number of the shot
def plotShot(p, x, y, num):
    p.circle([x], [y], size=30, color="black", line_color="white", line_width=2)
    p.text([x], [y], text=[str(num)], text_baseline="middle", text_align="center", color="white")

# Using the


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
