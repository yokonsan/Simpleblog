from flask_wtf import FlaskForm
from wtforms.validators import Length
from wtforms import TextAreaField


class NoticeForm(FlaskForm):
    body = TextAreaField('notice', validators=[Length(0, 25)])
