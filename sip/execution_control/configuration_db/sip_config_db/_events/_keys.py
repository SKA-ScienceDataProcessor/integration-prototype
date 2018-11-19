# coding=utf-8
"""Module of functions defining db keys used for events.

This separates the structure of the database for storing events from
the event handling logic.
"""


def event_counter(object_type: str) -> str:
    """Return db key for the event counter for the object type.

    The value stored at this key is used to generate a unique event id.

    Args:
        object_type (str): Type of object.

    Returns:
        str, database key for the event counter

    """
    return 'events:{}:count'.format(object_type)


def subscribers(object_type: str) -> str:
    """Key for list of subscribers to specified object type."""
    return 'events:{}:subscribers'.format(object_type)


def published(object_type: str, subscriber: str) -> str:
    """Return db key for subscriber published event ids.

    Args:
        object_type (str): Type of object.
        subscriber (str): Name of the subscriber.

    Returns:
        str, database key for the published event ids

    """
    return 'events:{}:{}:published'.format(object_type, subscriber)


def data(object_type: str, subscriber: str) -> str:
    """Return the db key for subscriber event data.

    Args:
         object_type (str): Type of object
         subscriber (str): Name of the subscriber

    Returns:
        str, database key for the event data

    """
    return 'events:{}:{}:data'.format(object_type, subscriber)


def processed_events(object_type: str, subscriber: str) -> str:
    """Return the db key used to store processed events.

    This is the key where processed events for the specified subscriber and
    object type are stored.

    Args:
        object_type (str): Type of object
        subscriber (str): Subscriber name

    Returns:
        str, db key where processed events are stored.

    """
    return 'events:{}:{}:processed'.format(object_type, subscriber)


def completed_events(object_type: str, subscriber: str) -> str:
    """Return the db key used to store completed events.

    Args:
        object_type (str): Type of object
        subscriber (str): Subscriber name

    Returns:
        str, db key where completed events are stored.

    """
    return 'events:{}:{}:completed'.format(object_type, subscriber)


def events_list(object_key: str) -> str:
    """."""
    return '{}:events_list'.format(object_key)


def events_data(object_key: str) -> str:
    """."""
    return '{}:events_data'.format(object_key)
