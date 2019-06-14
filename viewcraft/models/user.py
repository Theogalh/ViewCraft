from viewcraft import db, login
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask import url_for
import base64
import os
from viewcraft.models.paginate import PaginateAPIMixin
from viewcraft.models.post import UserPost

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

guild_followers = db.Table('guild_followers',
                           db.Column('guild_id', db.Integer, db.ForeignKey('guild.id')),
                           db.Column('follower_id', db.Integer, db.ForeignKey('user.id'))
                           )


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


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
        for roster in self.rosters:
            if roster.name == name:
                return roster
        return None
