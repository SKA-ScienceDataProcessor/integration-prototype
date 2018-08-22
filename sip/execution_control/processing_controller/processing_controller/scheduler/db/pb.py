# coding=utf-8
"""Processing Block (PB) data and event API.

TODO(BM): Consider having a PB class so that we have an object \
          for the PB that can be manipulated.

TODO(BM): Define event types or event objects that the PB can have.

"""
from typing import List

import redis
import ast

from . import events
from .event_keys import aggregate_events_data, aggregate_events_list

DB = redis.StrictRedis(decode_responses=True)
AGGREGATE_TYPE = 'pb'


def get_key(pb_id: str) -> str:
    """Return a Processing Block db key.

    Args:
        pb_id (str): Processing Block instance id

    Returns:
        str, db key for the specified PB

    """
    return '{}:{}'.format(AGGREGATE_TYPE, pb_id)


def get_event_data_key(pb_id: str) -> str:
    """Return the PB events data db key.

    Args:
        pb_id (str): PB id.

    Returns:
        str, db key for the specified PB event data.

    """
    return aggregate_events_data(get_key(pb_id))


def get_event_list_key(pb_id: str) -> str:
    """Return the PB events list db key.

    Args:
        pb_id (str): PB id.

    Returns:
        str, db key for the specified PB event data.

    """
    return aggregate_events_list(get_key(pb_id))


def subscribe(subscriber: str) -> events.EventQueue:
    """Subscribe to Processing Block (PB) events.

    Args:
        subscriber (str): Subscriber name.

    Returns:
        events.EventQueue, Event queue object for querying PB events.

    """
    return events.subscribe(AGGREGATE_TYPE, subscriber)


def get_subscribers() -> List[str]:
    """Get the list of subscribers to Processing Block (PB) events.

    Returns:
        List[str], list of subscriber names.

    """
    return events.get_subscribers(AGGREGATE_TYPE)


def publish(pb_id: str, event_type: str, event_data: dict = None):
    """Publish a PB event.

    Args:
        pb_id (str): ID of the PB.
        event_type (str): Type of event.
        event_data (dict, optional): Event data.

    """
    events.publish(AGGREGATE_TYPE, pb_id, event_type, event_data)


def cancel(pb_id: str):
    """Cancel a PB.

    Args:
        pb_id (str): the PB Id

    """
    # TODO(BM) Check that the key exists!

    pb_type = get_type(pb_id)
    publish(pb_id, 'cancelled')
    DB.lrem('{}:active'.format(AGGREGATE_TYPE), 0, pb_id)
    DB.lrem('{}:active:{}'.format(AGGREGATE_TYPE, pb_type), 0, pb_id)
    DB.rpush('{}:cancelled'.format(AGGREGATE_TYPE), pb_id)
    DB.rpush('{}:cancelled:{}'.format(AGGREGATE_TYPE, pb_type), pb_id)


def get_type(pb_id: str) -> str:
    """Get the PB type.

    Args:
        pb_id (str): PB Id

    Returns:
        str, The type (offline, realtime) of the PB

    """
    return DB.hget(get_key(pb_id), 'type')


def get_active() -> List[str]:
    """Get the list of active PBs from the database.

    Returns:
        list, PB ids.

    """
    return DB.lrange('{}:active'.format(AGGREGATE_TYPE), 0, -1)


def get_cancelled() -> List[str]:
    """Return the list of ids of cancelled PBs.

    Returns:
        list, PB ids

    """
    return DB.lrange('{}:cancelled'.format(AGGREGATE_TYPE), 0, -1)


def get_completed():
    """."""
    """Get the list of completed PBs from the database.

    Returns:
        list, PB ids.

    """
    return DB.lrange('{}:completed'.format(AGGREGATE_TYPE), 0, -1)


def get_events(pb_id: str) -> List[events.Event]:
    """Get event data for the specified PB.

    Args:
        pb_id (str): PB Id.

    Returns:
        list of event data dictionaries

    """
    event_data_key = get_event_data_key(pb_id)
    event_list = []
    for event_id, data in DB.hgetall(event_data_key).items():
        data = ast.literal_eval(data)
        event_list.append(events.Event(event_id, AGGREGATE_TYPE, '', data))
    return event_list


def get_config(pb_id: str) -> dict:
    """Get the data structure for a PB.

    Args:
        pb_id (str): PB id

    Returns:
        dict,

    """
    data = DB.hgetall(get_key(pb_id))
    # Attempt to convert data fields to python types.
    for key, value in data.items():
        try:
            data[key] = ast.literal_eval(value)
        except SyntaxError:
            pass
        except ValueError:
            pass
    return data


def get_status(pb_id: str) -> str:
    """Get the status of a PB.

    Args:
        pb_id (str): PB id

    Returns:
        str

    """
    # FIXME(BM) check the pb key exists.
    # FIXME(BM) use the events API for this?
    key = get_event_list_key(pb_id)
    last_event = DB.hget(get_event_data_key(pb_id), DB.lindex(key, -1))
    last_event = ast.literal_eval(last_event)
    return last_event['type']
