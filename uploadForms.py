from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import DataRequired, InputRequired


# form for uploading files
class uploadForm(FlaskForm):
    #todo: This doesn't work as expected yet
    file = MultipleFileField(u'Submit File', validators=[
        FileRequired(), FileAllowed(["html", "txt"], message="Must be a html file")])
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

# form for selecting date
class selectDate(FlaskForm):
    date = StringField('Date', validators=[InputRequired()])
    submit = SubmitField("Select")

class graphSelect(FlaskForm):
    graphType = RadioField('Label', choices=[('value','Line'),('value_two','Bar')])
    submit = SubmitField('ENTER')