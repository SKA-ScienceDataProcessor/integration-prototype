# coding=utf-8
"""Tests of the Configuration Database Events API."""
from threading import Thread
import json

from .. import processing_block_events as events


def test_event_from_json():
    """Test Creating and event object from JSON"""
    event = events.events.event_from_json(
        json.dumps(dict(_id='123', _event_type='type',
                        _subscriber='sub1', data={'a': 2})))
    assert event.data == {'a': 2}


def test_subscribe():
    """."""
    events.events.DB.flushall()
    q1 = events.subscribe('scheduler')
    q2 = events.subscribe('scheduler')
    q3 = events.subscribe('interface')
    assert 'scheduler' in events.get_subscribers()
    assert 'interface' in events.get_subscribers()

    events.publish({'type': 'foo1'})
    events.publish({'type': 'foo2'})

    print('')
    print('---- q1 ----')
    q1_events = []
    for _ in range(10):
        _event = q1.get()
        if _event:
            q1_events.append(_event)
            print(type(_event), _event.data)

    for _event in q1_events:
        print(type(_event))
        _event.complete()

    print('---- q2 ----')
    for _ in range(10):
        print(q2.get())

    print('---- q3 ----')
    for _ in range(10):
        print(q3.get())


def test_get_after_crash():
    """."""
    events.events.DB.flushall()

    # Start a subscriber that goes away (eg crashes after subscribing)
    temp_subscriber = Thread(target=events.subscribe, args=['temp_subscriber'])
    temp_subscriber.start()
    temp_subscriber.join()

    # While it is not active, some events are published...
    events.publish({'type': 'test1'})
    events.publish({'type': 'test2'})

    # When the subscriber comes back it will resubscribe but calling get
    # on the event queue will not return events published while it was down.
    q1 = events.subscribe('temp_subscriber')
    print('')
    for i in range(10):
        print(i, q1.get())

    # To get uncompleted processing events
    processing = q1.get_processing()
    print('PROCESSING1', processing)

    # To get unhandled historical published events
    published = q1.get_published()
    print('PUBLISHED1', published)

    # Historical published events now moved to publishing
    processing = q1.get_processing()
    print('PROCESSING2', processing)

    # To get unhandled historical published events
    published = q1.get_published()
    print('PUBLISHED2', published)

    # Complete the processing events.
    for event in processing:
        event.complete()

    # Historical published events now moved to publishing
    processing = q1.get_processing()
    print('PROCESSING3', processing)

    # To get unhandled historical published events
    published = q1.get_published()
    print('PUBLISHED3', published)



