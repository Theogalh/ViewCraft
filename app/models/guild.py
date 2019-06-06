from app import db
from datetime import datetime


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
        self.members.append(character)

    def del_member(self, character):
        """
        Delete a Character in the guild.
        :param character: Character object to del of the Guild.
        :return: None
        """
        self.members.remove(character)

    # TODO En faire une task.
    def refresh(self, created):
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
