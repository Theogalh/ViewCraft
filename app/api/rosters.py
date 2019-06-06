from flask import g
from app.models import Roster, Character
from app import db
from app.api.auth import token_auth
from app.api.errors import error_response, bad_request

from flask_restplus import Namespace, Resource

api = Namespace('rosters', description='Rosters operations')


class RosterRessource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


@api.route('')
class AllRoster(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get all rosters of current user account')
    @api.response(403, 'Not Authorized')
    def get(self):
        """
        Return all rosters of the current logged user.
        :return: List of Roster.to_dict() result.
        """
        data = []
        for roster in g.current_user.rosters:
            data.append(roster.to_dict())
        return data, 200


@api.route('/<name>')
class SpecificRoster(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    def get(self, name):
        """
        Return specific roster of the current logged user.
        :param name: name of the roster
        :return: Roster.to_dict result of the named roster.
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return error_response(404, 'Roster does not exist')
        return roster.to_dict(), 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Create a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    def post(self, name):
        """
        Create a new roster with a name for the logged user.
        :param name: Name of the new roster
        :return: Roster.to_dict of the new roster.
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if roster:
            return bad_request('Roster {} already exists.'.format(name))
        roster = Roster(name=name)
        g.current_user.add_roster(roster)
        db.session.add(roster)
        db.session.commit()
        return roster.to_dict(), 201

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Refresh a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
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
            return bad_request('Roster {} does not exist.'.format(name))
        for char in roster.members:
            try:
                char.refresh()
            except ValueError as e:
                return bad_request('Error when refreshing data for {} : {}'.format(char.name, e))
        return 'Refresh succeed', 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Delete a specific roster of current user account')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    def delete(self, name):
        """
        Delete a specifique roster of logged user.
        :param name: Name of the roster who will be deleted
        :return: None
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return bad_request('Roster {} does not exist.'.format(name))
        db.session.delete(roster)
        db.session.commit()
        return '', 204


@api.route('/<name>/members')
class RosterMembers(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get a specific roster list of members')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    def get(self, name):
        """
        Get characters in the roster.
        :param name: Name of the roster
        :return: Roster.to_dict with characters
        """
        name = name.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return bad_request('Roster {} does not exist.'.format(name))
        data = []
        for character in roster.members:
            data.append(character.to_dict())
        return data, 200


@api.route('/<name>/members/<realm>/<charName>')
class RosterMemberManagement(RosterRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Add a member to a specific roster')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.response(404, 'Not such character')
    def post(self, name, realm, charName):
        name = name.capitalize()
        realm = realm.capitalize()
        charName = charName.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return bad_request('Roster {} does not exists'.format(name))
        char = Character.query.filter_by(name=charName, realm=realm).first()
        if not char:
            char = Character(name=charName, realm=realm)
            try:
                char.refresh(created=True)
            except ValueError:
                return bad_request('Character {}:{} does not exists'.format(realm, charName))
            db.session.add(char)
        if roster.is_in_roster(char):
            return bad_request('Character {}:{} is already in roster {}'.format(realm, charName, name))
        roster.add_member(char)
        db.session.commit()
        return 'Character {}:{} added to roster {}'.format(realm, charName, name), 201

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Refresh a member of a specific roster')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.response(404, 'Not such character')
    def put(self, name, realm, charName):
        name = name.capitalize()
        realm = realm.capitalize()
        charName = charName.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return bad_request('Roster {} does not exists'.format(name))
        char = Character.query.filter_by(name=charName, realm=realm).first()
        if not char:
            return bad_request('Character {}:{} does not exists'.format(realm, charName))
        if roster.is_in_roster(char):
            try:
                char.refresh(roster=True)
            except ValueError as e:
                return bad_request("Character {}:{}: error while refresh : {}".format(realm, name, e))
            db.session.commit()
            return 'Character {}:{} refresh'.format(realm, charName), 200
        else:
            return bad_request('Character {}:{} is not in roster {}'.format(realm, charName, name))

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Delete a member to a specific roster')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'Not such roster')
    @api.response(404, 'Not such character')
    def delete(self, name, realm, charName):
        name = name.capitalize()
        realm = realm.capitalize()
        charName = charName.capitalize()
        roster = g.current_user.get_roster(name)
        if not roster:
            return bad_request('Roster {} does not exists'.format(name))
        char = Character.query.filter_by(name=charName, realm=realm).first()
        if not char:
            return bad_request('Character {}:{} does not exists'.format(realm, charName))
        if roster.is_in_roster(char):
            roster.del_member(char)
            db.session.commit()
            return 'Character {}:{} deleted from roster {}'.format(realm, charName, name), 200
        else:
            return bad_request('Character {}:{} is not in roster {}'.format(realm, charName, name))
