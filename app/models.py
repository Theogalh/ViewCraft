from app import db,login, bnet
from app.data import CLASS, RACE
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask import url_for
import base64
import os
import requests
import redis
import rq


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

guild_followers = db.Table('guild_followers',
                           db.Column('guild_id', db.Integer, db.ForeignKey('guild.id')),
                           db.Column('follower_id', db.Integer, db.ForeignKey('user.id'))
                           )


class PaginateAPIMixin(object):
    """
    A class for Paginate the API Result.
    """
    @staticmethod
    def to_collection_dict(query, page, per_page, endpoint, **kwargs):
        resources = query.paginate(page, per_page, False)
        data = {
            'items': [item.to_dict() for item in resources.item],
            '_meta': {
                'page': per_page,
                'total_pages': resources.pages,
                'total_items': resources.total
            },
            '_links': {
                'self': url_for(endpoint, page=page, per_page=per_page, **kwargs),
                'next': url_for(endpoint, page=page + 1, per_page=per_page, **kwargs) if resources.has_next else None,
                'prev': url_for(endpoint, page=page - 1, per_page=per_page, **kwargs) if resources.has_prev else None
            }
        }
        return data


class User(PaginateAPIMixin, UserMixin, db.Model):
    """
    User model Class.
    A User can Follow / Unfollow an other User.
    A User can Follow / Unfollow some Guild
    A User can Create or Delete some Roster
    """
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    posts = db.relationship('UserPost', backref='author', lazy='dynamic')
    rosters = db.relationship('Roster', backref='owner', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )
    guilds_followed = db.relationship(
        'Guild', secondary=guild_followers,
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def to_dict(self, include_email=False):
        """
        Return all Users informations in a dict.
        :param include_email: If True, return also the email adress.
        :return: Dict with user's information for API Response.
        """
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', name=self.username),
                'followers': url_for('api.get_followers', name=self.username),
                'followed': url_for('api.get_followed', name=self.username),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        """
        Load users information by a Dict for User creation or Edit.
        :param data: Dict with informations to change.
        :param new_user: if True, change the password.
        :return: None
        """
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

    def set_password(self, password):
        """
        Generate a new password_hash.
        :param password: New password in clear.
        :return: None
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if password is ok.
        :param password: password in clean
        :return: True or False
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        """
        Return gravatar link to User's avatar with his email.
        :param size: Size for the avatar.
        :return: Avatar links in string.
        """
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_token(self, expires_in=3600):
        """
        Get the authentification user Token, or create him.
        :param expires_in: int for expiration token in Seconds.
        :return: User.token string.
        """
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b16encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        """
        Change expiration date to now -1 for the Token.
        :return: None
        """
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def from_token(token):
        """
        Get an User from a Auth Token.
        :param token: String with authentification Token.
        :return: User object or None
        """
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

    def follow(self, user):
        """
        Follow an User
        :param user: User Object
        :return: None
        """
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """
        Unfollow an User.
        :param user: User Object
        :return: None
        """
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """
        Check if User follow an other User.
        :param user: User object
        :return: True or False
        """
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """
        Get all followed_posts
        :return: List of Post Object.
        """
        # TODO A voir avec la refonte des posts.
        followed = UserPost.query.join(
            followers, (followers.c.followed_id == UserPost.user_id)).filter(
            followers.c.follower_id == self.id)
        own = UserPost.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(UserPost.creation_date.desc())

    def follow_guild(self, guild):
        """
        Follow a Guild
        :param guild: Guild Object
        :return: None
        """
        if not self.is_following_guild(guild):
            self.guilds_followed.append(guild)

    def unfollow_guild(self, guild):
        """
        Unfollow a Guild.
        :param guild: Guild Object
        :return: None
        """
        if self.is_following_guild(guild):
            self.guilds_followed.remove(guild)

    def is_following_guild(self, guild):
        """
        Return true if the Guild Object is followed by User.
        :param guild: Guild Object
        :return: True or False.
        """
        return self.guilds_followed.filter(
            guild_followers.c.guild_id == guild.id).count() > 0

    def followed_guilds(self):
        """
        Return the guilds followed by User.
        :return: List of Guild object.
        """
        return self.guilds_followed.all()

    def add_roster(self, roster):
        """
        Link a Roster to the User.
        :param roster: Roster object
        :return: None
        """
        if roster not in self.rosters:
            self.rosters.append(roster)

    def del_roster(self, roster):
        """
        Delete a roster created by User.
        :param roster: Roster object.
        :return: None
        """
        # TODO A voir a prendre le nom, plutot que l'object user.
        # TODO A voir a Deprecated, pour utiliser db.session.delete() dans les methodes.
        self.rosters.remove(roster)

    def get_roster(self, name):
        """
        Get a roster created by User by his name.
        :param name: String with the name of the Roster
        :return: Roster object, or None.
        """
        for roster in self.roster:
            if roster.name is name:
                return roster
        return None


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)

    body = db.Column(db.String(140))

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<Post {}>'.format(self.body)


class UserPost(Post):
    """
    User's post for post news.
    """
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<UserPost {}>'.format(self.body)


class GuildPost(Post):
    """
    Guild's post
    """

    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'))

    def __repr__(self):
        return '<GuildPost {}>'.format(self.body)


class RosterPost(Post):
    """
    Roster's post
    """

    roster_id = db.Column(db.Integer, db.ForeignKey('roster.id'))

    def __repr__(self):
        return '<RosterPost {}>'.format(self.body)


roster_member = db.Table('roster_member',
                         db.Column('roster_id', db.Integer, db.ForeignKey('roster.id')),
                         db.Column('character_id', db.Integer, db.ForeignKey('character.id'))
                         )


class Roster(db.Model):
    """
    Roster model Class.
    A Roster can have multiples Character
    A Roster can be link to only one User
    A Roster can be followed by multiples users
    A Roster can post RosterPost
    """
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(24))

    ilvl_average = db.Column(db.Float, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    members = db.relationship(
        'Character', secondary=roster_member,
        backref=db.backref('rosters', lazy='dynamic'),
        lazy='dynamic'
    )
    posts = db.relationship('RosterPost', backref='author', lazy='dynamic')

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self, characters=False):
        data = {
            'id': self.id,
            'name': self.name,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            '_links': {
                'self': url_for('api.get_roster', name=self.name),
                'characters': url_for('api.get_characters', name=self.name)
            }
        }
        if characters:
            char_data = []
            for char in self.members:
                char_data.append(char.to_dict())
            data['members'] = char_data
        return data

    def __repr__(self):
        return '<Roster {}>'.format(self.name)

    def add_member(self, character):
        """
        Add a Character in the Roster.
        :param character: Character object
        :return: None
        """
        # TODO Ajouter un RosterPost
        if not self.is_in_roster(character):
            self.members.append(character)

    def del_member(self, character):
        """
        Delete a Character in the Roster.
        :param character: Character object
        :return: None
        """
        # TODO Ajouter un RosterPost
        if self.is_in_roster(character):
            self.members.remove(character)

    def is_in_roster(self, character):
        """
        Return the Character state from the Roster.
        :param character: Character Object
        :return: True if character is in Roster, else False.
        """
        return self.members.filter(
            roster_member.c.character_id == character.id).count() > 0


class Guild(db.Model):
    """
    Guild Model Class.
    A Guild can be followed by multiples Users.
    A Guild can create GuildPost for News.
    A Guild can be linked to multiples Character.
    """
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(24))
    realm = db.Column(db.String(24))
    region = db.Column(db.String(24))

    armory_link = db.Column(db.String(280))
    wowprogress_link = db.Column(db.String(280))

    members = db.relationship('Character', backref='guild', lazy='dynamic')
    posts = db.relationship('GuildPost', backref='author', lazy='dynamic')

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # TODO Voir comment stocker le progress de la guilde.

    def __repr__(self):
        return '<Guild {}:{}:{}>'.format(self.region, self.realm, self.name)

    def add_member(self, character):
        """
        Add a new Character to the guild.
        :param character: Character object.
        :return: None
        """
        # TODO Ajouter la creation de GuildPost si c'est call par un REFRESH.
        self.members.append(character)

    def del_member(self, character):
        """
        Delete a Character in the guild.
        :param character: Character object to del of the Guild.
        :return: None
        """
        # TODO Ajouter la creation de GuildPost si c'est call par un REFRESH.
        self.members.remove(character)

    # TODO En faire une task.
    def refresh(self):
        # TODO Coder la fonction
        # Refresh les members
        # Post_Update a chaque leave / down / join
        # Update wowprogress_link et armory_link
        # Update la update_date
        pass

    def post_update(self, character):
        # TODO Creer un GuildPost affichant le leaver/joiner/downdunboss
        pass

    def get_news(self, all=False):
        """
        Return weekly guildPosts posted by the guild.
        :param all: Return All the guild posts.
        :return: List of guildPost objects.
        """
        # TODO Ajouter la fonction Get news
        return []

    def to_dict(self):
        # TODO Ajouter la fonction TO DICT
        return self.__dict__


class Character(db.Model):
    """
    Character Models Class.
    A character can be in a multiple Roster, and One guild.
    No CharacterPost.
    """
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(24))
    realm = db.Column(db.String(24))
    region = db.Column(db.String(24))

    classe = db.Column(db.String(24))
    race = db.Column(db.String(24))

    level = db.Column(db.Integer)
    ilevel = db.Column(db.Float)
    rio_score = db.Column(db.Integer)

    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'))

    armory_link = db.Column(db.String(280))
    rio_link = db.Column(db.String(280))
    wlog_link = db.Column(db.String(280))

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True)

    def __repr__(self):
        return '<Character {}:{}:{}>'.format(self.region, self.realm, self.name)

    def to_dict(self):
        data = {
            'name': self.name,
            'realm': self.realm,
            'class': self.classe,
            'race': self.race,
            'level': self.level,
            'ilevel': self.ilevel,
            'rio_score': self.rio_score,
            '_links': {
                'self': url_for('api.get_character', name=self.name, realm=self.realm),
                'armory': self.armory_link,
                'raiderio': self.rio_link,
                'warcraftlog': self.wlog_link
            }
        }
        return data

    # TODO Ajouter en tache de fond.
    def refresh(self, index=0, roster=False):
        """
        Refresh all web-data of the character.
        :param index: For retry the bnet request who sometimes failed.
        :param roster: For only refresh the data for the Roster, and not all the character.
        :return: None
        """

        if index > 3:
            return 404
        r = bnet.get_player(self.server, self.name, "items")
        if r.status_code != 200:
            return self.refresh(index+1)
        r = r.json()
        self.ilevel = int(r["items"]['averageItemLevelEquipped'])
        if roster:
            return
        self.classe = CLASS[int(r["class"])]
        self.race = RACE[int(r["race"])]
        self.armory_link = "https://worldofwarcraft.com/fr-fr/character/{}/{}".format(
            self.server,
            self.name
        )
        url = 'https://raider.io/api/v1/characters/profile?region={}&realm={}&name={}&fields=mythic_plus_scores'.format(
            bnet.region,
            self.server,
            self.name
        )
        r = requests.get(url)
        if r.status_code != 200:
            self.rio_score = 0
        else:
            r = r.json()
            self.rio_score = r["mythic_plus_scores"]["all"]
            self.rio_link = r["profile_url"]
        self.update_date = datetime.now()
        # TODO Ajouter le check de MM+.
        # TODO Ajouter le lien warcraftlogs
