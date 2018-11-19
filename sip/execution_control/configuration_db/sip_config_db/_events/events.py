# coding=utf-8
"""Execution Control Configuration database events module."""
from ast import literal_eval
from typing import Callable, List
from copy import deepcopy

from . import EventQueue, _keys, Event
from .. import DB


def subscribe(object_type: str, subscriber: str,
              callback_handler: Callable = None) -> EventQueue:
    """Subscribe to the specified object type.

    Returns an EventQueue object which can be used to query events
    associated with the object type for this subscriber.

    Args:
        object_type (str): Object type
        subscriber (str): Subscriber name
        callback_handler (function, optional): Callback handler function.

    Returns:
        EventQueue, event queue object.

    """
    key = _keys.subscribers(object_type)
    DB.remove_from_list(key, subscriber)
    DB.append_to_list(key, subscriber)
    return EventQueue(object_type, subscriber, callback_handler)


def get_subscribers(object_type: str) -> List[str]:
    """Get the list of subscribers to events of the object type.

    Args:
        object_type (str): Type of object.

    Returns:
        List[str], list of subscriber names.

    """
    return DB.get_list(_keys.subscribers(object_type))


def publish(event_type: str,
            event_data: dict = None,
            object_type: str = None,
            object_id: str = None,
            object_key: str = None,
            origin: str = None):
    """Publish an event.

    Published the event to all subscribers and stores the event with the
    object.

    Args:
        event_type (str): The event type
        event_data (dict, optional): Optional event data
        object_type (str): Type of object.
        object_id (str): Object ID
        object_key (str, optional): Key used to stored the object. If None,
            the default assume the key is of the form <object type>:<object id>
        origin (str): Origin or publisher of the event.

    """
    event = Event(event_id=_get_event_id(object_type),
                  event_type=event_type,
                  event_data=event_data,
                  event_origin=origin,
                  object_type=object_type,
                  object_id=object_id,
                  object_key=object_key)

    # Publish the event to subscribers
    _publish_to_subscribers(event)

    # Update the object event list and data.
    if object_key is None:
        object_key = '{}:{}'.format(object_type, object_id)
    _update_object(object_key, event)

    # Execute the set of db transactions as an atomic transaction.
    DB.execute()


def _get_events_list(object_key: str) -> List[str]:
    """Get list of event ids for the object with the specified key.

    Args:
        object_key (str): Key of an object in the database.

    """
    return DB.get_list(_keys.events_list(object_key))


def _get_events_data(object_key: str) -> List[dict]:
    """Get the list of event data for the object with the specified key.

    Args:
        object_key (str): Key of an object in the database.

    """
    events_data = []
    key = _keys.events_data(object_key)
    for event_id in _get_events_list(object_key):
        event_dict = literal_eval(DB.get_hash_value(key, event_id))
        events_data.append(event_dict)
    return events_data


def get_events(object_key: str) -> List[Event]:
    """Get list of events for the object with the specified key."""
    events_data = _get_events_data(object_key)
    return [Event.from_config(event_dict) for event_dict in events_data]


def _publish_to_subscribers(event: Event):
    """Publish and event to all subscribers.

    - Adds the event id to the published event list for all subscribers.
    - Adds the event data to the published event data for all subscribers.
    - Publishes the event id notification to all subscribers.

    Args:
        event (Event): Event object to publish.

    """
    subscribers = get_subscribers(event.object_type)

    # Add the event to each subscribers published list
    for sub in subscribers:
        DB.prepend_to_list(_keys.published(event.object_type, sub),
                           event.id, pipeline=True)
        event_dict = deepcopy(event.config)
        event_dict.pop('id')
        DB.set_hash_value(_keys.data(event.object_type, sub), event.id,
                          str(event_dict), pipeline=True)
    DB.publish(event.object_type, event.id, pipeline=True)


def _update_object(object_key: str, event: Event):
    """Update the events list and events data for the object.

    - Adds the event Id to the list of events for the object.
    - Adds the event data to the hash of object event data keyed by event
      id.

    Args:
        object_key (str): Key of the object being updated.
        event (Event): Event object


    """
    events_list_key = _keys.events_list(object_key)
    events_data_key = _keys.events_data(object_key)
    event_dict = deepcopy(event.config)
    event_dict.pop('id')
    DB.append_to_list(events_list_key, event.id, pipeline=True)
    DB.set_hash_value(events_data_key, event.id, event_dict, pipeline=True)


def _get_event_id(object_type: str) -> str:
    """Return an event key for the event on the object type.

    This must be a unique event id for the object.

    Args:
        object_type (str): Type of object

    Returns:
        str, event id

    """
    key = _keys.event_counter(object_type)
    DB.watch(key, pipeline=True)
    count = DB.get_value(key)
    DB.increment(key)
    DB.execute()
    if count is None:
        count = 0
    return '{}_event_{:08d}'.format(object_type, int(count))
