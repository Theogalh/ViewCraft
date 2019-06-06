from flask import jsonify, request, url_for, g
from app.models import User
from app import db
from app.api.auth import token_auth
from app.api.errors import error_response, bad_request

from flask_restplus import Namespace, Resource

api = Namespace('users', description='Users operations')


class UsersResource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


@api.route('')
class UsersRest(Resource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get all users.')
    @api.response(403, 'Not Authorized')
    @token_auth.login_required
    def get(self):
        data = []
        for user in User.query.all():
            data.append(user.to_dict())
        return data, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Create a new User account')
    @api.response(403, 'Not Authorized')
    def post(self):
        data = request.get_json() or {}
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


@api.route('/<username>')
class UsersSpecific(UsersResource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a specific User account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return error_response(404, 'User {} does not exist.'.format(username))
        return user.to_dict(), 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Modify a specific User account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    def put(self, username):
        if g.current_user.username != username:
            return error_response(403, 'U cannot modify other profile')
        user = User.query.filter_by(username=username).first()
        if not user:
            return error_response(404, 'User {} does not exist.'.format(username))
        data = request.get_json() or {}
        if 'username' in data and data['username'] != user.username and \
                User.query.filter_by(username=data['username']).first():
            return bad_request('please use a different username')
        if 'email' in data and data['email'] != user.email and \
                User.query.filter_by(email=data['email']).first():
            return bad_request('please use a different email address')
        user.from_dict(data, new_user=False)
        db.session.commit()
        return user.to_dict(), 200


@api.route('/<username>/followers')
class UserSpecificFollowers(UsersResource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get followers of a specific User account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return error_response(404, 'User {} does not exist.'.format(username))
        data = []
        for followers in user.followers.all():
            data.append(followers.to_dict())
        return data, 200


@api.route('/<username>/followed')
class UserSpecificFollowed(UsersResource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get followed of a specific User account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            return error_response(404, 'User {} does not exist.'.format(username))
        data = []
        for followed in user.followed.all():
            data.append(followed.to_dict())
        return data, 200
