from flask import render_template
from . import user
from app import db

@user.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html', title='404'), 404

@user.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='500'), 500