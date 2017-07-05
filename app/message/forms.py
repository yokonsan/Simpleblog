from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class LetterForm(FlaskForm):
    body = PageDownField('评论', validators=[DataRequired()])