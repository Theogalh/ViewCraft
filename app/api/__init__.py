from flask_restplus import Api
from app.api.rosters import api as rosters_ns
from app.api.tokens import api as tokens_ns
from app.api.guilds import api as guilds_ns
from app.api.users import api as users_ns
from app.api.characters import api as characters_ns
from app.api.posts import api as posts_ns
from app.api.me import api as me_ns
from flask import Blueprint, current_app, request, make_response
import json

bp = Blueprint('api', __name__)
api = Api(
    bp,
    title='ViewCraft API',
    version='1.0',
    description='A description',
    doc='/doc'
)

api.add_namespace(rosters_ns)
api.add_namespace(tokens_ns)
api.add_namespace(guilds_ns)
api.add_namespace(users_ns)
api.add_namespace(characters_ns)
api.add_namespace(posts_ns)
api.add_namespace(me_ns)


@api.representation('application/json')
def restful_output_json(data, code, headers=None):
    """Makes a Flask response with a JSON encoded body"""

    if current_app.debug or request.headers.get('X-Pretty-JSON', 0) == "1":
        dumped = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False) + "\n"
    else:
        dumped = json.dumps(data, ensure_ascii=False) + "\n"

    resp = make_response(dumped, code)
    resp.headers.extend(headers or {})
    if code == 204:
        resp.headers['Content-Length'] = 0
    return resp


@bp.before_request
def before_request():
    """Before request for API Blueprint
    """
    pass


@bp.after_request
def after_request(resp):
    """
    """
    return resp
