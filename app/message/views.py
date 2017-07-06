from .. import db
from . import message
from flask import redirect, render_template, current_app, request, g, flash, url_for
from flask_login import login_required, current_user
from ..models import User, Conversation, Post, Permission
from ..user.forms import SearchForm
from datetime import datetime
from .forms import LetterForm


# 用户最后一次访问时间,全文搜索
@message.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now()
        db.session.add(current_user)
        db.session.commit()
    g.search_form = SearchForm()

@message.route('/comment')
@login_required
def comment_message():
    user = User.query.filter_by(id=current_user.id).first()
    all_post = user.posts.order_by(Post.timestamp.desc()).all()
    posts = [post for post in all_post if post.draft == False]
    # 每篇文章的评论，赞是一个列表集合
    i = [post.comments for post in posts]
    x, comments = 0, []
    if i != []:
        while x < len(i):
            comments += i[x]
            x += 1
        for comment in comments:
            comment.unread = False
    like_num = [post.like_num for post in posts]
    n, likes = 0, []
    if like_num != []:
        while n < len(like_num):
            likes += like_num[n]
            n += 1
        likes = [like for like in likes if like.unread is True]
    follows = [f for f in user.followers if f.unread is True]

    return render_template('message/comment_message.html',
                           title='消息',
                           like=len(likes),
                           follow=len(follows),
                           comments=comments)

@message.route('/like')
@login_required
def like_message():
    user = User.query.filter_by(id=current_user.id).first()
    all_post = user.posts.order_by(Post.timestamp.desc()).all()
    posts = [post for post in all_post if post.draft == False]

    i = [post.comments for post in posts]
    x, comments = 0, []
    if i != []:
        while x < len(i):
            comments += i[x]
            x += 1
        comments = [comment for comment in comments if comment.unread is True]
    like_num = [post.like_num for post in posts]
    n, likes = 0, []
    if like_num != []:
        while n < len(like_num):
            likes += like_num[n]
            n += 1
        for like in likes:
            like.unread = False
    follows = [f for f in user.followers if f.unread is True]

    return render_template('message/like_message.html',
                           title='消息',
                           likes=likes,
                           comments=len(comments),
                           follow=len(follows))

@message.route('/follow')
@login_required
def follow_message():
    user = User.query.filter_by(id=current_user.id).first()
    all_post = user.posts.order_by(Post.timestamp.desc()).all()
    posts = [post for post in all_post if post.draft == False]

    i = [post.comments for post in posts]
    x, comments = 0, []
    if i != []:
        while x < len(i):
            comments += i[x]
            x += 1
        comments = [comment for comment in comments if comment.unread is True]
    like_num = [post.like_num for post in posts]
    n, likes = 0, []
    if like_num != []:
        while n < len(like_num):
            likes += like_num[n]
            n += 1
        likes = [like for like in likes if like.unread is True]
    follows = [f for f in user.followers]
    for f in follows:
        f.unread = False

    return render_template('message/follow_message.html',
                           title='消息',
                           comments=len(comments),
                           likes=len(likes),
                           follows=follows)
# 私信箱
@message.route('/letter')
@login_required
def letter_message():
    user = User.query.filter_by(id=current_user.id).first()
    all_post = user.posts.order_by(Post.timestamp.desc()).all()
    posts = [post for post in all_post if post.draft == False]

    i = [post.comments for post in posts]
    x, comments = 0, []
    if i != []:
        while x < len(i):
            comments += i[x]
            x += 1
        comments = [comment for comment in comments if comment.unread is True]
    like_num = [post.like_num for post in posts]
    n, likes = 0, []
    if like_num != []:
        while n < len(like_num):
            likes += like_num[n]
            n += 1
        likes = [like for like in likes if like.unread is True]
    follows = [f for f in user.followers if f.unread is True]

    page = request.args.get('page', 1, type=int)
    pagination = Conversation.query.filter(
        Conversation.to_user_id == current_user.id,
        ).order_by(Conversation.timestamp.desc()). \
            paginate(page, per_page=current_app.config['MESSAGES_PER_PAGE'],
                     error_out=False)
    conversations = pagination.items
    message_count = Conversation.query.filter(
        Conversation.to_user_id == current_user.id).count()

    return render_template("message/letter_message.html",
                           title='消息',
                           comments=len(comments),
                           likes=len(likes),
                           follows=len(follows),
                           pagination=pagination,
                           conversations=conversations,
                           message_count=message_count)

# 读写私信
@message.route('/write_letter/<int:id>', methods=['GET','POST'])
@login_required
def write_letter(id):
    send_conv = Conversation.query.filter_by(
        to_user_id = id,
        from_user_id = current_user.id
    ).all()
    receive_conv = Conversation.query.filter_by(
        to_user_id = current_user.id,
        from_user_id = id
    ).all()
    if receive_conv:
        for conv in receive_conv:
            conv.unread = False

    form = LetterForm()
    if current_user.operation(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        letter = form.body.data
        conversation = Conversation(from_user_id=current_user.id,
                                    to_user_id=id,
                                    letter=letter,
                                    unread=True)
        db.session.add(conversation)
        flash('发送私信成功。')
        return redirect(url_for('message.write_letter',id=id))
    return render_template('message/conversation.html',
                           title='消息',
                           receive_conv = receive_conv,
                           send_conv = send_conv,
                           all = max(len(receive_conv),len(send_conv)),
                           form=form)

# 删除会话
@message.route('delete_letter/<int:id>')
@login_required
def delete_letter(id):
    conversation = Conversation.query.filter_by(
                                id=id,
                                to_user_id=current_user.id).first_or_404()
    db.session.delete(conversation)
    flash('你已删除此条私信。')

    return redirect(url_for('message.letter_message'))
