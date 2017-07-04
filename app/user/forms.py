from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_pagedown.fields import PageDownField


# 编辑用户资料表单
class ProfileForm(FlaskForm):
    nickname = StringField('nickname', validators=[Length(0, 7)])
    about_me = TextAreaField('about me', validators=[Length(0, 140)])

# 博客文章表单
class PostForm(FlaskForm):
    body = PageDownField('写文章或者提问?', validators=[DataRequired()])
    title = StringField('标题', validators=[Length(1, 20)])
    save_draft = SubmitField('保存草稿')
    submit = SubmitField('发布')

class EditpostForm(FlaskForm):
    title = StringField('标题', validators=[Length(1, 20)])
    body = PageDownField('编辑文章', validators=[DataRequired()])
    update = SubmitField('更新')
    submit = SubmitField('发布')
    save_draft = SubmitField('保存')

# 评论表单
class CommentForm(FlaskForm):
    body = PageDownField('评论', validators=[DataRequired()])

# 回复表单
class ReplyForm(FlaskForm):
    body = PageDownField('回复', validators=[DataRequired()])

# 搜索表单
class SearchForm(FlaskForm):
    search = StringField('搜索', validators=[DataRequired()])
