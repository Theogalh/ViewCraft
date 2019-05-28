from app import db
from datetime import datetime
from flask import url_for

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
        # TODO Ajouter la mise a jour du ilvl_average.
        if not self.is_in_roster(character):
            self.members.append(character)

    def del_member(self, character):
        """
        Delete a Character in the Roster.
        :param character: Character object
        :return: None
        """
        # TODO Ajouter un RosterPost
        # TODO Ajouter la mise a jour du ilvl_average.
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
