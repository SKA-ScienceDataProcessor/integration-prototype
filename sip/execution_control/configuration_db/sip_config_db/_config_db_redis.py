# -*- coding: utf-8 -*-
"""Low-level Configuration Database API using Redis."""
import logging
import os
from functools import wraps

import redis
import redis.exceptions

LOG = logging.getLogger('SIP.EC.CDB')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB_ID = os.getenv('REDIS_DB_ID', '0')


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


def flush_db():
    """Flush (clear) the database."""
    ConfigDb().flush_db()


class ConfigDb:
    """Low level Configuration Database client."""

    def __init__(self):
        """Create a connection to a configuration database."""
        LOG.debug("Creating connection pool with host = [%s], id = [%s], "
                  "port= %s", REDIS_HOST, REDIS_DB_ID, REDIS_PORT)
        pool = redis.ConnectionPool(host=REDIS_HOST, db=REDIS_DB_ID,
                                    port=REDIS_PORT, decode_responses=True)
        self._db = redis.StrictRedis(connection_pool=pool)
        self._pipeline = self._db.pipeline()

    @check_connection
    def get_value(self, key):
        """Get the value of the key.

        Args:
            key (str):  key (name) where the value is stored

        """
        return self._db.get(key)

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

    @check_connection
    def get_hash_values(self, key, fields):
        """Get values from the specified fields from the hash stored at key.

        Args:
            key (str): key (name) of the hash.
            fields (list): List of fields (keys) in the hash to return.

        Returns:
            list: List of hash field values in the order specified by fields.

        """
        return self._db.hmget(key, fields)

    @check_connection
    def set_hash_value(self, key, field, value, pipeline=False):
        """Set the value of field in a hash stored at key.

        Args:
            key (str): key (name) of the hash
            field (str): Field within the hash to set
            value: Value to set
            pipeline (bool): True, start a transaction block. Default false.

        """
        if pipeline:
            self._pipeline.hset(key, field, value)
        else:
            self._db.hset(key, field, value)

    @check_connection
    def get_hash_value(self, key, field):
        """Get the value of a field within a hash stored at key.

        Args:
            key (str): key (name) of the hash
            field (str): field of the value in the hash being retrieved.

        Returns:
            str: Value of the field within the hash.

        """
        return self._db.hget(key, field)

    @check_connection
    def get_hash_dict(self, key):
        """Get all the fields and values stored in the hash at key.

        Args:
            key (str): Key (name) of the hash.

        Returns:
            dict: Dictionary of key / values in the hash.

        """
        return self._db.hgetall(key)

    @check_connection
    def prepend_to_list(self, key, *value, pipeline=False):
        """Add new element to the start of the list stored at key.

        Args:
            key (str): Key where the list is stored
            value: Value to add to the list
            pipeline (bool): True, start a transaction block. Default false.

        """
        if pipeline:
            self._pipeline.lpush(key, *value)
        else:
            self._db.lpush(key, *value)

    @check_connection
    def append_to_list(self, key, *value, pipeline=False):
        """Add new element to the end of the list stored at key.

        Args:
            key (str): Key where the list is stored
            value: Value to add to the list
            pipeline (bool): True, start a transaction block. Default false.

        """
        if pipeline:
            self._pipeline.rpush(key, *value)
        else:
            self._db.rpush(key, *value)

    @check_connection
    def get_list_value(self, key, index):
        """Get an element from a list by its index.

        Args:
            key (str): Key where the list is stored
            index (int): Index of the value in the list to return.

        Returns:
            str: the value at index in the list stored at key

        """
        return self._db.lindex(key, index)

    @check_connection
    def get_list(self, key, pipeline=False):
        """Get all the value in the list stored at key.

        Args:
            key (str): Key where the list is stored.
            pipeline (bool): True, start a transaction block. Default false.

        Returns:
            list: values in the list ordered by list index

        """
        if pipeline:
            return self._pipeline.lrange(key, 0, -1)

        return self._db.lrange(key, 0, -1)

    @check_connection
    def get_list_length(self, key):
        """Get the length of the list stored at key.

        Args:
            key (str): Key where the list is stored

        Returns:
            int: Length of the list stored at key.

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

    @check_connection
    def delete(self, *names: str, pipeline=False):
        """Delete one or more keys specified by names.

        Args:
            names (str): Names of keys to delete
            pipeline (bool): True, start a transaction block. Default false.
        """
        if pipeline:
            self._pipeline.delete(*names)
        else:
            self._db.delete(*names)

    @check_connection
    def key_exists(self, key):
        """Check if a key exists in the database.

        Args:
            key (str): Key to check

        Returns:
            bool: True if key exists, else false.

        """
        return self._db.exists(key)

    @check_connection
    def push_event(self, event_name, event_type, block_id):
        """Add an event to the database.

        An event is a list entry stored at a list with key event_name.
        The list entry is a dictionary with two fields: event_type and block_id

        Args:
            event_name (str): Event list key.
            event_type (str): Event type field
            block_id (str): Event block Id field
        """
        self._db.rpush(event_name, dict(type=event_type, id=block_id))

    @check_connection
    def get_event(self, event_name, event_history=None):
        """Get an event from the database.

        Gets an event from the named event list removing the event and
        adding it to the event history.

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
    def pub_sub(self, **kwargs):
        """Subscribe to channels and listen for messages that get published.

        Args:
            kwargs: Channels to subscribe

        Returns:
            list: list of channels and number of subscribers

        """
        pub_sub = self._db.pubsub(**kwargs)
        return pub_sub

    @check_connection
    def remove_from_list(self, key: str, value, count: int = 0,
                         pipeline: bool = False):
        """Remove specified value(s) from the list stored at key.

        Args:
            key (str): Key where the list is stored.
            value: value to remove
            count (int): Number of entries to remove, default 0 == all
            pipeline(bool): If True, start a transaction block. Default False.

        """
        if pipeline:
            self._pipeline.lrem(key, count, value)
        else:
            self._db.lrem(key, count, value)

    @check_connection
    def execute(self):
        """Execute queued commands.

        Executes all previous queued commands in a transaction and restores
        the connection state to normal.

        """
        self._pipeline.execute()

    @check_connection
    def watch(self, key, pipeline=False):
        """Watch the given key.

        Marks the given key to be watch for conditional execution
        of a transaction.

        Args:
            key (str): Key that needs to be watched
            pipeline (bool): True, start a transaction block. Default false.

        """
        if pipeline:
            self._pipeline.watch(key)
        else:
            self._db.watch(key)

    @check_connection
    def publish(self, channel, message, pipeline=False):
        """Post a message to a given channel.

        Args:
            channel (str): Channel where the message will be published
            message (str): Message to publish
            pipeline (bool): True, start a transaction block. Default false.

        """
        if pipeline:
            self._pipeline.publish(channel, message)
        else:
            self._db.publish(channel, message)

    @check_connection
    def increment(self, key):
        """Increment the number stored a key by one.

        Args:
            key (str): Key where the list is stored

        """
        self._db.incr(key)

    @check_connection
    def flush_db(self):
        """Clear the entire database.

        *Warning* Use with care!
        """
        self._db.flushdb()
