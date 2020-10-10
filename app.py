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
from uploadForms import uploadForm, signUpForm, signIn, reportForm, comparativeSelect
from security import registerUser, validateLogin, User
from dataAccess import emailExists, addShoot, get_table_stats, get_all_dates,\
    get_shoots_dict, get_line_graph_ranges, get_all_shooter_names,\
    get_graph_details, get_shot_details, get_dates_for_all, get_ranges_for_all, usernameExists,\
    get_shooter_and_year

from werkzeug.utils import secure_filename, redirect
from drawtarget import create_target
from datetime import datetime
import time
import os
import graphProcessing
import numpy
import json

import sqlite3
from flask import g, session

app = Flask(__name__)
app.secret_key = "super secret"
csrf = CSRFProtect(app)  # Initalising secret key
# Intialising flask-login
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
def landingPage():
    if current_user.is_authenticated:
        if current_user.admin == 1:
            return render_template('adminHome.html')
        else:
            return render_template('shooterHome.html')
    return render_template('landingPage.html')


@app.route('/adminHome')
@login_required
def adminHome():
    return render_template('adminHome.html')


@app.route('/studentList')
@login_required
def studentList():
    all_shooters = get_shooter_and_year()
    return render_template('studentList.html', all_shooters=all_shooters)



@app.route('/shooterHome')
@login_required
def shooterHome():
    return render_template('shooterHome.html')


@app.route('/comparativeHomePage',  methods=['GET', 'POST'])
def comparativeHomePage():

    # calls the class from the uploadForms.py for
    all_forms = comparativeSelect()

    # collect the data used for the select fields and convert into jsons which javascript can read from
    #all_dates_dict leaves a copy in dictionary format for ease in further code
    all_dates = get_dates_for_all()
    all_dates_dict = all_dates
    all_dates = json.dumps(all_dates)
    all_ranges = get_ranges_for_all()
    all_ranges = json.dumps(all_ranges)

    # f the radio button is submit
    if request.method == "POST":

        # passes the values selected from the SelectFields to the get_graph_details
        # off the database of the (x,y) point of centre, the grouping size and total score in a shoot session e.g.
        # shoot_data = [(243.1, 5.6, 4.1, '95')]
        first_shoot_data = get_graph_details(all_forms.shooter_username_one.data, all_forms.shooting_range_one.data, all_forms.dates_one.data)
        second_shoot_data = get_graph_details(all_forms.shooter_username_two.data, all_forms.shooting_range_two.data, all_forms.dates_two.data)
        first_shots_data =  get_shot_details(first_shoot_data[0][4])
        second_shots_data = get_shot_details(second_shoot_data[0][4])
        first_median = first_shoot_data[0][5]
        first_mean = first_shoot_data[0][6]
        first_std = first_shoot_data[0][7]
        first_weather = first_shoot_data[0][8]
        second_median = second_shoot_data[0][5]
        second_mean = second_shoot_data[0][6]
        second_std = second_shoot_data[0][7]
        second_weather = second_shoot_data[0][8]

        # filters through each piece of data from the list of tuples and assigns them to the
        # variables necessary. e.g.
        # shot = {1: [5.6, 4.1, 95]
        # distance = "300m"
        # group_size = 243.3
        # group_center = (5.6, 4.1)
        first_shots = {}
        for i in range(len(first_shots_data)):
            key_first = first_shots_data[i][0]
            values_first = [first_shots_data[i][1], first_shots_data[i][2], first_shots_data[i][3]]
            first_shots[key_first] = values_first
        first_distance = all_forms.shooting_range_one.data
        first_group_size = first_shoot_data[0][0]
        first_group_center = (first_shoot_data[0][1], first_shoot_data[0][2])
        second_shots = {}
        for j in range(len(second_shots_data)):
            key_second = second_shots_data[j][0]
            values_second = [second_shots_data[j][1], second_shots_data[j][2], second_shots_data[j][3]]
            second_shots[key_second] = values_second
        second_distance = all_forms.shooting_range_two.data
        second_group_size = second_shoot_data[0][0]
        second_group_center = (second_shoot_data[0][1], second_shoot_data[0][2])

        # passes the shot values to render the bokeh targets
        first_script, first_div = graphProcessing.drawTarget(first_shots, first_distance, first_group_size, first_group_center)
        second_script, second_div = graphProcessing.drawTarget(second_shots, second_distance, second_group_size, second_group_center)

        # If the radio selected button is bar
        if (all_forms.graphType.data) == "Bar":
            bar_script, bar_div = graphProcessing.compareBar(all_forms.shooter_username_one.data, all_forms.shooter_username_two.data, first_shoot_data[0][3], second_shoot_data[0][3])
            return render_template('comparativeHomePage.html', first_script=first_script, first_div=first_div, second_script=second_script, second_div=second_div, graph_script = bar_script,
                                   graph_div=bar_div, all_forms=all_forms, all_dates=all_dates, all_ranges=all_ranges,
                                   first_median = first_median, first_mean = first_mean, first_std = first_std, first_weather = first_weather,
                                   second_median = second_median, second_mean = second_mean, second_std= second_std, second_weather = second_weather)

        # If the radio button selected is line
        if (all_forms.graphType.data) == "Line":
            # sets up for the line graph
            # gets shot data from a particular day forward to display a line graph
            # e.g. values = {'Rishi': { 'yValue': [50, 46, 49] , 'xValue': ['10/08/2020', '11/08/2020', '12/08/2020']}
            # internal_dict have the key as yValue and xValue, scores and times respectively
            values = {}
            xFill_one = []
            yFill_one = []
            for t in range(len(all_dates_dict[all_forms.shooter_username_one.data][all_forms.shooting_range_one.data])):
                internal_dict_one = {}
                if (
                all_dates_dict[all_forms.shooter_username_one.data][all_forms.shooting_range_one.data][t][1]) >= int(
                        all_forms.dates_one.data):
                    xFill_one.append(
                        all_dates_dict[all_forms.shooter_username_one.data][all_forms.shooting_range_one.data][t][0])
                    yFill_one.append(
                        get_graph_details(all_forms.shooter_username_one.data, all_forms.shooting_range_one.data,
                                          all_dates_dict[all_forms.shooter_username_one.data][
                                              all_forms.shooting_range_one.data][t][1])[0][3])
                internal_dict_one["yValue"] = yFill_one
                internal_dict_one["xValue"] = xFill_one
                values[all_forms.shooter_username_one.data] = internal_dict_one
            xFill_two = []
            yFill_two = []
            for t in range(len(all_dates_dict[all_forms.shooter_username_two.data][all_forms.shooting_range_two.data])):
                internal_dict_two = {}
                if (
                all_dates_dict[all_forms.shooter_username_two.data][all_forms.shooting_range_two.data][t][1]) >= int(
                        all_forms.dates_two.data):
                    xFill_two.append(
                        all_dates_dict[all_forms.shooter_username_two.data][all_forms.shooting_range_two.data][t][0])
                    yFill_two.append(
                        get_graph_details(all_forms.shooter_username_two.data, all_forms.shooting_range_two.data,
                                          all_dates_dict[all_forms.shooter_username_two.data][
                                              all_forms.shooting_range_two.data][t][1])[0][3])
                internal_dict_two["yValue"] = yFill_two
                internal_dict_two["xValue"] = xFill_two
                values[all_forms.shooter_username_two.data + "0000000000"] = internal_dict_two
            xLabel = "Dates"
            yLabel = "Times"
            title = "Comparison Line"
            line_script, line_div = graphProcessing.compareLine(values, xLabel, yLabel, title)
            return render_template('comparativeHomePage.html', first_script=first_script, first_div=first_div, second_script=second_script, second_div=second_div, graph_script = line_script,
                                   graph_div=line_div, all_forms=all_forms, all_dates=all_dates, all_ranges=all_ranges,
                                   first_median = first_median, first_mean = first_mean, first_std = first_std, first_weather = first_weather,
                                   second_median = second_median, second_mean = second_mean, second_std = second_std, second_weather = second_weather)

        return render_template('comparativeHomePage.html', first_script=first_script, first_div=first_div, second_script=second_script, second_div=second_div, all_forms=all_forms, all_dates=all_dates, all_ranges=all_ranges,
                               first_median=first_median, first_mean=first_mean, first_std=first_std, first_weather=first_weather,
                               second_median=second_median, second_mean=second_mean, second_std=second_std, second_weather=second_weather)
    return render_template('comparativeHomePage.html', all_forms=all_forms, all_dates=all_dates, all_ranges=all_ranges)  # form_usernameOne=form_usernameOne, form_usernameTwo=form_usernameTwo, form_rangeOne=form_rangeOne, form_rangeTwo=form_rangeTwo, form_graph=form_graph)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/report', methods=['GET', 'POST'])
@login_required
def report():
    form = reportForm()
    username = request.args.get('username')
    getDefault = True
    if username is None:
        # TODO create a custom error page
        return render_template('404.html')

    # connect to database
    conn = sqlite3.connect('PARS.db')
    c = conn.cursor()

    # collect the shooter's name
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    get_name = c.fetchone()

    # if the shooter isn't in the database redirect the user to noSheet page
    if not get_name:
        return render_template('noSheet.html', current_user=current_user)
    shooter_name = get_name[2][0].upper() + get_name[2][1:] + ' ' + get_name[3][0].upper() + get_name[3][1:]

    # on submit, get the data from the select field
    if request.method == 'POST':
        date = request.form['date']
        if date:
            dayStart = time.mktime(datetime.strptime(date, "%d-%m-%y").timetuple()) * 1000
            getDefault = False

    # collect latest date (as default)
    if getDefault:
        c.execute('SELECT time FROM shoots WHERE username=? ORDER BY time desc;', (username,))
        shootTimes = c.fetchall()
        if not shootTimes:
            return render_template('noSheet.html', current_user=current_user)
        print(shootTimes)
        # convert dayStart to the start of the day at 12:00:00 a.m. (in ts format)
        dayStart = shootTimes[0][0]
        dayStart = datetime.fromtimestamp(int(dayStart) / 1000).strftime('%d-%m-%y')
        dayStart = time.mktime(datetime.strptime(dayStart, "%d-%m-%y").timetuple()) * 1000

    # store all dates into a list (for the user to select from)
    form.date.choices = get_all_dates(username)

    # dayEnd is the same day as day 1 but at 11:59:59 p.m.
    dayEnd = dayStart + 86399000

    target_list, shot_table = get_shoots_dict(username, dayStart, dayEnd)
    # collect general stats

    # TODO have the stats only apply to the current season
    # # find the previous year
    # prevYear = dayStart - 31622400000

    # collect and calculate stats for the table
    stat_dict = get_table_stats(username)
    # create line graph
    line_script, line_div = get_line_graph_ranges(username)

    return render_template('shotList.html', target_list=target_list, shot_table=shot_table,
                           form=form, stat_dict=stat_dict, line_script=line_script,
                           line_div=line_div, shooter_name=shooter_name)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    # todo: neaten this up
    # todo: make verify page clearer (i.e. make it so that user knows that username field is for usernames)
    if current_user.admin == 1:
        # Create Form
        form = uploadForm()
        count = {'success': 0, 'incomplete': 0, 'failure': 0, 'total': 0}
        if form.identifier.data == "upload":
            invalidShoots = []
            # on submission
            if request.method == 'POST':
                files = request.files.getlist('file')
                for file in files:
                    count['total'] += 1
                    filename = secure_filename(file.filename)
                    filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filePath)  # Add file to upload folder
                    print(filename, "was uploaded")  # Debug
                    try:
                        shoot = validateShots(filePath)  # Fixes up file to obtain relevant data and valid shots
                        shoot['rifleRange'] = form.rifleRange.data
                        shoot['distance'] = form.distance.data
                        shoot['weather'] = form.weather.data
                        idFound = usernameExists(shoot['username'])
                        if idFound:
                            addShoot(shoot)  # Import the shoot to the database
                            count['success'] += 1
                        else:
                            shoot['id'] = count['incomplete']
                            count['incomplete'] += 1
                            invalidShoots.append(shoot)
                    except:
                        count['failure'] += 1
                        print(str(filename) + " had an error in uploading")
                    os.remove(filePath)  # Delete file
                    print(filename, "was removed")  # Debug
        else:
            shoots = json.loads(request.form["invalidShootInfo"])
            count['success'] = int(request.form["success"])
            count['total'] = int(request.form["total"])
            invalidShoots = []
            for key in request.form:
                if "username." in key:
                    id = int(key[9:])
                    username = request.form[key]
                    shoots[id]['username'] = username
                    idFound = usernameExists(username)
                    if idFound:
                        addShoot(shoots[id])
                        count['success'] += 1
                    else:
                        print("Username not found")  # Debug
                        shoots[id]['id'] = count['incomplete']
                        count['incomplete'] += 1
                        invalidShoots.append(shoots[id])

        if count['incomplete'] > 0:
            invalidShootsJson = json.dumps(invalidShoots)
            return render_template('uploadVerify.html', form=form, invalidShoots=invalidShoots,
                                   invalidShootsJson=invalidShootsJson,
                                   success=count['success'],
                                   total=count['total'], failure=count['failure'])
        else:
            print(invalidShoots)
            return render_template('upload.html', form=form, success=count['success'],
                                   total=count['total'], failure=count['failure'])
    else:
        return render_template('accessDenied.html')


@app.route('/user/signup', methods=['GET', 'POST'])
def signup():
    # create form
    form = signUpForm()
    # on submission
    if request.method == 'POST':
        if form.validate_on_submit():
            if emailExists(form.email.data):
                return render_template('signUpForm.html', form=form, emailError=True)
            else:
                registerUser(form)
                return render_template('adminHome.html')
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
                if current_user.admin == 1:
                    return render_template('adminHome.html')
                return flask.redirect(next or flask.url_for('report', username=current_user.username))
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
    return redirect(url_for('landingPage'))


if __name__ == '__main__':
    app.run(debug=True)
