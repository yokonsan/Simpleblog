from flask import render_template, request, jsonify
from . import user
from app import db


@user.errorhandler(404)
def page_not_found(error):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html', title='404'), 404

@user.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('errors/500.html', title='500'), 500
