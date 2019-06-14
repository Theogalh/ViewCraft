from app.api.auth import token_auth
from flask_restplus import Namespace, Resource, fields
from app.models.character import Character, get_character
from app import db
from app.api.errors import bad_request
from app.models.marshal import character_public_fields, guilds_public_fields

api = Namespace('characters', description='Characters operations')


class CharactersRessource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


character_public = api.model('Character', character_public_fields)
character_public['guild'] = fields.Nested(api.model('Guild', guilds_public_fields))

character_fields = api.parser()
character_fields.add_argument('name', type=str, help='Name of the character')
character_fields.add_argument('realm', type=str, help='Realm of the character')


@api.route('/<realm>/<name>')
class CharacterSpecific(CharactersRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a character specific')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such character')
    @api.marshal_with(character_public)
    @api.expect(character_fields)
    def get(self, realm, name):
        """
        Return all characters of the current logged user.
        :return: List of Characters.to_dict() result.
        """
        char = get_character(realm.capitalize(), name.capitalize())
        if not char:
            api.abort(404, 'Character {}:{} not found.'.format(realm, name))
        db.session.commit()
        return char, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Refresh a character in database.')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such character')
    @api.marshal_with(character_public)
    @api.expect(character_fields)
    def put(self, realm, name):
        """
        Return all characters of the current logged user.
        :return: List of Characters.to_dict() result.
        """
        char = get_character(realm.capitalize(), name.capitalize())
        if not char:
            api.abort(404, 'Character {}:{} not found.'.format(realm, name))
        char.refresh()
        db.session.commit()
        return char, 200
