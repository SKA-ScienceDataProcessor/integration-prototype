# -*- coding: utf-8 -*-
"""Low Level Configuration Service Client API"""

import os
from functools import wraps
import logging

import redis
import redis.exceptions


LOG = logging.getLogger('SIP.EC.PCI.DB')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_DB_ID = os.getenv('REDIS_DB_ID', '0')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')


def check_connection(func):
    """Decorator to check connection exceptions"""
    @wraps(func)
    def with_exception_handling(*args, **kwargs):
        """Wrapper to check for connection failures"""
        try:
            return func(*args, **kwargs)
        except redis.exceptions.ConnectionError:
            raise ConnectionError("Unable to connect to the Redis "
                                  "Configuration Database. host = {}, "
                                  "port = {}, id = {}."
                                  .format(REDIS_HOST, REDIS_PORT, REDIS_DB_ID))
    return with_exception_handling


class ConfigDB:
    """Low level Configuration Database client"""

    def __init__(self):
        """ Create a connection to a configuration database"""
        LOG.debug("Creating connection pool with host = [%s], id = [%s], "
                  "port= %s", REDIS_HOST, REDIS_DB_ID, REDIS_PORT)
        pool = redis.ConnectionPool(host=REDIS_HOST, db=REDIS_DB_ID,
                                    port=REDIS_PORT, decode_responses=True)
        self._db = redis.StrictRedis(connection_pool=pool)

    def set_specified_values(self, name, value):
        """Sets specified fields to their respective values in the
        has stored at key"""
        self._db.hmset(name, value)

    def set_value(self, key, field, value):
        """Add the state of the key and field"""
        self._db.hset(key, field, value)

    def get_specified_values(self, key, field):
        """Get all the values associated with the
        specified fields in the hash stored at key"""
        pass

    def get_value(self, key, field):
        """Get the value associated with the key and field"""
        return self._db.hget(key, field)

    def get_all_field_value(self, key):
        """Get all the fields and values stored at key"""
        return self._db.hgetall(key)

    def get_list(self, key):
        """Get all the value in the list"""
        return self._db.lrange(key, 0, -1)

    def get_element(self, key, index):
        """Get an element from a list by its index
        Returns the element at index in the list stored at key"""
        return self._db.lindex(key, index)

    def get_length(self, key):
        """Get the length of the list stored at key"""
        return self._db.llen(key)

    def add_element(self, key, element):
        """Adds a new element to the end of the list"""
        self._db.lpush(key, element)

    def delete_block(self, key):
        """Delete key"""
        self._db.delete(key)

    def get_all_blocks(self, block_id):
        """Search all keys associated with the block id"""
        key_search = '*' + block_id + '*'
        return self._db.keys(key_search)

    @check_connection
    def get_block(self, block_id):
        """Search for keys associated with the block id"""
        key_search = '*' + block_id
        return self._db.keys(key_search)

    def push_event(self, event_name, event_type, block_id):
        """Push inserts all the specified values at the tail of the list
        stored at the key"""
        self._db.rpush(event_name, dict(type=event_type, id=block_id))

    def get_event(self, block_event, block_history):
        """Removes the last element of the list stored at the source,
        and pushes the element at the first element of the list stored
        at destination"""
        return self._db.rpoplpush(block_event, block_history)

    @check_connection
    def get_ids(self, pattern):
        """Search for the key according to the pattern"""
        return self._db.keys(pattern)

    def flush_db(self):
        """Clear the entire database"""
        self._db.flushdb()
