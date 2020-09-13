from urllib.parse import urlparse, urljoin

import flask
from flask import Flask, render_template, request, send_file, send_from_directory, safe_join, abort, url_for, session, \
    flash
from flask_bootstrap import Bootstrap
# from bokeh.plotting import figure
# from bokeh.embed import components
# from bokeh.models import Range1d
from flask_login import logout_user, login_user, login_required, current_user
from flask_wtf import CSRFProtect
import flask_login

from shotProcessing import validateShots, getScore
from uploadForms import uploadForm, signUpForm, signIn, selectDate
from security import registerUser, validateLogin, User
from dataAccess import emailExists, addShoot

from werkzeug.utils import secure_filename, redirect
from drawtarget import create_target
from datetime import datetime
import time
import os
import graphProcessing

import sqlite3
from flask import g, session

app = Flask(__name__)
app.secret_key = "super secret"
csrf = CSRFProtect(app) #Initalising secret key
#Intialising flask-login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

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


@app.route('/comparativeHomePage')
def comparativeHomePage():
    shots = {1: [10, 10, 5]}
    targetSize= "300m"
    groupRadius = 228.8
    group_center = (12.66, -32.5)
    first_script, first_div = graphProcessing.drawTarget(shots,targetSize,groupRadius,group_center)
    second_script, second_div = graphProcessing.drawTarget(shots,targetSize,groupRadius,group_center)
    return render_template('comparativeHomePage.html', first_script=first_script, first_div=first_div, second_script=second_script, second_div=second_div)


@app.route('/about')
@login_required
def about():
    return render_template('about.html',variable="variable", )


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/report', methods=['GET', 'POST'])
def report():
    form = selectDate()
    target_list = []
    shot_table = {}
    username = request.args.get('username')
    if username is None:
        # TODO create a custom error page
        return render_template('404.html')
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()
    if request.method == 'POST':
        date = request.form['date']
        # change date so its in dd/mm/yyyy format
        date = '-'.join(reversed(date.split('-')))
        date1 = time.mktime(datetime.strptime(date, "%d-%m-%Y").timetuple()) * 1000
    else:
        # collect latest date (as default)
        c.execute('SELECT time FROM shoots WHERE username=? ORDER BY time desc;', (username,))
        date1 = c.fetchone()[0]
        # convert date1 to the start of the day at 12:00:00 a.m.
        date1 = datetime.fromtimestamp(int(date1) / 1000).strftime('%d-%m-%y')
        date1 = time.mktime(datetime.strptime(date1, "%d-%m-%y").timetuple()) * 1000
    date2 = date1 + 86399000
    print(date1, date2)
    # search through shoots database to get a tuple of shoots
    c.execute('SELECT * FROM shoots WHERE username=? AND time BETWEEN ? AND ? ORDER BY time desc;', (username, date1, date2))
    shoots = c.fetchall()
    # search through each shoot to collect a list of shots
    for shoot in shoots:
        shot_table[str(shoot[0])] = []
        c.execute('SELECT * FROM shots WHERE shootID=?', (shoot[0], ))
        range = shoot[3]
        shots_tuple = c.fetchall()
        shots = {}
        for row in shots_tuple:
            shots[row[-1]] = [row[5], row[3], row[6]]
            # create list of shots
            shot_table[str(shoot[0])].append((row[6], row[9]))
            # row[9] is shotNum
            # row[5] is x
            # row[3] is y
            # row[6] is score
        # create graph and put the data into target_list (along with shotNum
        script, div = graphProcessing.drawTarget(shots, range, (shoot[6]/2), (shoot[7], shoot[8]))
        date = datetime.fromtimestamp(int(shoot[1])/1000).strftime('%d-%m-%y')
        target_list.append([(str(shoot[0])), script, div, date, shoot[9], round(shoot[6]/2, 2)])

    return render_template('shotList.html', target_list=target_list, shot_table=shot_table, form=form)


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
            file.save(filePath)                 # Add file to upload folder
            print(filename, "was uploaded")     # Debug
            shoot = validateShots(filePath)     # Fixes up file to obtain relevant data and valid shots

            # todo: Handle missing values. 'username' may be a missing value.
            # Adds missing values temporarily
            shoot['rifleRange'] = "Malabar"
            shoot['distance'] = "300m"
            addShoot(shoot)                     # Import the shoot to the database

            os.remove(filePath)                 # Delete file
            print(filename, "was removed")      # Debug
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


def is_safe_url(target):
    # See https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work.
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@app.route('/user/signin', methods=['GET', 'POST'])
def signin():
    # create form
    form = signIn()
    # on submission
    if request.method == 'POST':
        if form.validate_on_submit():
            # Authenticate User. Also initialises sessions.
            usernameError, passwordError = validateLogin(form)
            if usernameError or passwordError:
                return render_template('signInForm.html', form=form, usernameError=True, passwordError=True)
            else:
                user = User(form.username.data)
                login_user(user)
                next = flask.request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                # See https://stackoverflow.com/questions/60532973/how-do-i-get-a-is-safe-url-function-to-use-with-flask-and-how-does-it-work for an example.
                if not is_safe_url(next):
                    return flask.abort(400)

                return flask.redirect(next or flask.url_for('report',username=current_user.username))
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


@login_manager.user_loader
def load_user(username):
    # Loads a user based off a given username
    return User(username)

@login_manager.unauthorized_handler
def unauthorized():
    return render_template('accessDenied.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
