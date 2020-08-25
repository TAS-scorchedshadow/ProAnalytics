from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField, SelectField, PasswordField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from wtforms.validators import DataRequired


# form for uploading files
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
    submit = SubmitField("Submit: ")


class signUpForm(FlaskForm):
    fName = StringField("Enter First Name:")
    sName = StringField("Enter Last Name:")
    email = EmailField("Email:")
    school = SelectField("Select a school", choices=[('sb','SBHS')])
    password = PasswordField("Password:")
    confirmPassword = PasswordField("Password:")

    submit = SubmitField("Sign Up")