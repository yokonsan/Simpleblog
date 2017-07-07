from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Post


"""
API资源：
    资源URL ---- 方法 ---- 说明
    -------------------------------
    /users/<int:id> ---- GET ---- 一个用户
    /users/<int:id>/posts/ ---- GET ---- 一个用户发布的博客文章
    /users/<int:id>/timeline/ ---- GET ---- 一个用户所关注用户发布的文章
    /posts/ ---- GET、POST ---- 所有博客文章
    /posts/<int:id> ---- GET、PUT ---- 一篇博客文章
    /posts/<int:id>/comments/ ---- GET、POST ---- 一篇博客文章中的评论
    /comments/ ---- GET ---- 所有评论
    /comments/<int:id> ---- GET ---- 一篇评论
"""

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/posts/')
def get_user_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/users/<int:id>/timeline/')
def get_user_followed_posts(id):
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_posts', page=page-1,
                       _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_followed_posts', page=page+1,
                       _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })