from app import db,login, bnet
from datetime import datetime, timedelta


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