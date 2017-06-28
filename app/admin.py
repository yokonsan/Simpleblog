from app import app, db
from flask_login import login_required
from .decorators import admin_required
from flask import render_template, redirect, url_for, flash, request
from .models import Comment, Post


# 管理员页面
@app.route('/admin/')
@admin_required
@login_required
def admin():

    return render_template('admin.html',
                           title='管理')

@app.route('/admincomment/')
@admin_required
@login_required
def admin_comment():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=app.config['COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('admin_comment.html', comments=comments,
                           pagination=pagination, page=page,
                           nums=len(comments),
                           title='管理评论')
# 恢复评论
@app.route('/adminrecover/<int:id>')
@login_required
def admin_recover(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('admin_comment'))
# 删除评论
@app.route('/admindelate/<int:id>')
@login_required
def admin_delate(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('admin_comment'))

@app.route('/adminpost/')
@admin_required
@login_required
def admin_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('admin_post.html', posts=posts,
                           pagination=pagination, page=page,
                           nums = len(posts),
                           title='管理文章')

# 恢复文章
@app.route('/recoverpost/<int:id>')
@login_required
def recover_post(id):
    post = Post.query.get_or_404(id)
    post.disabled = False
    db.session.add(post)
    return redirect(url_for('admin_post'))
# 删除文章
@app.route('/delatepost/<int:id>')
@login_required
def delate_post(id):
    post = Post.query.get_or_404(id)
    post.disabled = True
    db.session.add(post)
    return redirect(url_for('admin_post'))
