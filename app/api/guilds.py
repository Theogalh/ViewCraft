from app.api import bp
from flask import jsonify, request, url_for, current_app
from app.models import Guild
from app.api.errors import bad_request, error_response
from app import db, bnet
from app.api.auth import token_auth


@bp.route('/<string:realm>/guilds/')
@token_auth.login_required
def get_guilds(realm):
    """
    Get all guilds of a Realm.
    :param region: Region of the realm
    :param realm: Realm of the guilds
    :return: List of Guild.to_dict
    """
    data = []
    realm = realm.capitalize()
    guilds = Guild.query.filter_by(region=current_app.config['BNET_REGION'], realm=realm).all()
    if not guilds:
        return bad_request('Verify the realm and region.')
    for guild in guilds:
        data.append(guild.to_dict())
    return jsonify(data)


@bp.route('/<string:realm>/guild/<string:guildname>', methods=['GET'])
@token_auth.login_required
def get_guild(realm, guildname):
    """
    Return all guild informations, create her and refresh her if she does'nt exist in DB.
    :param region: Region of the Guild
    :param realm: Realm of the Guild
    :param guildname: Name of the Guild/
    :return: Guild.to_dict or 404.
    """
    realm = realm.capitalize()
    guildname = guildname.capitalize()
    guild = Guild.query.filter_by(region=current_app.config['BNET_REGION'], realm=realm, name=guildname).first()
    if not guild:
        req = bnet.get_guild(realm, guildname)
        if req.status_code != 200:
            return error_response(404, 'Guild {}:{}:{} does not exist'.format(
                current_app.config['BNET_REGION'], realm, guildname
            ))
        guild = Guild(region=current_app.config['BNET_REGION'], realm=realm, name=guildname)
        db.session.add(guild)
        db.session.commit()
    return jsonify(guild.to_dict())


@bp.route('/<string:realm>/guild/<string:guildname>', methods=['POST'])
@token_auth.login_required
def refresh_guild(realm, guildname):
    """
    Refresh guild with Bnet API. Create her in DB if she doesn't.
    :param region: Region of the Guild
    :param realm: Realm of the Guild
    :param guildname: Name of the Guild
    :return: Guild informations
    """
    realm = realm.capitalize()
    guildname = guildname.capitalize()
    guild = Guild.query.filter_by(region=current_app.config['BNET_REGION'], realm=realm, name=guildname).first()
    if not guild:
        req = bnet.get_guild(realm, guildname)
        if req.status_code != 200:
            return error_response(404, 'Guild {}:{}:{} does not exist'.format(
                current_app.config['BNET_REGION'], realm, guildname
            ))
        guild = Guild(region=current_app.config['BNET_REGION'], realm=realm, name=guildname)
        guild.refresh_from_dict(req.json())
        db.session.add(guild)
        db.session.commit()
    else:
        guild.refresh()
        db.session.commit()
    return jsonify(guild.to_dict())


@bp.route('/<string:realm>/guild/<string:guildname>/news', methods=['GET'])
@token_auth.login_required
def get_guild_news(realm, guildname):
    """
    Get the 5 lasts guild news.
    :param region: Region of the Guild
    :param realm: Realm of the Guild
    :param guildname: Name of the Guild
    :return: List of 5 lasts GuildPost of the Guild.
    """
    realm = realm.capitalize()
    guildname = guildname.capitalize()
    guild = Guild.query.filter_by(region=current_app.config['BNET_REGION'], realm=realm, name=guildname).first()
    if not guild:
        return error_response(404, 'Guild {}:{}:{} does not exist'.format(
            current_app.config['BNET_REGION'], realm, guildname
        ))
    return jsonify(guild.get_news())
