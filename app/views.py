from app import app
from flask import render_template, flash, redirect
from .forms import LogonForm


@app.route('/')
@app.route('/index')
def indexx():
    return '<h1>Hello world!</h1>'


@app.route('/login', methods=['GET','POST'])
def login():
    form = LogonForm()
    if form.validate_on_submit():
        flash('登录请求OpenID="' + form.openid.data + '", 记住我=' + str(form.remember_me.data))
        return redirect('/index')
    return render_template('login.html',
                           title = '登录',
                           form =form,
                           providers = app.config['OPENID_PROVIDERS'])

