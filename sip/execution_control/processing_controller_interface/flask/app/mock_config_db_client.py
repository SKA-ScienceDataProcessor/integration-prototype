# -*- coding: utf-8 -*-
"""Mock Client for the Redis Configuration Database.

This is provides functions for testing the Processing Controller (Interface)
"""
import json
import os
import ast

import redis
import jsonschema
import re


# Get Redis database object
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_DB_ID = os.getenv('REDIS_DB_ID', 0)
POOL = redis.ConnectionPool(host=REDIS_HOST, db=REDIS_DB_ID,
                            decode_responses=True)
DB = redis.StrictRedis(connection_pool=POOL)


# #############################################################################
# Utility functions
# #############################################################################


def load_schema(path):
    """Loads a JSON schema file."""
    with open(path) as json_data:
        schema = json.load(json_data)
    return schema


def clear_db():
    """Clear the entire db."""
    cursor = '0'
    while cursor != 0:
        cursor, keys = DB.scan(cursor, match='*', count=5000)
        if keys:
            DB.delete(*keys)


# #############################################################################
# Scheduling Block functions
# #############################################################################


def get_scheduling_block_ids():
    """Return list of scheduling block IDs"""
    ids = [key.split('/')[-1]
           for key in DB.keys(pattern='scheduling_block/*')]
    return sorted(ids)


def get_num_scheduling_blocks():
    """Return the number of scheduling blocks"""
    return len(DB.keys(pattern='scheduling_block/*'))


def add_scheduling_block(config):
    """Add a Scheduling Block to the Configuration Database.

    The configuration dictionary must match the schema defined in
    in the schema_path variable at the top of the function.

    Args:
        config (dict): Scheduling Block instance request configuration.
    """

    schema_path = os.path.join(os.path.dirname(__file__),
                               'scheduling_block_list', 'post_request.json')
    schema = load_schema(schema_path)
    jsonschema.validate(config, schema)

    # Add the scheduling block to the database
    # (This is done as a single k/v pair here but would probably be
    #  expanded to a set of keys in the actual implementation)
    DB.set('scheduling_block/{}'.format(config['id']), json.dumps(config))

    # Add a event to the scheduling block event list to notify
    # of a new scheduling block being added to the db.
    DB.rpush('scheduling_block_events',
             json.dumps(dict(type="created", id=config["id"])))


def delete_scheduling_block(block_id):
    """Delete Scheduling Block with the specified ID"""
    DB.delete('scheduling_block/{}'.format(block_id))

    # Add a event to the scheduling block event list to notify
    # of a deleting a scheduling block from the db
    DB.rpush('scheduling_block_events',
             json.dumps(dict(type="deleted", id=block_id)))


def get_scheduling_block(block_id):
    """Return the Scheduling Block configuration for a specified ID"""
    config = json.loads(DB.get('scheduling_block/{}'.format(block_id)))
    return config


def get_scheduling_block_event():
    """Return the latest Scheduling Block event"""
    event = DB.rpoplpush('scheduling_block_events',
                         'scheduling_block_event_history')
    if event:
        event = json.loads(event.decode('utf-8'))
    return event


# #############################################################################
# Processing Block functions
# #############################################################################


def get_processing_block_ids():
    """Return an array of Processing Block ids"""
    ids = []
    for key in sorted(DB.keys(pattern='scheduling_block/*')):
        config = json.loads(DB.get(key))
        for processing_block in config['processing_blocks']:
            ids.append(processing_block['id'])
    return ids


def get_processing_block(block_id):
    """Return the Processing Block Configuration for the specified ID"""
    identifiers = block_id.split(':')
    scheduling_block_id = identifiers[0]
    scheduling_block_config = get_scheduling_block(scheduling_block_id)
    for processing_block in scheduling_block_config['processing_blocks']:
        if processing_block['id'] == block_id:
            return processing_block
    raise KeyError('Unknown Processing Block id: {} ({})'
                   .format(identifiers[-1], block_id))


def delete_processing_block(processing_block_id):
    """Delete Processing Block with the specified ID"""
    scheduling_block_id = processing_block_id.split(':')[0]
    config = get_scheduling_block(scheduling_block_id)
    processing_blocks = config.get('processing_blocks')
    processing_block = list(filter(lambda x: x.get('id') == processing_block_id,
                            processing_blocks))[0]
    config['processing_blocks'].remove(processing_block)
    DB.set('scheduling_block/{}'.format(config['id']), json.dumps(config))

    # Add a event to the scheduling block event list to notify
    # of a new scheduling block being added to the db.
    DB.rpush('processing_block_events',
             json.dumps(dict(type="deleted", id=processing_block_id)))


def get_processing_block_event():
    """Return the latest Processing Block event"""
    event = DB.rpoplpush('processing_block_events',
                         'processing_block_event_history')
    if event:
        event = json.loads(event.decode('utf-8'))
    return event


