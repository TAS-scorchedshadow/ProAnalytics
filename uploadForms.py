from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField, RadioField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, InputRequired
from dataAccess import shooter_username, shoot_range

# form for uploading files
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
    rifleRange = SelectField("Rifle Range:", choices=[('Malabar', 'Malabar')])
    distance = SelectField("Distance:", choices=[('300m', '300m'), ('500m', '500m'), ('600m', '600m'),
                                                 ('700m', '700m'), ('800m', '800m')])
    weather = SelectField("Weather:", choices=[('Sunny', 'Sunny'), ('Cloudy', 'Cloudy'), ('Windy', 'Windy'),
                                               ('Rain', 'Rain'), ('Storm', 'Storm')])
    submit = SubmitField("Submit: ")

# form for registering
class signUpForm(FlaskForm):
    fName = StringField("Enter First Name:")
    sName = StringField("Enter Last Name:")
    email = EmailField("Email:")
    school = SelectField("Select a school", choices=[('sbhs','Sydney Boys High School')])
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

class graphSelect(FlaskForm):
    graphType = RadioField('Graph', choices=[('Line','Line'),('Bar','Bar')])
    submit = SubmitField('ENTER')

class nameSelectTargetOne(FlaskForm):
    shooter_username = SelectField('Username', choices=shooter_username())

class nameSelectTargetTwo(FlaskForm):
    shooter_username = SelectField('Username', choices=shooter_username())

class rangeSelectTargetOne(FlaskForm):
    shooting_range = SelectField('Range', choices=shoot_range())

class rangeSelectTargetTwo(FlaskForm):
    shooting_range = SelectField('Range', choices=shoot_range())