from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort, url_for, session
from flask_bootstrap import Bootstrap
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import Range1d
from flask_wtf import CSRFProtect

from shotProcessing import validateShots, getScore
from uploadForms import uploadForm, signUpForm, signIn
from security import registerUser, validateLogin
from dataAccess import emailExists

from werkzeug.utils import secure_filename
from drawtarget import create_target
import os
import graphProcessing


app = Flask(__name__)
app.secret_key = "super secret"
csrf = CSRFProtect(app)

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
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/report')
def report():
    script, div = graphProcessing.drawTarget()
    script2, div2 = graphProcessing.drawTarget()
    return render_template('OPGG.html', script=script,div=div,script2=script2,div2=div2)


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


@app.route('/user/signup',methods=['GET', 'POST'])
def signup():
    # create form
    form = signUpForm()
    # on submission
    if request.method == 'POST':
        if form.validate_on_submit():
            if emailExists(form.email.data):
                return render_template('signUpForm.html', form=form,emailError=True)
            else:
                registerUser(form)
                return render_template('home.html')
    return render_template('signUpForm.html', form=form, emailError=False)



@app.route('/user/signin', methods=['GET', 'POST'])
def signin():
    # create form
    form = signIn()
    # on submission
    if request.method == 'POST':
        if form.validate_on_submit():
            usernameError, passwordError = validateLogin(form)
            if usernameError or passwordError:
                return render_template('signInForm.html', form=form, usernameError=True, passwordError=True)
            else:
                return render_template('home.html', form=form)
    return render_template('signInForm.html', form=form)



@app.route('/target')
def testDrawTarget():
    script, div = graphProcessing.drawTarget()
    return render_template('target.html', script=script, div=div)


@app.route('/comparativeBar')
def comparitiveBar():
    script, div = graphProcessing.compareBar()
    return render_template('comparativeBar.html', script=script, div=div)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route('/comparitiveBar')
def comparitiveBar():

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

    return render_template('comparitive_bar.html', script=script, div=div)

if __name__ == '__main__':
    app.run(debug=True)
