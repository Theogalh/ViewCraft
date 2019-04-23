from app import db,login, bnet
from app.data import CLASS, RACE
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
from flask import url_for
import base64
import os
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
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))

    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
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
        data = {
            'id': self.id,
            'username': self.username,
            'last_seen': self.last_seen.isoformat() + 'Z',
            'about_me': self.about_me,
            'post_count': self.posts.count(),
            'follower_count': self.followers.count(),
            'followed_count': self.followed.count(),
            '_links': {
                'self': url_for('api.get_user', id=self.id),
                'followers': url_for('api.get_followers', id=self.id),
                'followed': url_for('api.get_followed', id=self.id),
                'avatar': self.avatar(128)
            }
        }
        if include_email:
            data['email'] = self.email
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])

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

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b16encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def from_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user

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

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

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

    ilvl_average = db.Column(db.Float)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    members = db.relationship(
        'Character', secondary=roster_member,
        backref=db.backref('rosters', lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<Roster {}:{}>'.format(self.region, self.name)

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)

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

    armory_link = db.Column(db.String(280))
    wowprogress_link = db.Column(db.String(280))

    members = db.relationship('Character', backref='guild', lazy='dynamic')

    creation_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    update_date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # TODO Voir comment stocker le progress de la guilde.

    def __repr__(self):
        return '<Guild {}:{}:{}>'.format(self.region, self.realm, self.name)

    def add_member(self, character):
        self.members.append(character)

    def del_member(self, character):
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


class Character(db.Model):
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

    # TODO Ajouter en tache de fond.
    def refresh(self, index=0, roster=False):

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
        r = bnet.get(url)
        if r.status_code != 200:
            self.rio_score = 0
        else:
            r = r.json()
            self.rio_score = r["mythic_plus_scores"]["all"]
            self.rio_link = r["profile_url"]
        self.update_date = datetime.now()
        # TODO Ajouter le check de MM+.
        # TODO Ajouter le lien warcraftlogs

    # def get_msg(self, leaves):
    #     if leaves:
    #         mod = 'left'
    #     else:
    #         mod = 'joined'
    #     msg = 'Player {} {} {}.\n' \
    #           'Ilvl : {}\n' \
    #           'Rio Score : {}\n' \
    #           'Class : {}\n' \
    #           'Race : {} \n' \
    #           'Armory : <{}>\n' \
    #           'RaiderIo : <{}>\n'.format(self.name, mod, self.guild, self.ilvl, self.raiderio, self.classe, self.race,
    #                                      self.armory, self.raiderio_link)
    #     return msg

# class Task(db.Model):
#     id = db.Column(db.String(36), primary_key=True)
#     name = db.Column(db.String(128), index=True)
#     description = db.Column(db.String(128))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     complete = db.Column(db.Boolean, default=False)
#
#     def get_rq_job(self):
#         try:
#             rq_job = rq_job.Job.fetch(self.id, connection=current_app.redis)
#         except (redis.exceptions.RedisError, rq.exceptions.NoSuchJobError):
#             return None
#         return rq_job