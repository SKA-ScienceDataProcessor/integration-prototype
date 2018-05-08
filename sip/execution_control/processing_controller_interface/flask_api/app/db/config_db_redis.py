# -*- coding: utf-8 -*-
"""Low Level Configuration Service Client API"""

import os
import redis


class ConfigDB:
    """Configuration Client Interface"""

    def __init__(self):
        """Create a connection to a configuration database"""
        # Get Redis database object
        host = os.getenv('REDIS_HOST', 'localhost')
        db = os.getenv('REDIS_DB_ID', 0)
        pool = redis.ConnectionPool(host=host, db=db, decode_responses=True)
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
        print("Placeholder")
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

    # TODO(NJT): Might be better to combine the two functions or have a third function
    def get_all_blocks(self, block_id):
        """Search all keys associated with the block id"""
        key_search = '*' + block_id + '*'
        if key_search:
            keys = self._db.keys(key_search)
        return keys  # FIXME(BM) keys can be never assigned!

    def get_block(self, block_id):
        """Search for keys associated with the block id"""
        key_search = '*' + block_id
        if key_search:
            key = self._db.keys(key_search)
        return key  # FIXME(BM) key can be never assigned!

    def push_event(self, event_name, type, block_id):
        """Push inserts all the specified values at the tail of the list
        stored at the key"""
        self._db.rpush(event_name, dict(type=type, id=block_id))

    def get_event(self, block_event, block_history):
        """Removes the last element of the list stored at the source,
        and pushes the element at the first element of the list stored
        at destination"""
        print(block_event)
        print(block_history)
        event = self._db.rpoplpush(block_event, block_history)
        if event:
            return event

    def flush_db(self):
        """Deletes all the data in the database"""
        self._db.flushdb()

    def get_ids(self, pattern):
        return self._db.keys(pattern)

    def clear(self):
        """Clear the entire database."""
        _db = self._db
        cursor = '0'
        while cursor != 0:
            cursor, keys = _db.scan(cursor, match='*', count=5000)
            if keys:
                _db.delete(*keys)
