from flask import g
from viewcraft.models.character import Character
from viewcraft.app import application
from viewcraft.models.resource import Resource
from viewcraft.models.rmember import RMember


class Roster(Resource):
    def __init__(self, name):
        self.name = name
        self.members = []
        self.ilvl_average = 0
        self.len = 0

    @property
    def path(self):
        return "roster:{}:{}".format(g["id"], self.name)

    @classmethod
    def from_db(cls, region, server, name, roster="Basic"):
        """
        Get a RMember from the database.
        :return: RMember object instance or None if doesn't exist.
        """
        # TODO Recoder la fonction
        rm = RMember(region, server, name, roster)
        if not g["redis"].exists(rm.path):
            return None
        else:
            rm.character = Character.from_db(region, server, name)
            rm.role = g["redis"].hget(rm.path, "role")
            if not rm.role:
                rm.role = None
            return rm

    def save_db(self):
        """
        Save in Redis the rmember.
        """
        # TODO Recoder la fonction
        g["redis"].hmset("rmember:{}:{}:{}:{}:{}".format(g["id"], self.roster, self.region, self.server, self.name),
                         self.__dict__)
        if not g["redis"].exists("character:{}:{}:{}".format(self.region, self.server, self.name)):
            char = Character.create(self.region, self.server, self.name)
            char.refresh()
        if not g["redis"].exists("roster:{}:{}".format(g["id"], self.roster)):
            pass

    @classmethod
    def create(cls, name="Basic"):
        """
        Create a Roster.
        :param name:  Roster Name
        :return: Roster object created.
        """
        roster = Roster(name)
        roster.refresh()
        return roster

    def refresh(self):
        """
        Refresh all data about the roster.
        """
        # TODO Recoder
        if not self.character:
            self.character = Character.from_db(self.region, self.server, self.name)
            if not self.character:
                self.character = Character.create(self.region, self.server, self.name)
        self.character.refresh()

    def delete(self):
        """
        Delete the Roster.
        Delete all rmember of this roster.
        """
        for member in self.members:
            g["redis"].delete("rmember:{}:{}:{}:{}:{}".format(g["id"], member.roster,
                                                              member.region, member.server,
                                                              member.name))
        g["redis"].delete("{}:member".format(self.path))
        g["redis"].delete(self.path)
