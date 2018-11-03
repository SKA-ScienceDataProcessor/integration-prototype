# coding=utf-8
"""Module of functions defining db keys used for events.

This separates the structure of the database for storing events from
the event handling logic.
"""


def event_counter(aggregate_type: str) -> str:
    """Return db key for the event counter for the aggregate type.

    The value stored at this key is used to generate a unique event id.

    Args:
        aggregate_type (str): Type of aggregate.

    Returns:
        str, database key for the event counter

    """
    return 'events:{}:count'.format(aggregate_type)


def subscribers(aggregate_type: str) -> str:
    """."""
    return 'events:{}:subscribers'.format(aggregate_type)


def published(aggregate_type: str, subscriber: str) -> str:
    """Return db key for subscriber published event ids.

    Args:
        aggregate_type (str): Type of aggregate.
        subscriber (str): Name of the subscriber.

    Returns:
        str, database key for the published event ids

    """
    return 'events:{}:{}:published'.format(aggregate_type, subscriber)


def data(aggregate_type: str, subscriber: str) -> str:
    """Return the db key for subscriber event data.

    Args:
         aggregate_type (str): Type of aggregate
         subscriber (str): Name of the subscriber

    Returns:
        str, database key for the event data

    """
    return 'events:{}:{}:data'.format(aggregate_type, subscriber)


def processed(aggregate_type: str, subscriber: str) -> str:
    """Return the db key used to store processed events.

    This is the key where processed events for the specified subscriber and
    aggregate type are stored.

    Args:
        aggregate_type (str): Type of aggregate
        subscriber (str): Subscriber name

    Returns:
        str, db key where processed events are stored.

    """
    return 'events:{}:{}:processed'.format(aggregate_type, subscriber)


def history(aggregate_type: str, subscriber: str) -> str:
    """."""
    return 'events:{}:{}:history'.format(aggregate_type, subscriber)


def aggregate_events_list(aggregate_key: str) -> str:
    """."""
    return '{}:events_list'.format(aggregate_key)


def aggregate_events_data(aggregate_key: str) -> str:
    """."""
    return '{}:events_data'.format(aggregate_key)
