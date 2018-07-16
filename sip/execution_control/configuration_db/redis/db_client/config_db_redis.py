# -*- coding: utf-8 -*-
"""Low Level Configuration Service Client API."""
import os
from functools import wraps
import logging

import redis
import redis.exceptions

LOG = logging.getLogger('SIP.EC.CDB')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB_ID = os.getenv('REDIS_DB_ID', 0)


def check_connection(func):
    """Check connection exceptions."""
    @wraps(func)
    def with_exception_handling(*args, **kwargs):
        """Wrap function being decorated."""
        try:
            return func(*args, **kwargs)
        except redis.exceptions.ConnectionError:
            raise ConnectionError("Unable to connect to the Redis "
                                  "Configuration Database. host = {}, "
                                  "port = {}, id = {}."
                                  .format(REDIS_HOST, REDIS_PORT,
                                          REDIS_DB_ID))
    return with_exception_handling


class ConfigDbRedis:
    """Low level Configuration Database client."""

    def __init__(self):
        """Create a connection to a configuration database."""
        LOG.debug("Creating connection pool with host = [%s], id = [%s], "
                  "port= %s", REDIS_HOST, REDIS_DB_ID, REDIS_PORT)
        pool = redis.ConnectionPool(host=REDIS_HOST, db=REDIS_DB_ID,
                                    port=REDIS_PORT, decode_responses=True)
        self._db = redis.StrictRedis(connection_pool=pool)

    @check_connection
    def set_hash_values(self, key, fields):
        """Set key/value fields in the Redis hash stored at key.

        A Redis Hash (see https://redis.io/topics/data-types) is a data type
        which represents a mapping between string fields and string values.

        Keys and values are taken from the fields dictionary.

        Args:
            key (str): Key (name) of the hash
            fields (dict): Key / value fields in the hash to set.

        """
        self._db.hmset(key, fields)

    def get_hash_values(self, key, fields):
        """Get values from the specified fields from the hash stored at key.

        Args:
            key (str): key (name) of the hash.
            fields (list): List of fields (keys) in the hash to return.

        Returns:
            list: List of hash field values in the order specified by fields.

        """
        return self._db.hmget(key, fields)

    def set_hash_value(self, key, field, value):
        """Set the value of field in a hash stored at key.

        Args:
            key (str): key (name) of the hash
            field (str): Field within the hash to set
            value (str): Value to set

        """
        self._db.hset(key, field, value)

    def get_hash_value(self, key, field):
        """Get the value of a field within a hash stored at key.

        Args:
            key (str): key (name) of the hash
            field (str): field of the value in the hash being retrieved.

        Returns:
            str: Value of the field within the hash.

        """
        return self._db.hget(key, field)

    def get_hash_dict(self, key):
        """Get all the fields and values stored in the hash at key.

        Args:
            key (str): Key (name) of the hash.

        Returns:
            dict: Dictionary of key / values in the hash.

        """
        return self._db.hgetall(key)

    def prepend_to_list(self, key, value):
        """Add new element to the start of the list stored at key.

        Args:
            key (str): Key where the list is stored
            value: Value to add to the list
        """
        self._db.lpush(key, value)

    def append_to_list(self, key, value):
        """Add new element to the end of the list stored at key.

        Args:
            key (str): Key where the list is stored
            value: Value to add to the list
        """
        self._db.rpush(key, value)

    def get_list_value(self, key, index):
        """Get an element from a list by its index.

        Args:
            key (str): Key where the list is stored
            index (int): Index of the value in the list to return.

        Returns:
            str: the value at index in the list stored at key

        """
        return self._db.lindex(key, index)

    def get_list(self, key):
        """Get all the value in the list stored at key.

        Args:
            key (str): Key where the list is stored.

        Returns:
            list: values in the list ordered by list index

        """
        return self._db.lrange(key, 0, -1)

    def get_list_length(self, key):
        """Get the length of the list stored at key.

        Args:
            key (str): Key where the list is stored

        Returns:
            int: length of the list stored at key.

        """
        return self._db.llen(key)

    @check_connection
    def get_keys(self, pattern):
        """Search for the key according to the pattern.

        For details on pattern matching see: https://redis.io/commands/keys

        Args:
            pattern (str): Glob style pattern used to search for keys.

        Returns:
            list: List of keys matching the pattern.

        """
        return self._db.keys(pattern)

    def delete_key(self, key):
        """Delete a key in the database (and associated values).

        Args:
            key (str): Key to delete
        """
        self._db.delete(key)

    def key_exists(self, key):
        """Check if a key exists in the database.

        Args:
            key (str): Key to check

        Returns:
            bool: True if key exists, else false.

        """
        return self._db.exists(key)

    def get_all_blocks(self, block_id):
        """Search all keys associated with the block id.

        FIXME(BM): This function should probably be moved to the
                   Processing Controller client

        """
        key_search = '*' + block_id + '*'
        return self._db.keys(key_search)

    @check_connection
    def get_block(self, block_id):
        """Search for keys associated with the block id.

        FIXME(BM): This function should probably be moved to the
            Processing Controller client
        """
        key_search = '*' + block_id
        return self._db.keys(key_search)

    def push_event(self, event_name, event_type, block_id):
        """Add an event to the database.

        An event is a list entry stored at a list with key event_name.
        The list entry is a dictionary with two fields: event_type and block_id

        FIXME(BM): This function needs to be generalised or added to the
            Processing Controller client.

        Args:
            event_name (str): Event list key.
            event_type (str): Event type field
            block_id (str): Event block Id field
        """
        self._db.rpush(event_name, dict(type=event_type, id=block_id))

    def get_event(self, event_name, event_history=None):
        """Get an event from the database.

        Gets an event from the named event list removing the event and
        adding it to the event history.

        FIXME(BM): This function needs to be generalised or added to the
            Processing Controller client.

        Args:
            event_name (str): Event list key.
            event_history (str, optional): Event history list.

        Returns:
            str: string representation of the event object

        """
        if event_history is None:
            event_history = event_name + '_history'
        return self._db.rpoplpush(event_name, event_history)

    @check_connection
    def flush_db(self):
        """Clear the entire database.

        Note:
            Use with care!
        """
        self._db.flushdb()
