from datetime import time
from viewcraft.utils import database_required
from flask import g


class Resource(object):

    def __init__(self, name):
        """
        Init function
        """

        self.id = name
        self._creation_time = time()
        self._modification_time = self._creation_time
        self._properties = {}

    @classmethod
    @database_required
    def from_db(cls, name):
        """
        Get a resource from db.
        :param name:
        :return:
        """
        res = cls(name)
        if not g.redis.exists(res.path):
            return None
        rdata = g.redis.hgetall(res.path)
        for data in rdata:
            try:
                if rdata[data] == 'True':
                    rdata[data] = True
                elif rdata[data] == 'False':
                    rdata[data] = False
                getattr(res, data)
                setattr(res, data, rdata[data])
            except (AttributeError, TypeError):
                res.property_add(data,
                                 rdata[data])
                continue
        return res

    @database_required
    def save_db(self):
        """
        Save the resource into the db.
        :return:
        """
        rdata = self.properties
        rdata.update({'creation_time': self.creation_time,
                      'modification_time': self.modification_time,
                      'uuid': str(self.uuid)})
        g.redis.hmset(self.path, rdata)
        for prop in g.redis.hgetall(self.path):
            if prop not in rdata:
                g.redis.hdel(self.path, prop)

    @database_required
    def delete_db(self):
        """
        Remove an element from the db.
        :return:
        """
        g.redis.delete(self.path)

    def property_add(self, rproperty, value):
        if rproperty in self._properties:
            raise ValueError
        self._properties[rproperty] = str(value)

    def property_del(self, rproperty):
        try:
            del self._properties[rproperty]
        except KeyError:
            pass

    def property_set(self, rproperty, value):
        try:
            self._properties[rproperty] = str(value)
            self._modification_time = time()
        except ValueError:
            raise

    @property
    def creation_time(self):
        return self._creation_time

    @creation_time.setter
    def creation_time(self, creation_time):
        self._creation_time = float(creation_time)

    @property
    def modification_time(self):
        return self._modification_time

    @modification_time.setter
    def modification_time(self, modification_time):
        self._modification_time = float(modification_time)

    @property
    def path(self):
        return ''

    @property
    def properties(self):
        return self._properties
