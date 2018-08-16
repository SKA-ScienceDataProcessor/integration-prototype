# coding=utf-8
"""Scheduling Block Instance (SBI) Events."""
import ast

import redis

from typing import List

from . import events
from . import pb
from .data_keys import get_sbi_key, get_pb_key

AGGREGATE_TYPE = 'sbi'
DB = redis.StrictRedis(decode_responses=True)


def subscribe(subscriber: str) -> events.EventQueue:
    """Subscribe to Scheduling Block Instance (SBI) events.

    Args:
        subscriber (str): Subscriber name.

    Returns:
        events.EventQueue, Event queue object for querying PB events.

    """
    return events.subscribe(AGGREGATE_TYPE, subscriber)


def get_subscribers() -> List[str]:
    """Get the list of subscribers to Scheduling Block Instance (SBI) events.

    Returns:
        List[str], list of subscriber names.

    """
    return events.get_subscribers(AGGREGATE_TYPE)


def publish(sbi_key: str, event_type: str, event_data: dict = None):
    """Publish a SBI event.

    Args:
        sbi_key (str): Key of the SBI.
        event_type (str): Type of event.
        event_data (dict, optional): Event data.

    """
    events.publish(AGGREGATE_TYPE, sbi_key, event_type, event_data)


def cancel_sbi(sbi_id):
    """Cancel a SBI.

    Args:
        sbi_id (str): the SBI Id

    """
    sbi_key = get_sbi_key(sbi_id)
    # TODO(BM) check that the key exists!

    publish(sbi_key, 'cancelled')

    sbi_pb_ids = get_sbi_data_value(sbi_id, 'processing_block_ids')
    for pb_id in sbi_pb_ids:
        pb.publish(get_pb_key(pb_id), 'cancelled')


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
    publish(sbi_key, 'created')

    # Loop over PBs in the SBI and add them to the db
    for _, pb_config in sbi_pb_config.items():

        # Store the SBI key in the PB for back-reference.
        pb_config['sbi_id'] = sbi_key

        pb_key = get_pb_key(pb_config['id'])
        DB.hmset(pb_key, pb_config)
        DB.rpush('pb:list', pb_key)
        DB.rpush('pb:{}'.format(pb_config['type']), pb_key)

        # Publish an event to notify subscribers of the new PB
        pb.publish(pb_key, 'created')


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
