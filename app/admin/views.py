from .. import db
from flask_login import login_required, current_user
from ..decorators import admin_required
from flask import render_template, redirect, url_for, request, current_app
from ..models import Comment, Post, Admin
from . import admin
from flask import g
from ..user.forms import SearchForm
from datetime import datetime
from .forms import NoticeForm


# 用户最后一次访问时间,全文搜索
@admin.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.add(current_user)
        db.session.commit()
    g.search_form = SearchForm()


# 管理员页面
@admin.route('/')
@admin_required
@login_required
def index():

    return render_template('admin/admin.html',
                           title='管理')

@admin.route('/admincomment/')
@admin_required
@login_required
def admin_comment():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('admin/admin_comment.html',
                           comments=comments,
                           pagination=pagination,
                           page=page,
                           nums=len(comments),
                           title='管理评论')
# 恢复评论
@admin.route('/adminrecover/<int:id>')
@login_required
def admin_recover(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('admin.admin_comment'))
# 删除评论
@admin.route('/admindelate/<int:id>')
@login_required
def admin_delate(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('admin.admin_comment'))

@admin.route('/adminpost/')
@admin_required
@login_required
def admin_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('admin/admin_post.html',
                           posts=posts,
                           pagination=pagination,
                           page=page,
                           nums = len(posts),
                           title='管理文章')

# 恢复文章
@admin.route('/recoverpost/<int:id>')
@login_required
def recover_post(id):
    post = Post.query.get_or_404(id)
    post.disabled = False
    db.session.add(post)
    return redirect(url_for('admin.admin_post'))
# 删除文章
@admin.route('/delatepost/<int:id>')
@login_required
def delate_post(id):
    post = Post.query.get_or_404(id)
    post.disabled = True
    db.session.add(post)
    return redirect(url_for('admin.admin_post'))

# 添加公告
@admin.route('/notice', methods=['GET','POST'])
@login_required
@admin_required
def add_notice():
    notice = Admin.query.order_by(Admin.timestamp.desc()).first()
    if notice:
        db.session.delete(notice)
    form = NoticeForm()
    if form.validate_on_submit():
        admin = Admin(
            notice = form.body.data
        )
        db.session.add(admin)
        return redirect(url_for('admin.index'))
    return render_template('admin/admin_notice.html',
                           title='网站公告',
                           form=form)

