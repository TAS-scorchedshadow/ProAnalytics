from flask_wtf import FlaskForm, Form
from wtforms import RadioField, SubmitField
from wtforms.validators import data_required
from wtforms.fields import StringField
from wtforms.widgets import TextArea

class graphSelect(FlaskForm):
    graphType = RadioField('Label', choices=[('value','Line'),('value_two','Bar')])
    submit = SubmitField('ENTER')