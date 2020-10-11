from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField, RadioField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, InputRequired
from dataAccess import shoot_range, get_all_shooter_names, get_all_usernames, get_all_dates

# form for uploading files
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
    rifleRange = SelectField("Rifle Range:", choices=[('Malabar', 'Malabar')])
    distance = SelectField("Distance:", choices=[('300m', '300m'), ('500m', '500m'), ('600m', '600m'),
                                                 ('700m', '700m'), ('800m', '800m')])
    weather = SelectField("Weather:", choices=[('Sunny', 'Sunny'), ('Cloudy', 'Cloudy'), ('Windy', 'Windy'),
                                               ('Rain', 'Rain'), ('Storm', 'Storm')])
    submit = SubmitField("Submit")
    identifier = HiddenField("Upload/Verify", default="upload")
    submit = SubmitField("Submit")
    invalidShootInfo = HiddenField("Data")
    success = HiddenField("Success")
    total = HiddenField("Total")

# form for registering
class signUpForm(FlaskForm):
    fName = StringField("Enter First Name:",validators=[InputRequired()])
    sName = StringField("Enter Last Name:",validators=[InputRequired()])
    email = EmailField("Email:",validators=[InputRequired()])
    school = SelectField("Select a school", choices=[('sbhs','Sydney Boys High School')])
    year = SelectField("Select a school", choices=['None','7','8','9','10','11','12'])
    password = PasswordField("Password:")
    confirmPassword = PasswordField("Password:")

    submit = SubmitField("Sign Up")

# form for logging in
class signIn(FlaskForm):
    username = StringField("Username or password")
    password = PasswordField("Password:")

    submit = SubmitField("Sign In")

# form for report page
class reportForm(FlaskForm):
    date = SelectField('Date',)
    submit = SubmitField("Select")

class comparativeSelect(FlaskForm):
    graphType = RadioField('Graph', choices=['Line', 'Bar'])
    shooter_username_one = SelectField('Username', choices=get_all_usernames())
    shooter_username_two = SelectField('Username', choices=get_all_usernames())

    shooting_range_one = SelectField('Range')
    shooting_range_two = SelectField('Range')

    dates_one = SelectField('Dates')
    dates_two = SelectField('Dates')

    submit = SubmitField('ENTER')

class comparativeSpecify(FlaskForm):
    shooter_username_one = SelectField('Username', choices=get_all_shooter_names())