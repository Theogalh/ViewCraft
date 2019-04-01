from app import db,login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
                     )

guild_followers = db.Table('guild_followers',
                           db.Column('guild_id', db.Integer, db.ForeignKey('guild.id')),
                           db.Column('follower_id', db.Integer, db.ForeignKey('user.id'))
                           )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    rosters = db.relationship('Roster', backref='owner', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
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

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if password is ok.
        :param password:
        :return: True if password = password_hash
        """
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.creation_date.desc())

    def follow_guild(self, guild):
        if not self.is_following_guild(guild):
            self.guilds_followed.append(guild)

    def unfollow_guild(self, guild):
        if self.is_following_guild(guild):
            self.guilds_followed.remove(guild)

    def is_following_guild(self, guild):
        return self.guilds_followed.filter(
            guild_followers.c.guild_id == guild.id).count() > 0

    def followed_guilds(self):
        return self.guilds_followed.all()

    def add_roster(self, roster):
        self.rosters.append(roster)

    def del_roster(self, roster):
        self.roster.remove(roster)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


roster_member = db.Table('roster_member',
                         db.Column('roster_id', db.Integer, db.ForeignKey('roster.id')),
                         db.Column('character_id', db.Integer, db.ForeignKey('character.id'))
                         )


class Roster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    region = db.Column(db.String(24))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    members = db.relationship(
        'Character', secondary=roster_member,
        backref=db.backref('rosters', lazy='dynamic'),
        lazy='dynamic'
    )

    def add_member(self, character):
        if not self.is_in_roster(character):
            self.members.append(character)

    def del_member(self, character):
        if self.is_in_roster(character):
            self.members.remove(character)

    def is_in_roster(self, character):
        return self.members.filter(
            roster_member.c.character_id == character.id).count() > 0


class Guild(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    realm = db.Column(db.String(24))
    region = db.Column(db.String(24))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    members = db.relationship('Character', backref='guild', lazy='dynamic')

    def add_member(self, character):
        self.members.append(character)

    def del_member(self, character):
        self.members.remove(character)

    def refresh(self):
        # TODO Coder la fonction
        pass

    def add_leaver(self, character):
        # TODO Creer un GuildPost affichant le leaver
        pass

    def add_joiner(self, character):
        # TODO Creer un GuildPost affichant le joiner
        pass


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    realm = db.Column(db.String(24))
    region = db.Column(db.String(24))
    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    guild_id = db.Column(db.Integer, db.ForeignKey('guild.id'))
