from flask import current_app
from viewcraft.models import Guild
from viewcraft import bnet

from viewcraft import db
from viewcraft.api.auth import token_auth

from flask_restplus import Namespace, Resource
from viewcraft.models.marshal import guilds_public_fields

api = Namespace('guilds', description='Guilds operations')
guilds_public = api.model('Guild', guilds_public_fields)


class GuildRessource(Resource):
    """
    Subclass of Resource with the login_required decorator
    """
    method_decorators = [token_auth.login_required]


@api.route('/<realm>')
class AllGuildsRealms(GuildRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='List all guilds on a specific realms register on viewcraft')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such guild')
    @api.marshal_list_with(guilds_public)
    def get(self, realm):
        """
        Get all guilds of a Realm.
        :param region: Region of the realm
        :param realm: Realm of the guilds
        :return: List of Guild.to_dict
        """
        realm = realm.capitalize()
        guilds = Guild.query.filter_by(region=current_app.config['BNET_REGION'], realm=realm).all()
        if not guilds:
            return api.abort(404, 'No guilds added in this realm, or realm does not exists.')
        return guilds, 200


@api.route('/<realm>/<guildname>')
class SpecificGuild(GuildRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get guilds informations')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such guild')
    @api.marshal_with(guilds_public)
    def get(self, realm, guildname):
        """
        Return all guild informations, create her and refresh her if she does'nt exist in DB.
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
                return api.abort(404, 'Guild {}:{}:{} does not exist'.format(
                    current_app.config['BNET_REGION'], realm, guildname
                ))
            guild = Guild(region=current_app.config['BNET_REGION'], realm=realm, name=guildname)
            db.session.add(guild)
            db.session.commit()
        return guild, 200

    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Refresh guilds informations')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such guild')
    @api.marshal_with(guilds_public)
    def put(self, realm, guildname):
        """
        Refresh guild with Bnet API. Create her in DB if she doesn't.
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
                return api.abort(404, 'Guild {}:{}:{} does not exist'.format(
                    current_app.config['BNET_REGION'], realm, guildname
                ))
            guild = Guild(region=current_app.config['BNET_REGION'], realm=realm, name=guildname)
            guild.refresh_from_dict(req.json())
            db.session.add(guild)
            db.session.commit()
        else:
            guild.refresh()
            db.session.commit()
        return guild, 200


@api.route('<realm>/<guildname>/posts')
class SpecificGuildNews(GuildRessource):
    @api.header('Authorization', 'Bearer', required=True)
    @api.doc(description='Get guilds news posts')
    @api.response(403, 'Not Authorized')
    @api.response(404, 'No such guild')
    def get(self, realm, guildname):
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
            return api.abort(404, 'Guild {}:{}:{} does not exist'.format(
                current_app.config['BNET_REGION'], realm, guildname
            ))
        return guild.get_news(), 200
