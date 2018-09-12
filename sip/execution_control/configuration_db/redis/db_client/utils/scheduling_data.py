# coding=utf-8
"""Execution Control Scheduling Data Model resources API.

This module is used by the Processing Controller Services for interacting with
Scheduling Block Instances, Processing Blocks, and Sub-arrays data models
used to Schedule the SDP processing.
"""
import ast

import redis

from ..events import publish


# TODO(BM) Replace this with the low level config db client.
DB = redis.StrictRedis(decode_responses=True)


# TODO(BM) add other methods from Processing Controller Client
# eg.
# - get_sbi_ids()
# - get_pb_ids()


def get_sbi_key(sbi_id: str) -> str:
    """Return a Scheduling Block Instance db key.

    Args:
        sbi_id (str): Scheduling block instance id

    Returns:
        str, db key for the specified SBI

    """
    return 'sbi:{}'.format(sbi_id)


def get_pb_key(pb_id: str) -> str:
    """Return a Processing Block db key.

    Args:
        pb_id (str): Processing Block instance id

    Returns:
        str, db key for the specified PB

    """
    return 'pb:{}'.format(pb_id)


def add_sbi(sbi_config: dict):
    """Add an SBI to the EC Configuration database.

    Args:
        sbi_config (dict): Scheduling Block Instance configuration dictionary.
    """
    # TODO(BM) Validate dictionary against schema.

    sbi_pb_config = sbi_config['processing_block_data']
    del sbi_config['processing_block_data']

    sbi_key = get_sbi_key(sbi_config['id'])
    sbi_list_key = 'sbi:list'

    # Add Scheduling Block instance configuration to the db
    DB.hmset(sbi_key, sbi_config)
    DB.rpush(sbi_list_key, sbi_key)

    # Publish an event to notify subscribers of the new SBI
    publish('sbi', sbi_key, 'created')

    # Loop over PBs in the SBI and add them to the db
    for _, pb_config in sbi_pb_config.items():

        # Store the SBI key in the PB for back-reference.
        pb_config['sbi_id'] = sbi_key

        pb_key = get_pb_key(pb_config['id'])
        DB.hmset(pb_key, pb_config)
        DB.rpush('pb:list', pb_key)
        DB.rpush('pb:{}'.format(pb_config['type']), pb_key)

        # Publish an event to notify subscribers of the new PB
        publish('pb', pb_key, 'created')


def get_sbi_data_value(sbi_id: str, key: str):
    """Get the value of an SBI data field converted back to a Python type."""
    return ast.literal_eval(DB.hget(get_sbi_key(sbi_id), key))


def set_sbi_status(sbi_id: str, value: str):
    """Set the status of a SBI to the specified value.

    Expected to be called by SBI event handlers.

    Args:
        sbi_id (str): SBI id
        value (str): Status value.

    """
    DB.hset(get_sbi_key(sbi_id), 'status', value)


def cancel_sbi(sbi_id):
    """Cancel a SBI.

    Args:
        sbi_id (str): the SBI Id

    """
    sbi_key = get_sbi_key(sbi_id)
    # TODO(BM) check that the key exists!
    publish('sbi', sbi_key, 'cancelled')

    sbi_pb_ids = get_sbi_data_value(sbi_id, 'processing_block_ids')
    for pb_id in sbi_pb_ids:
        publish('pb', get_pb_key(pb_id), 'cancelled')
