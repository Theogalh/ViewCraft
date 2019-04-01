from init import g
from models.character import Character
import time


class RMember:
    def __init__(self, region, server, name, roster, role=None):
        self.name = name
        self.role = role
        self.roster = roster
        self.server = server
        self.region = region
        self.character = None

    @property
    def path(self):
        return "rmember:{}:{}:{}:{}:{}".format(g["id"], self.roster, self.region, self.server, self.name)

    @property
    def ilvl(self):
        try:
            return self.character.ilvl
        except AttributeError:
            return None

    @classmethod
    def from_db(cls, region, server, name, roster="Basic"):
        """
        Get a RMember from the database.
        :return: RMember object instance or None if doesn't exist.
        """
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
        # TODO Remplacer le dict par les properties.
        g["redis"].hmset("rmember:{}:{}:{}:{}:{}".format(g["id"], self.roster, self.region, self.server, self.name),
                         self.__dict__)
        if not g["redis"].exists("character:{}:{}:{}".format(self.region, self.server, self.name)):
            char = Character.create(self.region, self.server, self.name)
            char.refresh()
        if not g["redis"].exists("roster:{}:{}".format(g["id"], self.roster)):
            g["redis"].hset("roster:{}:{}".format(g["id"], self.roster), "created_time", int(time.time()))
            g["redis"].sadd("roster:{}:{}".format(g["id"], self.roster), self.path)

    @classmethod
    def create(cls, region, server, name, roster="Basic"):
        """
        Create a new RMember and save it in DB.
        Create a Character if doesn't exist in DB.
        Create a Roster if doesn't exist in DB.
        Raise AttributeError if character doesnt exists.
        :param region: Character Region
        :param server: Character Realm
        :param name:  Character Name
        :param roster: Roster Name
        :return: Rmember object created.
        """
        rm = RMember(region, server, name, roster)
        try:
            rm.refresh()
        except AttributeError:
            raise AttributeError("Character not found")
        if not g["redis"].exists("roster:{}:{}".format(g["id"], roster)):
            g["redis"].hset("roster:{}:{}".format(g["id"], roster), {"name": roster})
            g["redis"].sadd("roster:{}:{}:members".format(g["id"], roster), rm.path)
        return rm

    def refresh(self):
        """
        Refresh all data about the rmember.
        Raise AttributeError if guild character exists.
        """
        if not self.character:
            self.character = Character.from_db(self.region, self.server, self.name)
            if not self.character:
                self.character = Character.create(self.region, self.server, self.name)
        try:
            self.character.refresh()
        except AttributeError as e:
            raise AttributeError(e)

    def delete(self):
        """
        Delete the RMember.
        Delete his entry on the roster. And decremente the len of him.
        :return:
        """
        g["redis"].srem("roster:{}:{}:members".format(g["id"], self.roster), self.path)
        g["redis"].delete(self.path)
