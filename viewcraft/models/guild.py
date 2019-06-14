from viewcraft import db, bnet
from datetime import datetime
from viewcraft.models.character import Character, get_character


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

    @property
    def infos(self):
        return self.name, self.realm

    def check_leaver(self):
        guild = bnet.get_guild(self.realm, self.name)
        listName = []
        for member in guild['members']:
            if member['level'] == 120:
                listName.append((member['name'], member['realm']))
        for member in self.members:
            if member.infos not in listName:
                # TODO Add GuildPost for Leave
                self.members.del_member(member)
            listName.remove(member.infos)
        for infos in listName:
            char = get_character(infos[0]. infos[1])
            if not char:
                continue
            self.add_member(char)
            # TODO post un GuildPost for Join

    def refresh(self):
        for char in self.members:
            try:
                char.refresh()
            except ValueError as e:
                raise ValueError(e)

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
