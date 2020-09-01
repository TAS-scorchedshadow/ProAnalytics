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

import sqlite3

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
    # create targets based on user
    target_list = []
    username = request.args.get('username')
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    # search through shoots database to get a tuple of shoots
    c.execute('SELECT * FROM shoots WHERE username=? ORDER BY date desc;', (username,))
    shoots = c.fetchall()
    # search through each shoot to collect a list of shots
    for shoot in shoots:
        c.execute('SELECT * FROM shots WHERE shootID=?', (shoot[0], ))
        range = shoot[3]
        shots_tuple = c.fetchall()
        shots = {}
        for row in shots_tuple:
            shots[row[-1]] = [row[5], row[3], row[6]]
            # row[-1] is shotNum
            # row[5] is x
            # row[3] is y
            # row[6] is score
        # create graph and put the data into target_list (along with shotNum
        script, div = graphProcessing.drawTarget(shots, range, 228.8, (12.66, -32.5))
        target_list.append([('a' + str(shoot[0])), script, div])
    return render_template('shotList.html', target_list=target_list)


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


if __name__ == '__main__':
    app.run(debug=True)
