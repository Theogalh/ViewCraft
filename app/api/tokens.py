from app.api.auth import basic_auth, token_auth
from flask import g
from app import db

from flask_restplus import Namespace, Resource

api = Namespace('tokens', description='Tokens operations')


@api.route('')
class TokenManagement(Resource):
    @basic_auth.login_required
    @api.header('Authorization', 'Basic', required=True)
    @api.doc(description='Get an authentification\'s token')
    @api.response(403, 'Not Authorized')
    def post(self):
        """
        Get an authentification token
        :return: Response with token parameter.
        """
        token = g.current_user.get_token()
        db.session.commit()
        return {'token': token}, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Revoke an authentification\'s token')
    @api.response(403, 'Not Authorized')
    @token_auth.login_required
    def delete(self):
        """
        Revoke the user's token.
        :return: None
        """
        g.current_user.revoke_token()
        db.session.commit()
        return '', 204
