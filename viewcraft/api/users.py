from flask import url_for, g
from viewcraft.models import User
from viewcraft import db
from viewcraft.api.auth import token_auth
from viewcraft.models.marshal import user_public_fields, posts_public_fields
from flask_restplus import Namespace, Resource, fields

api = Namespace('users', description='Users operations')


class UsersResource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


user_public = api.model('User', user_public_fields)
user_public['posts'] = fields.List(fields.Nested(api.model('Post', posts_public_fields)))
user_public['followed'] = fields.List(fields.String(attribute='username'))

user_create_parser = api.parser()
user_create_parser.add_argument('username', type=str, help='Username of the User')
user_create_parser.add_argument('email', type=str, help='Email of the User')
user_create_parser.add_argument('password', type=str, help='password of the User')
# TODO Ajouter un Captcha checking.

user_modify_parser = api.parser()
user_modify_parser.add_argument('username', type=str, help='New username for the User', required=False)
user_modify_parser.add_argument('about_me', type=str, help='New description for the User.', required=False)
user_modify_parser.add_argument('password', type=str, help='New password for the User', required=False)


@api.route('')
class UsersRest(Resource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get all users.')
    @api.response(403, 'Not Authorized')
    @token_auth.login_required
    @api.marshal_list_with(user_public)
    def get(self):
        return User.query.all(), 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Create a new User account')
    @api.response(403, 'Not Authorized')
    @api.marshal_with(user_public)
    @api.expect(user_create_parser)
    def post(self):
        # TODO Check le CAPTCHA
        args = user_create_parser.parse_args()
        if User.query.filter_by(username=args['username'].capitalize()).first():
            api.abort(400, "Username already exists.")
        if User.query.filter_by(username=args['email']).first():
            api.abort(400, "Email already exists.")
        user = User(username=args['username'].capitalize(), email=args['email'])
        user.set_password(args['password'])
        db.session.add(user)
        db.session.commit()
        return user, 201, {'Location': url_for('api.users_users_specific', username=user.username)}


@api.route('/<username>')
class UsersSpecific(UsersResource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a specific User account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    @api.marshal_with(user_public)
    def get(self, username):
        user = User.query.filter_by(username=username.capitalize()).first()
        if not user:
            return api.abort(404, 'User {} does not exist.'.format(username))
        return user, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Follow an User')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    def post(self, username):
        user = User.query.filter_by(username=username.capitalize()).first_or_404()
        if user == g.current_user:
            api.abort(400, 'U can not follow yourself')
        g.current_user.follow(user)
        db.session.commit()
        return 'You are following {}'.format(username), 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='UnFollow an User')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such User')
    def delete(self, username):
        user = User.query.filter_by(username=username.capitalize()).first_or_404()
        if user == g.current_user:
            api.abort(400, 'You cannot unfollow yourself!')
        g.current_user.unfollow(user)
        db.session.commit()
        return 'You are unfollowing {}!'.format(username), 200
