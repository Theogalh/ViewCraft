from flask import g, url_for
from app.api.auth import token_auth
from flask_restplus import Namespace, Resource, fields
from app.models.character import Character
from app import db
from app.api.errors import bad_request

api = Namespace('characters', description='Characters operations')


class CharactersRessource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


class LinksCharacter(fields.Raw):
    __schema_type__ = 'dict'
    __schema_example__ = "{self: url for character}"

    def format(self, value):
        return {
            'self': url_for('api.characters_character_specific', name=value[0], realm=value[1]),
        }


character_public = api.model('Character',
                             {
                                 'name': fields.String(description='Name of the Characters',
                                                       attribute='name'),
                                 'realm': fields.String(description='Realm of the Characters',
                                                        attribute='realm'),
                                 'region': fields.String(description='Region of the Characters',
                                                         attribute='region'),
                                 'ilvl': fields.Float(description='Ilvl average for all members of the character',
                                                      attribute='ilevel'),
                                 'armory_link': fields.String(description='Link to armory', attribute='armory_link'),
                                 'wlog_link': fields.String(description='Link to warcraftLog', attribute='wlog_link'),
                                 'raiderio_link': fields.String(description='Link to raider.io', attribute='rio_link'),
                                 'creation_date': fields.DateTime(description='Creation datetime of the Characters',
                                                                  attribute='creation_date'),
                                 'update_date': fields.DateTime(description='Last updated datetime of the Characters',
                                                                attribute='update_date'),
                                 'links': LinksCharacter(description='Links about the character', attribute='infos',
                                                         about='Link for self character'),
                                 'race': fields.String(description='Race of the character', attribute='race'),
                                 'class': fields.String(description='Class of the character', attribute='classe'),
                             })

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
        char = Character.query.filter_by(name=name, realm=realm).first()
        if not char:
            char = Character(name=name, realm=realm)
            try:
                char.refresh(created=True)
            except ValueError:
                return bad_request('Character {}:{} does not exists'.format(realm, name))
            db.session.add(char)
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
        char = Character.query.filter_by(name=name, realm=realm).first()
        if not char:
            char = Character(name=name, realm=realm)
            try:
                char.refresh(created=True)
            except ValueError:
                return bad_request('Character {}:{} does not exists'.format(realm, name))
            db.session.add(char)
        else:
            try:
                char.refresh()
            except ValueError:
                db.session.delete(char)
        db.session.commit()
        return char, 200
