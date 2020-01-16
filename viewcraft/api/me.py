from flask_restplus import Namespace, fields, Resource
from viewcraft.models.marshal import user_public_fields, roster_public_fields, posts_public_fields, me_private_fields
from viewcraft.api.auth import token_auth
from viewcraft.utils import check_password_security
from viewcraft.data import email_re
from flask import g
from viewcraft import db

api = Namespace('me', description='About me')

me_private = api.model('Me', me_private_fields)
me_private['rosters'] = fields.List(fields.Nested(api.model('Roster', roster_public_fields)))
me_private['followed'] = fields.List(fields.Nested(api.model('User', user_public_fields)))
me_private['followers'] = fields.List(fields.Nested(api.model('User', user_public_fields)))
me_private['posts'] = fields.List(fields.Nested(api.model('Post', posts_public_fields)))


me_password_parser = api.parser()
me_password_parser.add_argument('password', type=str, help='The new Password')
me_password_parser.add_argument('oldPassword', type=str, help='The old Password')


me_email_parser = api.parser()
me_email_parser.add_argument('email', type=str, help='The new email adress')


me_infos_parser = api.parser()
me_infos_parser.add_argument('about_me', type=str, help='A short description about me.')


class MeRessource(Resource):
    method_decorators = [token_auth.login_required]


@api.route('')
class MeRest(MeRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get me.')
    @api.response(403, 'Not Authorized')
    @api.marshal_with(me_private)
    def get(self):
        return g.current_user, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Change some informations about me')
    @api.expect(me_infos_parser)
    @api.marshal_with(me_private)
    def post(self):
        args = me_infos_parser.parse_args()
        g.current_user.about_me = args['about_me']
        db.session.commit()
        return g.current_user, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Delete user')
    def delete(self):
        db.session.delete(g.current_user)
        db.session.commit()
        return '', 204


@api.route('/password')
class MePassword(MeRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Change password')
    @api.response(403, 'Not Authorized')
    @api.expect(me_password_parser)
    def post(self):
        args = me_password_parser.parse_args()
        if not g.current_user.check_password(args['oldPassword']):
            api.abort(403, 'Old password incorrect')
        if not check_password_security(args['password']):
            api.abort(400, 'Need a Password secure.')
        g.current_user.set_password(args['password'])
        db.session.commit()
        return 'Password change', 200


@api.route('/email')
class MeEmail(MeRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Change email')
    @api.response(403, 'Not Authorized')
    @api.expect(me_email_parser)
    def post(self):
        args = me_email_parser.parse_args()
        if not email_re.match(args['email']):
            api.abort(400, 'Email Invalid')
        if g.current_user.email == args['email']:
            api.abort(400, 'This is already your email.')
        g.current_user.email = args['email']
        db.session.commit()
        return 'Password change', 200
