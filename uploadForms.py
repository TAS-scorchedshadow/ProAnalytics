from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.fields.html5 import DateField, TimeField, EmailField
from wtforms.validators import DataRequired


# collect all shot information needed
class uploadForm(FlaskForm):
    shooterName = SubmitField('Shooter name: ')
    coachName = SubmitField('Coach name: ')
    range = SubmitField('Range: ')
    dist = SubmitField('Distance: ')
    shots = SubmitField('')
    # Not sure if the following is needed
    weather = SubmitField('Weather: ')
    wind = SubmitField('Wind: ')
