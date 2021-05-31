from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length, Optional
from wtforms.widgets import TextArea


class NameForm(FlaskForm):
    name = StringField(
        'Add user name:', validators=[Required(), Length(1, 16)])
    description = StringField(
        'Short description', widget=TextArea(),
        validators=[Optional(), Length(max=200)])
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField(
        'Username : ', validators=[Required(), Length(10, 12)])
    password = StringField(
        'Password : ', validators=[Optional(), Length(6, 16)])
    submit = SubmitField('Submit')
