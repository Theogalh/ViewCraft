from app.api import bp
from flask import jsonify, request, url_for
from app.models import User
from app.api.errors import bad_request, error_response
from app import db
from app.api.auth import token_auth

CREATING_FIELDS = [
    'username',
    'email',
    'password',
]


@bp.route('/users/<int:id>', methods=['GET'])
@token_auth.login_required
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
@token_auth.login_required
def get_users():
    data = []
    for user in User.query.all():
        data.append(user.to_dict())
    return jsonify(data)


@bp.route('/users/<int:id>/followers', methods=['GET'])
@token_auth.login_required
def get_followers(id):
    user = User.query.get_or_404(id)
    data = []
    for followers in user.followers.all():
        data.append(followers.to_dict())
    return jsonify(data)


@bp.route('/users/<int:id>/followed', methods=['GET'])
@token_auth.login_required
def get_followed(id):
    user = User.query.get_or_404(id)
    data = []
    for followed in user.followed.all():
        data.append(followed.to_dict())
    return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json() or {}
    for field in CREATING_FIELDS:
        if field not in data:
            return bad_request('Field {} is mandatory.'.format(field))
    if User.query.filter_by(email=data['email']).first():
        return bad_request('This email is already used.')
    if User.query.filter_by(username=data['username']).first():
        return bad_request('This username is already used.')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    response = jsonify(user.to_dict())
    response.status_code = 201

    # HTTP PROTOCOL
    response.headers['Location'] = url_for('api.get_user', id=user.id)

    return response


@bp.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    if g.current_user.id != id:
        return error_response(403, 'U cannot modify other profile')
    user = User.query_or_404(id)
    data = request.get_json() or {}
    if 'username' in data and data['username'] != user.username and \
            User.query.filter_by(username=data['username']).first():
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            User.query.filter_by(email=data['email']).first():
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return jsonify(user.to_dict())
