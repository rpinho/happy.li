from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, SelectField
from wtforms.validators import Required

class LoginForm(Form):
    job1 = TextField('job1', validators = [Required()])
    job2 = TextField('job2', validators = [Required()])
