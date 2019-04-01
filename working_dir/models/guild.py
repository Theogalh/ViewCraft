from viewcraft.models.character import Character
from viewcraft.app import application
from flask import g
from viewcraft.models.resource import Resource


class Guild(Resource):
    def __init__(self, region, server, name):
        self.name = name
        self.server = server
        self.region = region
        self.members = []

        # TODO Ajouter l'armory link & wprogress link.
        self.armory_link = None
        self.wprogress_link = None

    @property
    def path(self):
        return "guild:{}:{}:{}".format(self.region, self.server, self.name)

    @classmethod
    def from_db(cls, region, server, name):
        """
        Get a guild from the database.
        :return: Guild object instance or None if doesn't exist.
        """
        guild = Guild(region, server, name)
        if not g["redis"].exists(guild.path):
            return None
        for member in g["redis"].smembers(guild.path + ":members"):
            member = member.split(":")
            char = Character.from_db(member[1], member[2], member[3])
            if char:
                guild.members.append(char)
        return guild

    def save_db(self):
        """
        Save in Redis the guild.
        """
        for member in self.members:
            g["redis"].hsadd(self.path + ":members", member.path)

    @classmethod
    def create(cls, region, server, name):
        """
        Create a new Guild and save her in DB.
        :param region: Guild Region
        :param server: Guild Realm
        :param name:  Guild Name
        :return: Guild object created.
        """
        guild = Guild(region, server, name)
        try:
            guild.refresh()
        except AttributeError:
            raise AttributeError("Guild didn't exists")
        return guild

    def refresh(self, members=False):
        """
        Refresh all data about the guild, boolean for refresh member too..
        Raise AttributeError if guild doesnt exists.
        :param members: True for refresh data of all members.
        """
        # TODO Refresh les guilds datas.
        # TODO Remplir Leavers ici.
        if members:
            for member in self.members:
                member.refresh()
