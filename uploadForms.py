from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from wtforms.validators import DataRequired


# form for uploading files
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
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

    submit = SubmitField("Sign Up")

# form for selecting date
class selectDate(FlaskForm):
    date = DateField("Date: ")
    submit = SubmitField("Select")