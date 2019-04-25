from app.api import bp
from flask import jsonify, request, g
from app.models import Roster
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
    return jsonify(data)


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
    return jsonify(roster.to_dict())


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
    return '201', jsonify(roster.to_dict())


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
    return 204, ''
