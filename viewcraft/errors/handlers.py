from flask import render_template, request
from viewcraft import db
from viewcraft.errors import bp
from viewcraft.api.errors import error_response


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= request.accept_mimetypes['text/html']


@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return error_response(404)
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return error_response(500)
    return render_template('errors/500.html'), 500
