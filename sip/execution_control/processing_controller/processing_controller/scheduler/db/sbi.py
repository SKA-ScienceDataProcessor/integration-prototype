# coding=utf-8
"""Scheduling Block Instance (SBI) data and events API.

TODO(BM): Consider having a SBI class so that we have an object for the \
          SBI that can be manipulated.

TODO(BM): Define event types or event objects that the SBI can have.
"""
import ast

import redis

import json

from typing import List

from . import events
from . import pb
from .event_keys import aggregate_events_data, aggregate_events_list


AGGREGATE_TYPE = 'sbi'
DB = redis.StrictRedis(decode_responses=True)


def get_key(sbi_id: str) -> str:
    """Return a Scheduling Block Instance db key.

    Args:
        sbi_id (str): Scheduling block instance id

    Returns:
        str, db key for the specified SBI

    """
    return '{}:{}'.format(AGGREGATE_TYPE, sbi_id)


def get_event_data_key(sbi_id: str) -> str:
    """Return the SBI events data db key.

    Args:
        sbi_id (str): SBI id.

    Returns:
        str, db key for the specified SBI event data.

    """
    return aggregate_events_data(get_key(sbi_id))


def get_event_list_key(sbi_id: str) -> str:
    """Return the SBI events list db key.

    Args:
        sbi_id (str): SBI id.

    Returns:
        str, db key for the specified SBI event data.

    """
    return aggregate_events_list(get_key(sbi_id))


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


def publish(sbi_id: str, event_type: str, event_data: dict = None):
    """Publish a SBI event.

    Args:
        sbi_id (str): SBI id.
        event_type (str): Type of event.
        event_data (dict, optional): Event data.

    """
    events.publish(AGGREGATE_TYPE, sbi_id, event_type, event_data)


def cancel(sbi_id: str):
    """Cancel a SBI.

    Args:
        sbi_id (str): the SBI Id

    """
    # sbi_key = get_sbi_key(sbi_id)
    # TODO(BM) check that the key exists!

    # TODO(BM) ideally publish the cancel event and update the sbi and pb \
    # lists in one atomic transaction (using pipelines)
    publish(sbi_id, 'cancelled')
    DB.lrem('{}:active'.format(AGGREGATE_TYPE), 0, sbi_id)
    DB.rpush('{}:cancelled'.format(AGGREGATE_TYPE), sbi_id)
    sbi_pb_ids = get_config_value(sbi_id, 'processing_block_ids')
    for pb_id in sbi_pb_ids:
        pb.cancel(pb_id)


def add(sbi_config: dict):
    """Add an SBI to the EC Configuration database.

    Args:
        sbi_config (dict): Scheduling Block Instance configuration dictionary.
    """
    # TODO(BM) Validate dictionary against schema.

    sbi_pb_config = sbi_config['processing_block_data']
    del sbi_config['processing_block_data']

    sbi_id = sbi_config['id']
    sbi_key = get_key(sbi_config['id'])
    sbi_list_key = '{}:active'.format(AGGREGATE_TYPE)

    # Add Scheduling Block instance configuration to the db
    DB.hmset(sbi_key, sbi_config)
    DB.rpush(sbi_list_key, sbi_config['id'])

    # Publish an event to notify subscribers of the new SBI
    publish(sbi_id, 'created')

    # Loop over PBs in the SBI and add them to the db
    for _, pb_config in sbi_pb_config.items():

        pb_id = pb_config['id']

        # Store the SBI key in the PB for back-reference.
        pb_config['sbi_id'] = sbi_key

        pb_key = pb.get_key(pb_id)
        DB.hmset(pb_key, pb_config)
        DB.rpush('{}:active'.format(pb.AGGREGATE_TYPE), pb_id)
        DB.rpush('{}:active:{}'.format(pb.AGGREGATE_TYPE, pb_config['type']),
                 pb_id)

        # Publish an event to notify subscribers of the new PB
        pb.publish(pb_id, 'created')


def get_active():
    """Get the list of active SBI from the database.

    Returns:
        list, SBI ids

    """
    return DB.lrange('{}:active'.format(AGGREGATE_TYPE), 0, -1)


def get_cancelled():
    """Get the list of cancelled SBI from the database.

    Returns:
        list, SBI ids

    """
    return DB.lrange('{}:cancelled'.format(AGGREGATE_TYPE), 0, -1)


def get_completed():
    """Get the list of completed SBI from the database.

    Returns:
        list, SBI ids

    """
    return DB.lrange('{}:completed'.format(AGGREGATE_TYPE), 0, -1)


def get_config(sbi_id: str) -> dict:
    """Get the data structure for an SBI.

    Args:
        sbi_id (str): SBI id

    Returns:
        dict,

    """
    data = DB.hgetall(get_key(sbi_id))
    # Attempt to convert data fields to python types.
    for key, value in data.items():
        try:
            data[key] = ast.literal_eval(value)
        except SyntaxError:
            pass
        except ValueError:
            pass
    return data


def get_status(sbi_id: str) -> str:
    """Get the status of an SBI.

    TODO(BM) Could use an event handler to update the status of the aggregate
             and then query the aggregate (rather than using the event stream
             here). This option would probably be more scalable and allow
             more complicated logic.

    Args:
        sbi_id (str): SBI id.

    Returns:
        str,

    """
    # FIXME(BM) check the SBI key exists.
    # FIXME(BM) use the events API for this?
    key = get_event_list_key(sbi_id)
    last_event = DB.hget(get_event_data_key(sbi_id), DB.lindex(key, -1))
    last_event = ast.literal_eval(last_event)
    return last_event['type']


def get_config_value(sbi_id: str, key: str):
    """Get the value of an SBI data field converted back to a Python type."""
    return ast.literal_eval(DB.hget(get_key(sbi_id), key))


def get_pb_ids(sbi_id: str) -> List[str]:
    """Return the list of PB ids associated with the SBI.

    Args:
        sbi_id (str): SBI id

    Returns:
        list,

    """
    # TODO(BM) move this hardcoded key to a function?
    key = 'processing_block_ids'
    return ast.literal_eval(DB.hget(get_key(sbi_id), key))
