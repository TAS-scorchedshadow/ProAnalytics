from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, MultipleFileField, FileField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from wtforms.validators import DataRequired


# form for uploading files
class uploadForm(FlaskForm):
    file = MultipleFileField(u'Submit File')
    submit = SubmitField("Submit: ")