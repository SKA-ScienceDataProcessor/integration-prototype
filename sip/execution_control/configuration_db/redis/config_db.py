# -*- coding: utf-8 -*-
"""Low Level Configuration Service Client API"""

import os
import redis

class configDB():
    """ Configuration Client Interface"""
    def __init__(self):
        """ Create a connection to a configuration database"""
        # Get Redis database object
        REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
        REDIS_DB_ID = os.getenv('REDIS_DB_ID', 0)
        POOL = redis.ConnectionPool(host=REDIS_HOST, db=REDIS_DB_ID,
                                    decode_responses=True)
        self._db = redis.StrictRedis(connection_pool=POOL)

    def get_hash(self, key, field):
        """Get the value associated with the key and field"""
        value = self._db.hget(key, field)
        return value

    def get_hash_all(self, key):
        """Get all the field and value in the key"""
        value_all = self._db.hgetall(key)
        return value_all

    def get_field(self, key):
        """ """
        field = self._db.hget(key)
        return field

    def get_list(self, key):
        """Get all the value in the list"""
        list = self._db.lrange(key, 0, -1)
        return list

    def get_element(self, key, index):
        """Get an element from a list by its index
        Returns the element at index in the list stored at key"""
        element = self._db.lindex(key, index)
        return element

    def get_length(self, key):
        """Get the length of a list"""
        len = self._db.llen(key)
        return len

    def set_value(self, key, field, value):
        """Add the state of the key and field"""
        self._db.hset(key, field, value)

    def add_element(self, key, element):
        """Adds a new element to the end of the list"""
        self._db.lpush(key, element)

    def delete_key(self, key):
        """Delete key"""
        self._db.delete(key)



