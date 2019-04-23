from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response


@bp.app_errorhandler(404)
def not_found_error(error):
    if request.url.split('/')[3] == 'api':
        return error_response(404, 'Ressource not found')
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if request.url.split('/')[3] == 'api':
        return error_response(500, "Internal error")
    return render_template('errors/500.html'), 500
