# coding=utf-8
"""Redis Configuration Database Events API.

This API is intended to support basic use of the
[Event Sourcing pattern](https://martinfowler.com/eaaDev/EventSourcing.html)
for SIP Execution Control services.

The implementation here is inspired by the description found at:
<https://medium.com/lcom-techblog/scalable-microservices-with-event-sourcing-and-redis-6aa245574db0>

Usage description:

1. An event subscriber registers itself to a subscribers list.
2. When an event is published, event data is written to a published
   list for list for each subscriber and a redis event is published
   in an atomic operation. The event itself does not contain any data
   it simply notifies subscribers that there is event data waiting.
   If a subscriber goes down, data will continue to be written to its published
   list and can be picked up when it comes back up.
3. When a subscriber receives an event notification, it pops the event from
   the 'published' list and pushes it to another 'acknowledged' list using
   the rpoplpush command. This makes it possible to have multiple instances
   of a subscriber running and while all instances will receive the event
   notification, only one of them will pick up the event data and process it.
4. Once processing of the event data is complete, it is removed from the
   acknowledged list by calling the event complete method. If an error is
   encountered during processing of the event, the data remains in the
   processing list and processing can be retried at a later time.

"""
import logging
import os
from uuid import uuid4
import json

import redis

LOG = logging.getLogger('sip.ec.db')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_DB_ID = os.getenv('REDIS_DB_ID', '0')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
DB = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB_ID,
                       decode_responses=True)


def published_key(event_type, subscriber):
    """."""
    return 'events/{}_{}_published'.format(event_type, subscriber)


def acknowledged_key(event_type: str, subscriber: str) -> str:
    """Key for event data that has been picked up by a subscriber.

    When a published event has been acknowledged, accepted, or picked up
    by a subscriber of the event type for handling the event data is moved
    to this key.

    Args:
        event_type (str): Event type string, ie name of the event.
        subscriber (str): Subscriber name or type (eg. service name subscribing)

    Returns:
        str, the key where acknowledged events are stored for the given
        event type and subscriber.

    """
    return 'events/{}_{}_acknowledged'.format(event_type, subscriber)


def subscribers_key(event_type):
    """."""
    return 'events/{}_subscribers'.format(event_type)


class Event:
    """."""
    pass


class Event:
    """."""
    # FIXME(BM) may not need event type if using a hash
    # This is mainly used to be able to complete events.

    def __init__(self, data, event_type, subscriber, id=None):
        """."""
        if id:
            self._id = id
        else:
            self._id = str(uuid4())
        self._event_type = event_type
        self._subscriber = subscriber
        self.data = data

    def __str__(self):
        """."""
        return json.dumps(self.__dict__)

    def complete(self):
        """."""
        # TODO(BM): Move this to event history rather than destroy it.
        return DB.lrem(acknowledged_key(self._event_type, self._subscriber),
                       0, self)


def event_from_json(json_string):
    """."""
    data = json.loads(json_string)
    data['id'] = data['_id']
    data['subscriber'] = data['_subscriber']
    data['event_type'] = data['_event_type']
    del data['_id']
    del data['_subscriber']
    del data['_event_type']
    return Event(**data)


class EventQueue:
    """Event Queue object"""

    def __init__(self, event_type, subscriber):
        """."""
        self._queue = DB.pubsub()
        self._queue.subscribe(event_type)
        self._published_key = published_key(event_type, subscriber)
        self._acknoledged_key = acknowledged_key(event_type, subscriber)

    def _get_event(self):
        """."""
        _json = DB.rpoplpush(src=self._published_key,
                             dst=self._acknoledged_key)
        if _json:
            return event_from_json(_json)
        return None

    def get(self):
        """."""
        message = self._queue.get_message()
        if message and message['data'] == 'new':
            LOG.debug('New event!')
            print('new event!')
            return self._get_event()
        return None

    def get_published(self):
        """."""
        # Intended for recovery -- needs thought
        published = []
        pipeline = DB.pipeline()
        while True:
            _event = pipeline.rpoplpush(self._published_key,
                                        self._acknoledged_key)
            if _event is None:
                break
            published.append(event_from_json(_event))
        pipeline.execute()
        return published

    def get_processing(self):
        """."""
        # Intended for recovery -- needs thought
        processing = DB.lrange(self._acknoledged_key, 0, -1)
        for i in range(len(processing)):
            processing[i] = event_from_json(processing[i])
        return processing


def subscribe(event_type, subscriber):
    """Add subscriber to the subscribers list for the given event type.

    Args:
        event_type (str): Type of event
        subscriber (str): Name of the subscriber.
    """
    _key = subscribers_key(event_type)
    DB.lrem(_key, 0, subscriber)
    DB.lpush(_key, subscriber)
    return EventQueue(event_type, subscriber)


def get_subscribers(event_type):
    """Return the list of subscribers for the event type."""
    return DB.lrange(subscribers_key(event_type), 0, -1)


def unsubscribe(event_type, subscriber):
    """Add a subscriber to the subscribers list for the given event type."""
    DB.lrem(subscribers_key(event_type), 0, subscriber)


def publish(event_type, data):
    """Publish a Processing Block event as an atomic operation.

    - Event data is pushed to each subscribers event data list
    - A notification of a new event is published to all subscribers.
    - If there is more than one instance of a subscriber, only one
      can pick up the data as it is pushed to a 2nd queue atomically.

    Args:
        event_type (str): Event type
        data (object): Event data

    """
    subscribers = get_subscribers(event_type)
    pipeline = DB.pipeline()
    for subscriber in subscribers:
        pipeline.rpush(published_key(event_type, subscriber),
                       Event(data, event_type, subscriber))
    pipeline.publish(event_type, 'new')
    pipeline.execute()

