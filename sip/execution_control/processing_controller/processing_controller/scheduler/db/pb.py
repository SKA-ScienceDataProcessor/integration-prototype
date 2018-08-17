# coding=utf-8
"""Processing Block (PB) data and events."""
from typing import List

import redis
import ast

from . import events
from .event_keys import aggregate_events_data, aggregate_events_list

DB = redis.StrictRedis(decode_responses=True)
AGGREGATE_TYPE = 'pb'


def get_pb_key(pb_id: str) -> str:
    """Return a Processing Block db key.

    Args:
        pb_id (str): Processing Block instance id

    Returns:
        str, db key for the specified PB

    """
    return '{}:{}'.format(AGGREGATE_TYPE, pb_id)


def get_pb_event_data_key(pb_id: str) -> str:
    """Return the PB events data db key.

    Args:
        pb_id (str): PB id.

    Returns:
        str, db key for the specified PB event data.

    """
    return aggregate_events_data(get_pb_key(pb_id))


def get_pb_event_list_key(pb_id: str) -> str:
    """Return the PB events list db key.

    Args:
        pb_id (str): PB id.

    Returns:
        str, db key for the specified PB event data.

    """
    return aggregate_events_list(get_pb_key(pb_id))


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


def get_type(pb_id: str) -> str:
    """Get the PB type.

    Args:
        pb_id (str): PB Id

    Returns:
        str, The type (offline, realtime) of the PB

    """
    return DB.hget(get_pb_key(pb_id), 'type')


def get_cancelled() -> List[str]:
    """Return the list of ids of cancelled PBs

    Returns:
        list, PB ids

    """
    return DB.lrange('pb:cancelled', 0, -1)


def get_events(pb_id: str) -> List[events.Event]:
    """Get event data for the specified PB.

    Args:
        pb_id (str): PB Id.

    Returns:
        list of event data dictionaries

    """
    event_data_key = get_pb_event_data_key(pb_id)
    event_list = []
    for event_id, data in DB.hgetall(event_data_key).items():
        data = ast.literal_eval(data)
        event_list.append(events.Event(event_id, AGGREGATE_TYPE, '', data))
    return event_list

