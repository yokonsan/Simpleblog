from flask import request, g, jsonify, abort, url_for, current_app
from .. import db
from ..models import Post, Permission
from . import api
from .errors import forbidden
from .decorators import permission_required


"""
REST 架构 API 中使用的 HTTP 请求方法：
    请求方法 ---- 目标 ---- 说明 ---- HTTP状态码
    -----------------------------------------------
    GET ---- 单个资源的URL ---- 获取目标资源 ---- 200
    GET ---- 资源集合的URL ---- 获取资源的集合，如有分页，就是一页中的资源 ---- 200
    POST ---- 资源集合的URL ---- 创建新资源，并将其加入目标集合。服务器为新资源指派URL，并在响应的Location首部中返回 ---- 201
    PUT ---- 单个资源的URL ---- 修改一个现有资源。如果客户端能为资源指派URL，还可以用来创建新资源 ---- 200
    DELETE ---- 单个资源的URL ---- 删除一个资源 ---- 200
    DELETE ---- 资源集合的URL ---- 删除目标集合的所有资源 ---- 200
"""

# 文章资源get请求
@api.route('/posts/')
def get_posts():
    # posts = Post.query.all()
    # return jsonify({'posts': [post.to_json() for post in posts]})
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

# post请求
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()), 201, {'Location': url_for('api.get_post',id=post.id, _external=True)}

# put请求
@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.operation(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.title = request.json.get('title', post.title)
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())
