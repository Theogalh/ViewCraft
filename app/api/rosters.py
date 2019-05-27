from app.api import bp
from flask import jsonify, g
from app.models import Roster, Character
from app import db
from app.api.auth import token_auth
from app.api.errors import error_response, bad_request


@bp.route('/roster', methods=['GET'])
@token_auth.login_required
def get_all_roster():
    """
    Return all rosters of the current logged user.
    :return: List of Roster.to_dict() result.
    """
    data = []
    for roster in g.current_user.rosters:
        data.append(roster.to_dict())
    return jsonify(data), 200


@bp.route('/roster/<string:name>', methods=['GET'])
@token_auth.login_required
def get_roster(name):
    """
    Return specific roster of the current logged user.
    :param name: name of the roster
    :return: Roster.to_dict result of the named roster.
    """
    name = name.capitalize()
    roster = g.current_user.get_roster(name)
    if not roster:
        return error_response(404, 'Roster does not exist')
    return jsonify(roster.to_dict()), 200


@bp.route('/roster/<string:name>', methods=['POST'])
@token_auth.login_required
def add_roster(name):
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
    return jsonify(roster.to_dict()), 201


@bp.route('/roster/<string:name>', methods=['PUT'])
@token_auth.login_required
def refresh_roster(name):
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


@bp.route('/roster/<string:name>', methods=['DELETE'])
@token_auth.login_required
def del_roster(name):
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


@bp.route('/roster/<string:name>/members', methods=['GET'])
@token_auth.login_required
def get_characters(name):
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
    return jsonify(data), 200


@bp.route('/roster/<string:name>/members/<string:realm>/<string:charName>', methods=['POST'])
@token_auth.login_required
def add_character(name, realm, charName):
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
            char.refresh()
        except ValueError:
            return bad_request('Character {}:{} does not exists'.format(realm, charName))
        db.session.add(char)
    if roster.is_in_roster(char):
        return bad_request('Character {}:{} is already in roster {}'.format(realm, charName, name))
    roster.add_member(char)
    db.session.commit()
    return jsonify('Character {}:{} added to roster {}'.format(realm, charName, name)), 201


@bp.route('/roster/<string:name>/members/<string:realm>/<string:charName>', methods=['PUT'])
@token_auth.login_required
def refresh_character(name, realm, charName):
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
        char.refresh()
        db.session.commit()
        return jsonify('Character {}:{} refresh'.format(realm, charName)), 200
    else:
        return bad_request('Character {}:{} is not in roster {}'.format(realm, charName, name))


@bp.route('/roster/<string:name>/members/<string:realm>/<string:charName>', methods=['DELETE'])
@token_auth.login_required
def del_character(name, realm, charName):
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
        return jsonify('Character {}:{} deleted from roster {}'.format(realm, charName, name)), 200
    else:
        return bad_request('Character {}:{} is not in roster {}'.format(realm, charName, name))
