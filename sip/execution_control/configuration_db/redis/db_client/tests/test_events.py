# coding=utf-8
"""Test of events interface."""
import time
from threading import Thread

from .. import events


def test_events():
    """Misc tests of the events interface."""
    # events.DB.flushall()
    events.db.flush_db()
    aggregate_type = 'test'
    subscriber = 'test_subscriber'
    event_type = 'test_event'
    aggregate_key = 'test:01'

    # Subscribe to the 'pb' aggregate events with the 'test' subscriber
    event_queue = events.subscribe(aggregate_type, subscriber)
    assert subscriber in events.get_subscribers(aggregate_type)

    # Publish an event.
    events.publish(aggregate_type, aggregate_key,
                   event_type=event_type, event_data={})

    # Keep asking for events until we get one.
    while True:
        event = event_queue.get()
        if event:
            assert event.id == '{}_event_00000000'.format(aggregate_type)
            assert event.aggregate_type == aggregate_type
            assert event.subscriber == subscriber
            assert 'type' in event.data
            assert event.data['type'] == event_type
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


def test_events_recovery():
    """Test event recovery, eg. after a subscriber service crash."""
    # events.DB.flushall()
    events.db.flush_db()
    aggregate_type = 'test'
    subscriber = 'test_subscriber'
    event_type = 'test_event'
    aggregate_key = 'test:02'

    # Start a subscriber that goes away. eg it crashes, or in this case is a
    # temp thread that finishes after subscribing.
    temp_subscriber = Thread(target=events.subscribe,
                             args=[aggregate_type, subscriber])
    temp_subscriber.start()
    temp_subscriber.join()

    # While the subscriber is not getting events (it is a temp thread
    # that has finished), some events are published.
    events.publish(aggregate_type, aggregate_key, event_type,
                   event_data={'counter': 1})
    events.publish(aggregate_type, aggregate_key, event_type,
                   event_data={'counter': 2})

    # When the subscriber comes back, it will resubscribe but calling
    # get on the event queue will not return any events as event notifications
    # were missed.
    event_queue = events.subscribe(aggregate_type, subscriber)
    event_count = 0
    for _ in range(100):
        event = event_queue.get()
        if event:
            event_count += 1
    assert event_count == 0

    # At this point, since we cleared the db for the test, there are no
    # active (previously acknowledged) events
    active_events = event_queue.get_active_events()
    assert not active_events

    # But there are two published events to get form the subscriber queue.
    published_events = event_queue.get_published_events()
    assert len(published_events) == 2

    # After asking for published events they are moved to the active queue.
    active_events = event_queue.get_active_events()
    assert len(active_events) == 2

    # And there are no longer any published events.
    published_events = event_queue.get_published_events()
    assert not published_events

    # If we complete the active events.
    for event in active_events:
        event.complete()

    # They are moved to the history queue and are no longer active.
    active_events = event_queue.get_active_events()
    assert not active_events
