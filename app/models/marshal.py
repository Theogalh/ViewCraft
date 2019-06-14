from flask_restplus import fields
from flask import url_for


class LinksCharacter(fields.Raw):
    __schema_type__ = 'dict'
    __schema_example__ = "{self: url for character,guild: url for the character guild}"

    def format(self, value):
        # TODO Ajouter le lien vers la guild.
        return {
            'self': url_for('api.characters_character_specific', name=value[0], realm=value[1]),
        }


class LinksGuild(fields.Raw):
    __schema_type__ = 'dict'
    __schema_example__ = "{self: url for guild}"

    def format(self, value):
        return {
            'self': url_for('api.guilds_guilds_specific', name=value[0], realm=value[1]),
        }


class LinksRoster(fields.Raw):
    __schema_type__ = 'dict'
    __schema_example__ = "{\nself: url for roster,\nmembers: url for roster's members\n}"
    #    __schema_format__ = 'self, members'

    def format(self, value):
        return {
            'self': url_for('api.rosters_specific_roster', name=value),
            'members': url_for('api.rosters_roster_members', name=value)
        }


guilds_public_fields = {
    'name': fields.String(description='Name of the Characters',
                          attribute='name'),
    'realm': fields.String(description='Realm of the Characters',
                           attribute='realm'),
    'region': fields.String(description='Region of the Characters',
                            attribute='region'),
    'armory_link': fields.String(description='Link to armory', attribute='armory_link'),
    'wowprogress_link': fields.String(description='Link to wowprogress', attribute='wowprogress_link'),
    'creation_date': fields.DateTime(description='Creation datetime of the Guild',
                                     attribute='creation_date'),
    'update_date': fields.DateTime(description='Last updated datetime of the Guild',
                                   attribute='update_date'),
    'links': LinksGuild(description='Links about the guild', attribute='infos',
                        about='Link for self guild')
}

character_public_fields = {
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
}

roster_public_fields = {
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
}

user_public_fields = {
    'username': fields.String(description='Username of the User', attribute='username'),
    'about_me': fields.String(description='Description of the User', attribute='about_me'),
    'last_seen': fields.DateTime(description='Date where the user was seen last time.', attribute='last_seen')
}


me_private_fields = {
    'username': fields.String(description='Username of the User', attribute='username'),
    'about_me': fields.String(description='Description of the User', attribute='about_me'),
    'last_seen': fields.DateTime(description='Date where the user was seen last time.', attribute='last_seen'),
    'email': fields.String(description='Email of the User.', attribute='email'),
}

posts_public_fields = {
    'author': fields.String(attribute='author.username'),
    'body': fields.String(attribute='body'),
    'creation_date': fields.DateTime(attribute='creation_date'),
    'update_date': fields.DateTime(attribute='update_date'),
}
