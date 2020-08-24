from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, IntegerField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from wtforms.validators import DataRequired


# form for uploading files
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
    submit = SubmitField("Submit: ")


class signUpForm(FlaskForm):
    name = StringField("Please enter a name:")
    email = EmailField("Email:")
    studentID = IntegerField("Student ID")
    username = StringField("Associated Username:")
    password = StringField("Password:")
    submit = SubmitField("Submit:")