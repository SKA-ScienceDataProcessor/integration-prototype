# coding=utf-8
"""Test of events interface."""
import time
import redis

from .. import events


def test_events():
    """."""
    print('')
    client = redis.StrictRedis(decode_responses=True)
    client.flushall()

    aggregate_type = 'test'

    # Subscribe to the 'pb' aggregate events with the 'test' subscriber
    event_queue = events.subscribe(aggregate_type, 'test')
    assert 'test' in events.get_subscribers(aggregate_type)

    # Publish an event.
    aggregate_key = 'pb:01'
    events.publish(aggregate_type, aggregate_key,
                   event_type='test_type', event_data={})

    # Keep asking for events until we get one.
    while True:
        event = event_queue.get()
        if event:
            assert event.id == '{}_event_00000000'.format(aggregate_type)
            assert event.aggregate_type == aggregate_type
            assert event.subscriber == 'test'
            assert 'type' in event.data
            assert event.data['type'] == 'test_type'
            assert '{}_id'.format(aggregate_type) in event.data
            assert event.data['{}_id'.format(aggregate_type)] == aggregate_key
            break
        time.sleep(0.01)

    # There should be no published events as we already got the
    # only event.
    assert not event_queue.get_published_events()

    # There should be one active event.
    active_events = event_queue.get_active_events()
    assert len(active_events) == 1
    assert active_events[0].id == '{}_event_00000000'.format(aggregate_type)

    # Completing the active event should move it to history.
    event.complete()
    active_events = event_queue.get_active_events()
    assert not active_events
