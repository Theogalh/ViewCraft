from flask import g, url_for
from app.models import Roster, Character
from app import db
from app.api.auth import token_auth
from flask_restplus import Namespace, Resource, fields
from app.api.characters import character_public

api = Namespace('rosters', description='Rosters operations')


class RosterRessource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


class LinksRoster(fields.Raw):
    __schema_type__ = 'dict'
    __schema_example__ = "{\nself: url for roster,\nmembers: url for roster's members\n}"
    #    __schema_format__ = 'self, members'

    def format(self, value):
        return {
            'self': url_for('api.rosters_specific_roster', name=value),
            'members': url_for('api.rosters_roster_members', name=value)
        }


roster_public = api.model('Roster',
                          {
                              'name': fields.String(description='Name of the Roster',
                                                    attribute='name'),
                              'ilvl_average': fields.Float(description='Ilvl average for all members of the roster',
                                                           attribute='ilvl_average'),
                              'creation_date': fields.DateTime(description='Creation datetime of the Roster',
                                                               attribute='creation_date'),
                              'update_date': fields.DateTime(description='Last updated datetime of the Roster',
                                                             attribute='update_date'),
                              'links': LinksRoster(description='Links about the roster', attribute='name',
                                                   about='Link for self roster'),
                              'members': fields.List(fields.Nested(character_public))
                          })

roster_fields = api.parser()
roster_fields.add_argument('name', type=str, help='Name of the roster')

roster_character_fields = api.parser()
roster_character_fields.add_argument('name', type=str, help='Name of the roster')
roster_character_fields.add_argument('realm', type=str, help='Realm of the character')
roster_character_fields.add_argument('charName', type=str, help='Name of the character')


@api.route('')
class AllRoster(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get all rosters of current user account')
    @api.response(403, 'Not Authorized')
    @api.marshal_list_with(roster_public, mask='name,ilvl_average,creation_date,update_date,links')
    def get(self):
        """
        Return all rosters of the current logged user.
        :return: List of Roster.to_dict() result.
        """
        return g.current_user.rosters.all(), 200


@api.route('/<name>')
class SpecificRoster(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.marshal_with(roster_public, mask='name,ilvl_average,creation_date,update_date,links')
    @api.expect(roster_fields)
    def get(self, name):
        """
        Return specific roster of the current logged user.
        :param name: name of the roster
        :return: Roster.to_dict result of the named roster.
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(404, 'Roster does not exist')
        return roster, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Create a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.marshal_with(roster_public, mask='name,ilvl_average,creation_date,update_date,links')
    @api.expect(roster_fields)
    def post(self, name):
        """
        Create a new roster with a name for the logged user.
        :param name: Name of the new roster
        :return: Roster.to_dict of the new roster.
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if roster:
            return api.abort(400, 'Roster {} already exists.'.format(name))
        roster = Roster(name=name)
        g.current_user.add_roster(roster)
        db.session.add(roster)
        db.session.commit()
        return roster, 201

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Refresh a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.marshal_with(roster_public, mask='name,ilvl_average,creation_date,update_date,links')
    @api.expect(roster_fields)
    def put(self, name):
        """
        Refresh the characters in the roster.
        :param name: Name of the roster
        :return: 200 if success.
        """
        # TODO A tester
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(400, 'Roster {} does not exist.'.format(name))
        for char in roster.members:
            try:
                char.refresh()
            except ValueError as e:
                return api.abort(400, 'Error when refreshing data for {} : {}'.format(char.name, e))
        return roster, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Delete a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.expect(roster_fields)
    def delete(self, name):
        """
        Delete a specifique roster of logged user.
        :param name: Name of the roster who will be deleted
        :return: None
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(400, 'Roster {} does not exist.'.format(name))
        db.session.delete(roster)
        db.session.commit()
        return '', 204


@api.route('/<name>/members')
class RosterMembers(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a specific roster list of members')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.marshal_with(roster_public)
    @api.expect(roster_fields)
    def get(self, name):
        """
        Get characters in the roster.
        :param name: Name of the roster
        :return: Roster.to_dict with characters
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(400, 'Roster {} does not exist.'.format(name))
        return roster, 200


@api.route('/<name>/members/<realm>/<charName>')
class RosterMemberManagement(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Add a member to a specific roster')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.response(404, 'Not such character')
    @api.expect(roster_character_fields)
    def post(self, name, realm, charName):
        name = name.capitalize()
        realm = realm.capitalize()
        charName = charName.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(400, 'Roster {} does not exists'.format(name))
        char = Character.query.filter_by(name=charName, realm=realm).first()
        if not char:
            char = Character(name=charName, realm=realm)
            try:
                char.refresh(created=True)
            except ValueError:
                return api.abort(400, 'Character {}:{} does not exists'.format(realm, charName))
            db.session.add(char)
        if roster.is_in_roster(char):
            return api.abort(400, 'Character {}:{} is already in roster {}'.format(realm, charName, name))
        roster.add_member(char)
        db.session.commit()
        return 'Character {}:{} added to roster {}'.format(realm, charName, name), 201

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Refresh a member of a specific roster')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.response(404, 'Not such character')
    @api.expect(roster_character_fields)
    def put(self, name, realm, charName):
        name = name.capitalize()
        realm = realm.capitalize()
        charName = charName.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(400, 'Roster {} does not exists'.format(name))
        char = Character.query.filter_by(name=charName, realm=realm).first()
        if not char:
            return api.abort(400, 'Character {}:{} does not exists'.format(realm, charName))
        if roster.is_in_roster(char):
            try:
                char.refresh(roster=True)
            except ValueError as e:
                db.session.delete(char)
                return api.abort(400, "Character {}:{}: error while refresh : {}".format(realm, name, e))
            db.session.commit()
            return 'Character {}:{} refresh'.format(realm, charName), 200
        else:
            return api.abort(400, 'Character {}:{} is not in roster {}'.format(realm, charName, name))

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Delete a member to a specific roster')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.response(404, 'Not such character')
    @api.expect(roster_character_fields)
    def delete(self, name, realm, charName):
        name = name.capitalize()
        realm = realm.capitalize()
        charName = charName.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return api.abort(400, 'Roster {} does not exists'.format(name))
        char = Character.query.filter_by(name=charName, realm=realm).first()
        if not char:
            return api.abort(400, 'Character {}:{} does not exists'.format(realm, charName))
        if roster.is_in_roster(char):
            roster.del_member(char)
            db.session.commit()
            return 'Character {}:{} deleted from roster {}'.format(realm, charName, name), 200
        else:
            return api.abort(400, 'Character {}:{} is not in roster {}'.format(realm, charName, name))
